from models import DebateTotal
import glob
import os
from run_debate import get_judgement
from debate_prompts import get_debate_prompt
from dotenv import load_dotenv

load_dotenv()


folder_to_search = "debate_test_judges"

def analyse_judges(debate_total: DebateTotal) -> None:
    num_judges = len(debate_total.judge_token_counts.model_usages.keys())
    print(f"The number of judges is {num_judges} for motion {debate_total.motion.topic_description}")
    for judgement in debate_total.judge_results:
        print("model is", judgement.model)
        print("winner is", judgement.winner)
        print("confidence is", judgement.confidence)



json_files = glob.glob(os.path.join(folder_to_search, "*.json"))

for file in json_files:
    debate_total = DebateTotal.load_from_json(file)
    analyse_judges(debate_total)


