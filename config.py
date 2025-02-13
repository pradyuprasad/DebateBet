from dataclasses import dataclass
from pathlib import Path

@dataclass
class Config:
    topics_data_path: Path = Path("topics.json")
