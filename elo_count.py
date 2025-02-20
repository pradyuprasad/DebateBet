import glob
import os
from typing import Dict, List

from models import DebateTotal

def compute_elo_ratings(debates: List[DebateTotal], k_factor: int = 32) -> Dict[str, float]:
    """
    Computes Elo ratings for models based on a list of DebateTotal objects, scaling Elo changes by judge confidence.

    Args:
        debates (List[DebateTotal]): List of DebateTotal objects containing debate results.
        k_factor (int): The base K-factor for Elo rating updates (default is 32).

    Returns:
        Dict[str, float]: A dictionary mapping model names to their Elo ratings.
    """
    # Initialize Elo ratings for all models
    elo_ratings: Dict[str, float] = {}

    for debate in debates:
        # Get the models and their sides
        proposition_model = debate.proposition_model
        opposition_model = debate.opposition_model

        # Initialize ratings for new models
        if proposition_model not in elo_ratings:
            elo_ratings[proposition_model] = 1200  # Default starting rating
        if opposition_model not in elo_ratings:
            elo_ratings[opposition_model] = 1200  # Default starting rating

        # Get the current ratings
        proposition_rating = elo_ratings[proposition_model]
        opposition_rating = elo_ratings[opposition_model]

        # Determine the winner based on judge results
        if not debate.judge_results:
            raise ValueError(f"No judge results found for debate: {debate.motion.topic_description}")

        # Aggregate judge results to determine the winner and average confidence
        winner_counts = {"proposition": 0, "opposition": 0}
        total_confidence = 0

        for result in debate.judge_results:
            winner_counts[result.winner] += 1
            total_confidence += result.confidence

        # Determine the overall winner
        if winner_counts["proposition"] > winner_counts["opposition"]:
            winner = "proposition"
            loser = "opposition"
        elif winner_counts["opposition"] > winner_counts["proposition"]:
            winner = "opposition"
            loser = "proposition"
        else:
            # If it's a tie, skip updating ratings
            continue

        # Calculate average confidence for this debate
        average_confidence = total_confidence / len(debate.judge_results)

        # Calculate expected scores
        def expected_score(rating_a: float, rating_b: float) -> float:
            return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))

        expected_proposition = expected_score(proposition_rating, opposition_rating)
        expected_opposition = expected_score(opposition_rating, proposition_rating)

        # Scale the K-factor by confidence (normalized to 0-1)
        confidence_scale = average_confidence / 100  # Confidence is 0-100, so divide by 100
        scaled_k_factor = k_factor * confidence_scale

        # Update ratings based on the winner and scaled K-factor
        if winner == "proposition":
            proposition_rating += scaled_k_factor * (1 - expected_proposition)
            opposition_rating += scaled_k_factor * (0 - expected_opposition)
        else:
            proposition_rating += scaled_k_factor * (0 - expected_proposition)
            opposition_rating += scaled_k_factor * (1 - expected_opposition)

        # Update the Elo ratings dictionary
        elo_ratings[proposition_model] = proposition_rating
        elo_ratings[opposition_model] = opposition_rating

    return elo_ratings


folder_to_search = "debate_test_judges"
json_files = glob.glob(os.path.join(folder_to_search, "*.json"))

debate_list: List[DebateTotal] = []
for file in json_files:
    debate_total = DebateTotal.load_from_json(file)
    debate_list.append(debate_total)

print(compute_elo_ratings(debate_list))
