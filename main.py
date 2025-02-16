from typing import List
from models import DebatePrompts, DebateTopic, DebateTotal
from run_debate import run_debate
from pathlib import Path
import json
from debate_prompts import get_debate_prompt
from load_topics import get_all_topics
from dotenv import load_dotenv
import logging

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

NUM_DEBATER_MODELS: int = 5

def load_models_pricing(file_path: str) -> dict[str, List[float]]:
    logging.info(f"Loading pricing from {file_path}")
    with open(file_path, 'r') as f:
        pricing = json.load(f)
    logging.info(f"Loaded {len(pricing)} models from {file_path}")
    return pricing

def get_judge_models(file_path:str) -> List[str]:
    logging.info(f"loading judge models from {file_path}")
    with open(file_path, 'r') as f:
        judge_pricing = json.load(f)

    return list(judge_pricing.keys())

def get_debate_combinations(models_pricing: dict[str, float]) -> List[tuple[str, str]]:
    """Returns list of (proposition_model, opposition_model) pairs for debates"""
    models_list = list(models_pricing.keys())
    # Ensuring we have exactly 5 models
    assert len(models_list) == 5, f"Expected 5 models but got {len(models_list)}"

    # A, B, C, D, E mapping to actual model names
    A, B, C, D, E = models_list

    # Our balanced 8 debates from earlier
    debates = [
        (A, B),  # A prop vs B opp
        (B, C),  # B prop vs C opp
        (C, D),  # C prop vs D opp
        (D, E),  # D prop vs E opp
        (E, A),  # E prop vs A opp
        (C, A),  # C prop vs A opp
        (D, B),  # D prop vs B opp
        (E, C),  # E prop vs C opp
    ]

    return debates

def run_all_debates(
    debates: List[tuple[str, str]],
    topic_list: List[DebateTopic],
    debate_prompt: DebatePrompts,
    base_path: Path,
    judge_models: List[str]
) -> List[DebateTotal]:
    """Runs all debates with given combinations"""
    results = []
    for i, (prop_model, opp_model) in enumerate(debates):
        # Use topic_list[i % len(topic_list)] to cycle through topics if needed
        topic = topic_list[i % len(topic_list)]
        safe_prop_name = prop_model.replace('/', '_')
        safe_opp_name = opp_model.replace('/', '_')
        debate_path = base_path / f"{safe_prop_name}_{safe_opp_name}.json"
        if debate_path.exists():
            logging.info(f"{debate_path} already exists. SKIPPING")
            continue



        logging.info(f"Running debate {i+1}/8: {prop_model} (prop) vs {opp_model} (opp)")
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
    # Create output directory with timestamp

    # Setup logging
    setup_logging()

    # Get prompts and topic
    logging.info("Loading debate prompts and topic")
    topic_list = get_all_topics()
    debate_prompt = get_debate_prompt()
    models_pricing = load_models_pricing('api_pricing.json')
    assert len(models_pricing.keys()) == NUM_DEBATER_MODELS, f"Expected {NUM_DEBATER_MODELS} but got {len(models_pricing.keys())}"

    debates = get_debate_combinations(models_pricing=models_pricing)
    output_path = Path("debate_test_judges")
    output_path.mkdir(exist_ok=True)



    judge_models = get_judge_models('judge_models.json')

    results = run_all_debates(
    debates=debates,
    topic_list=topic_list,
    debate_prompt=debate_prompt,
    base_path=output_path,
    judge_models=judge_models  # You'll need to define this list
    )

    print(results)







if __name__ == "__main__":
    load_dotenv()
    main()
