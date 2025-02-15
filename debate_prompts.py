from models import DebatorPrompts
import yaml


# Create the DebatorPrompts object


def get_debator_prompts() -> DebatorPrompts:
    with open("debate_prompts.yaml", "r") as file:
        prompts = yaml.safe_load(file)

    debator_prompts = DebatorPrompts(
        first_speech_prompt=prompts["first_speech"],
        rebuttal_speech_prompt=prompts["rebuttal_speech"],
        final_speech_prompt=prompts["final_speech"],
        judge_prompt=prompts["judging_prompt"]
    )

    return debator_prompts

if __name__ == "__main__":
    print(get_debator_prompts())
