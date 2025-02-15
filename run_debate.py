import os
from pathlib import Path
import re

import requests
from models import (
    DebateTotal,
    DebatorOutputs,
    DebatorPrompts,
    DebateTopic,
    JudgeResult,
    Round,
    Side,
    SpeechType,
)
from utils import make_rounds
from openai import OpenAI
from typing import List, Dict
from tenacity import retry, stop_after_attempt, wait_exponential

import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)



class DebateState:
    def __init__(self):
        self.proposition = DebatorOutputs(side=Side.PROPOSITION)
        self.opposition = DebatorOutputs(side=Side.OPPOSITION)

    def add_speech(self, side: Side, speech_type: SpeechType, speech: str):
        target = self.proposition if side == Side.PROPOSITION else self.opposition
        target.speeches[speech_type] = speech

    def get_context_for_next_speech(self, current_round: Round) -> List[Dict]:
        messages = []
        for speech_type in SpeechType:
            if speech_type == current_round.speech_type:
                break
            prop_speech = self.proposition.speeches[speech_type]
            opp_speech = self.opposition.speeches[speech_type]
            if prop_speech != -1:
                messages.append(
                    {
                        "role": "assistant"
                        if current_round.side == Side.OPPOSITION
                        else "user",
                        "content": prop_speech,
                    }
                )
            if opp_speech != -1:
                messages.append(
                    {
                        "role": "assistant"
                        if current_round.side == Side.PROPOSITION
                        else "user",
                        "content": opp_speech,
                    }
                )
        print("state for next speech is", messages)
        return messages


def extract_debate_result(xml_string: str, model: str) -> JudgeResult:
   try:
       # Find all winner matches
       winner_matches = re.findall(r'<winnerName>(\w+)</winnerName>', xml_string)
       if not winner_matches or len(winner_matches) != 1:
           raise ValueError("Must have exactly one winner")
       winner = winner_matches[0]
       if winner not in ["opposition", "proposition"]:
           raise ValueError("Winner must be opposition or proposition")

       # Find all confidence matches
       confidence_matches = re.findall(r'<confidence>(\d+)</confidence>', xml_string)
       if not confidence_matches or len(confidence_matches) != 1:
           raise ValueError("Must have exactly one confidence value")
       confidence = int(confidence_matches[0])
       if not 0 <= confidence <= 100:
           raise ValueError("Confidence must be between 0 and 100")

       return JudgeResult(
           model=model,
           winner=winner,
           confidence=confidence,
           logic=xml_string
       )

   except Exception as e:
       print(f"Error processing input: {str(e)}")
       print("\nCurrent XML:")
       print(xml_string)

       while True:
           try:
               winner = input("\nEnter winner (opposition/proposition): ").strip()
               if winner not in ["opposition", "proposition"]:
                   print("Invalid winner")
                   continue

               confidence_str = str(input("Enter confidence (0-100): ").strip())
               if not confidence_str.isdigit():
                   print("Confidence must be a number")
                   continue

               confidence = int(confidence)
               if not 0 <= confidence <= 100:
                   print("Confidence must be between 0 and 100")
                   continue

               return JudgeResult(
                   model=model,
                   winner=winner,
                   confidence=confidence,
                   logic=xml_string
               )
           except ValueError:
               print("Invalid input, please try again")

def get_judgement_string(debate: DebateTotal, prompts: DebatorPrompts, model: str) -> str:
    logger.info(f"Starting judge request to OpenRouter for model: {model}")

    headers = {
        "Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}",
        "Content-Type": "application/json",
    }

    messages = [
        {
            "role": "system",
            "content": f"You are a judge. Follow these rules {prompts.judge_prompt}"
        },
        {
            "role": "user",
            "content": f"the debate is {debate.get_transcript()}"
        }
    ]

    payload = {
        "model": model,
        "messages": messages
    }

    logger.debug(f"Judge request payload: {payload}")

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload
    )

    response_json = response.json()
    logger.info(f"Raw judge API response: {response_json}")

    if response.status_code != 200:
        error_msg = f"Judge API returned error: {response_json.get('error', {}).get('message')}"
        logger.error(error_msg)
        raise ValueError(error_msg)

    judgment = response_json["choices"][0]["message"]["content"]
    logger.info("Successfully retrieved judgment")
    logger.debug(f"Judgment content: {judgment}")

    return judgment


def get_judgement(debate: DebateTotal, prompts: DebatorPrompts, judge_model:str) -> JudgeResult:
    judgement_string = get_judgement_string(debate=debate, prompts=prompts, model=judge_model)
    return extract_debate_result(xml_string=judgement_string, model=judge_model)

def run_debate(
    proposition_model: str,
    opposition_model: str,
    motion: DebateTopic,
    prompts: DebatorPrompts,
    client: OpenAI,
    path: Path,
    judge_models: List[str]
) -> DebateTotal:
    state = DebateState()
    rounds = make_rounds()
    output = DebateTotal(
        motion=motion,
        proposition_model=proposition_model,
        opposition_model=opposition_model,
        prompts=prompts,
        path_to_store=path,
    )

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        before_sleep=lambda retry_state: logger.warning(
            f"Attempt {retry_state.attempt_number} failed. Retrying after backoff..."
        ),
    )
    def get_valid_response(messages, model):
        logger.info(f"Starting API request to OpenRouter for model: {model}")
        logger.debug(f"Request messages: {messages}")
        headers = {
        "Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}",
        "Content-Type": "application/json",
        }
        payload = {
        "model": model,  # OpenRouter requires full model path like "openai/gpt-4"
        "messages": messages
        }
        logger.debug(f"Request payload: {payload}")

        response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload
        )

        response_json = response.json()



        logger.info(f"Raw API response: {response_json}")
        if response.status_code != 200:
            error_msg = f"API returned error: {response_json.get('error', {}).get('message')}"
            logger.error(error_msg)
            raise ValueError(error_msg)


        # Get token usage for any API response
        usage = response_json.get("usage", {})
        completion_tokens = usage.get("completion_tokens", 0)
        prompt_tokens = usage.get("prompt_tokens", 0)
        total_tokens = usage.get("total_tokens", 0)

        logger.info(f"Token usage - Completion: {completion_tokens}, Prompt: {prompt_tokens}, Total: {total_tokens}")


        try:
            if not response_json.get("choices"):
                error_msg = "API response contains empty choices list"
                logger.error(error_msg)
                raise ValueError(error_msg)

            speech = response_json["choices"][0]["message"]["content"]

            if not speech:
                error_msg = "API returned empty speech content"
                logger.error(error_msg)
                raise ValueError(error_msg)

            logger.info("Successfully retrieved speech content")
            logger.info(f"Speech content: {speech}")

            # Track successful token usage
            output.token_counts.add_successful_call(
                model=model,
                completion_tokens=completion_tokens,
                prompt_tokens=prompt_tokens,
                total_tokens=total_tokens,
            )

            logger.info("Successfully tracked token usage")


            return speech

        except Exception as e:
            # Track failed token usage
            logger.error(f"Error processing API response: {str(e)}")

            output.token_counts.add_failed_call(
                model=model,
                completion_tokens=completion_tokens,
                prompt_tokens=prompt_tokens,
                total_tokens=total_tokens,
            )
            raise

    for round in rounds:
        model = (
            proposition_model if round.side == Side.PROPOSITION else opposition_model
        )
        context = state.get_context_for_next_speech(round)

        logger.info(f"Starting {round.side} {round.speech_type} speech")
        logger.debug(f"Context for speech: {context}")

        prompt = {
            SpeechType.OPENING: prompts.first_speech_prompt,
            SpeechType.REBUTTAL: prompts.rebuttal_speech_prompt,
            SpeechType.CLOSING: prompts.final_speech_prompt,
        }[round.speech_type]

        messages = [
            {
                "role": "system",
                "content": f"You are debating {motion.topic_description}. You are on the {round.side.value} side. {prompt}",
            },
            *context,
        ]

        try:
            speech = get_valid_response(messages, model)

            logger.info(f"Successfully got speech for {round.side} {round.speech_type}")
            logger.debug(f"Speech content: {speech}")

            state.add_speech(round.side, round.speech_type, speech)

            if round.side == Side.PROPOSITION:
                output.proposition_output.speeches[round.speech_type] = speech
            else:
                output.opposition_output.speeches[round.speech_type] = speech

        except Exception as e:
            logger.error(f"Error during debate round: {e}", exc_info=True)
            raise

        output.save_to_json()

    output.judge_results =  []
    for model in judge_models:
        output.judge_results.append(get_judgement(debate=output, prompts=prompts, judge_model=model))

        output.save_to_json()

    return output
