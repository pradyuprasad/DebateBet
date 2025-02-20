from typing import List
from models import DebatePrompts, DebateTopic, DebateTotal
from run_debate import run_debate
from pathlib import Path
import json
from debate_prompts import get_debate_prompt
from load_topics import get_all_topics
from dotenv import load_dotenv
import itertools
import logging
import random

def setup_logging():
   logging.basicConfig(
       level=logging.INFO,
       format='%(asctime)s - %(levelname)s - %(message)s'
   )

def get_judge_models(file_path:str) -> List[str]:
    logging.info(f"loading judge models from {file_path}")
    with open(file_path, 'r') as f:
        judge_pricing = json.load(f)

    return list(judge_pricing.keys())

NUM_DEBATER_MODELS: int = 5

def load_models_pricing(file_path: str) -> dict[str, List[float]]:
   logging.info(f"Loading pricing from {file_path}")
   with open(file_path, 'r') as f:
       pricing = json.load(f)
   logging.info(f"Loaded {len(pricing)} models from {file_path}")
   return pricing

def get_debate_pairs(models_list: List[str], topic_list: List[DebateTopic]) -> List[tuple[str, str, DebateTopic]]:
    """Returns list of (prop_model, opp_model, topic) pairs for debates"""
    pairs = []
    all_pairs = list(itertools.combinations(models_list, 2))

    for model_a, model_b in all_pairs:
        random_topic = random.choice(topic_list)
        # Add both A vs B and B vs A for each topic
        pairs.append((model_a, model_b, random_topic))  # Pass the whole DebateTopic object
        pairs.append((model_b, model_a, random_topic))

    logging.info(f"Generated {len(pairs)} debate pairs")
    return pairs

def run_all_debates(
   debate_pairs: List[tuple[str, str, DebateTopic]],
   debate_prompt: DebatePrompts,
   base_path: Path,
   judge_models: List[str]
) -> List[DebateTotal]:
   """Runs all debates with given combinations"""
   results = []
   for prop_model, opp_model, topic in debate_pairs:
       safe_prop_name = prop_model.replace('/', '_')
       safe_opp_name = opp_model.replace('/', '_')
       debate_path = base_path / f"{safe_prop_name}_{safe_opp_name}.json"

       if debate_path.exists():
           logging.info(f"Skipping existing debate: {safe_prop_name} vs {safe_opp_name}")
           continue

       logging.info(f"Running debate: {prop_model} (prop) vs {opp_model} (opp) on topic {topic}")
       result = run_debate(
           proposition_model=prop_model,
           opposition_model=opp_model,
           motion=topic,
           prompts=debate_prompt,
           path=debate_path,
           judge_models=judge_models
       )
       results.append(result)

   return results

def main():
   setup_logging()

   logging.info("Loading debate prompts and topics")
   debate_prompt = get_debate_prompt()
   topic_list = get_all_topics()

   models_pricing = load_models_pricing("api_pricing.json")
   assert len(models_pricing.keys()) == NUM_DEBATER_MODELS, f"Expected {NUM_DEBATER_MODELS} models but got {len(models_pricing.keys())}"
   models_list = list(models_pricing.keys())

   output_path = Path("stage_one")
   output_path.mkdir(exist_ok=True)

   judge_models = get_judge_models("judge_models.json")

   debate_pairs = get_debate_pairs(models_list, topic_list)
   results = run_all_debates(
       debate_pairs=debate_pairs,
       debate_prompt=debate_prompt,
       base_path=output_path,
       judge_models=judge_models  # You'll need to define this list
   )

if __name__ == "__main__":
   load_dotenv()
   main()
