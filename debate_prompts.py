from models import DebatePrompts
import yaml


# Create the DebatePrompts object


def get_debate_prompt() -> DebatePrompts:
    with open("debate_prompts.yaml", "r") as file:
        prompts = yaml.safe_load(file)

    debator_prompts = DebatePrompts(
        first_speech_prompt=prompts["first_speech"],
        rebuttal_speech_prompt=prompts["rebuttal_speech"],
        final_speech_prompt=prompts["final_speech"],
        judge_prompt=prompts["judging_prompt"]
    )

    return debator_prompts

if __name__ == "__main__":
    print(get_debate_prompt())
