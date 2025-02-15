import json
from typing import Dict, List, Tuple
from dataclasses import dataclass
from config import Config


@dataclass
class DebateConfig:
    system_prompt_words: int = 300
    first_speech_words: int = 500
    rebuttal_words: int = 400
    scratchpad_words: int = 300
    final_speech_words: int = 500
    words_to_tokens_multiplier: float = 1.35
    judge_output_words: int = 2000
    num_trials: int = 2


def count_debate_tokens(config: DebateConfig) -> Tuple[float, float]:
    input_history = config.system_prompt_words

    stages = [
        (config.first_speech_words, config.scratchpad_words),
        (config.rebuttal_words, config.scratchpad_words),
        (config.final_speech_words, config.scratchpad_words),
    ]

    total_input = 0
    total_output = 0

    for speech_words, scratchpad_words in stages:
        stage_output = speech_words + scratchpad_words
        total_input += input_history
        total_output += stage_output
        input_history += stage_output + speech_words

    return (
        total_input * config.words_to_tokens_multiplier,
        total_output * config.words_to_tokens_multiplier,
    )


def calculate_cost(
    input_tokens: float, output_tokens: float, input_price: float, output_price: float
) -> float:
    return (input_tokens * input_price + output_tokens * output_price) / 10**6


def load_model_pricing(
    config: Config,
) -> Tuple[Dict[str, List[float]], Dict[str, List[float]]]:
    with open(config.api_pricing_path, "r") as f:
        debater_pricing = json.load(f)
    with open(config.judge_pricing_path, "r") as f:
        judge_pricing = json.load(f)
    return debater_pricing, judge_pricing


def calculate_experiment_count(num_models: int) -> int:
    debates_per_model = (num_models - 1) * 2  # Each model debates others twice
    return num_models * debates_per_model


def estimate_judging_cost(config: Config, debate_config: DebateConfig) -> float:
    _, single_debate_output = count_debate_tokens(debate_config)
    judge_input_tokens = single_debate_output * 2
    judge_output_tokens = (
        debate_config.judge_output_words * debate_config.words_to_tokens_multiplier
    )

    _, judge_pricing = load_model_pricing(config)

    # Calculate cost per judge
    judge_costs = {
        model: calculate_cost(
            judge_input_tokens, judge_output_tokens, prices[0], prices[1]
        )
        for model, prices in judge_pricing.items()
    }

    total_judge_cost = sum(judge_costs.values())
    debater_pricing, _ = load_model_pricing(config)
    total_experiments = (
        calculate_experiment_count(len(debater_pricing)) * debate_config.num_trials
    )

    return total_judge_cost * total_experiments


def estimate_debater_cost(config: Config, debate_config: DebateConfig) -> float:
    input_tokens, output_tokens = count_debate_tokens(debate_config)
    debater_pricing, _ = load_model_pricing(config)

    # Calculate cost per debater
    debater_costs = {
        model: calculate_cost(input_tokens, output_tokens, prices[0], prices[1])
        for model, prices in debater_pricing.items()
    }

    num_models = len(debater_pricing)
    experiments_per_model = (num_models - 1) * 2
    total_cost = (
        sum(debater_costs.values()) * experiments_per_model * debate_config.num_trials
    )

    return total_cost


def print_detailed_experiment_report(
    config: Config, debate_config: DebateConfig
) -> None:
    debater_pricing, judge_pricing = load_model_pricing(config)

    # Calculate basic stats
    num_debater_models = len(debater_pricing)
    num_judge_models = len(judge_pricing)
    debates_per_model = (num_debater_models - 1) * 2
    total_debates = num_debater_models * debates_per_model * debate_config.num_trials

    print("\n=== Experiment Scale ===")
    print(f"Debater models: {num_debater_models}")
    print(f"Judge models: {num_judge_models}")
    print(f"Debates per model: {debates_per_model}")
    print(f"Trials per debate: {debate_config.num_trials}")
    print(f"Total debates: {total_debates}")

    print("\n=== Debater Models & Pricing (per million tokens) ===")
    for model, prices in debater_pricing.items():
        print(f"{model}:")
        print(f"  Input: ${prices[0]:.4f}")
        print(f"  Output: ${prices[1]:.4f}")

    print("\n=== Judge Models & Pricing (per million tokens) ===")
    for model, prices in judge_pricing.items():
        print(f"{model}:")
        print(f"  Input: ${prices[0]:.4f}")
        print(f"  Output: ${prices[1]:.4f}")

    print("\n=== Token Usage Per Debate ===")
    input_tokens, output_tokens = count_debate_tokens(debate_config)
    print(f"Debater input tokens: {input_tokens:,.0f}")
    print(f"Debater output tokens: {output_tokens:,.0f}")
    print(
        f"Judge output tokens: {debate_config.judge_output_words * debate_config.words_to_tokens_multiplier:,.0f}"
    )

    # Calculate and show costs
    debater_cost = estimate_debater_cost(config, debate_config)
    judge_cost = estimate_judging_cost(config, debate_config)
    total_cost = debater_cost + judge_cost

    print("\n=== Cost Breakdown ===")
    print(f"Total debater cost: ${debater_cost:,.2f}")
    print(f"Total judging cost: ${judge_cost:,.2f}")
    print(f"Total experiment cost: ${total_cost:,.2f}")
    print(f"Cost per debate: ${total_cost / total_debates:,.2f}")


if __name__ == "__main__":
    config = Config()
    debate_config = DebateConfig()
    print_detailed_experiment_report(config, debate_config)
