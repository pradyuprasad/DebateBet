from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    topics_data_path: Path = Path("topics.json")
    api_pricing_path: Path = Path("api_pricing.json")
    judge_pricing_path: Path = Path("judge_models.json")
