import json
from typing import List, Dict, Any
from config import Config
from topic import DebateTopic

config = Config()
with open(config.topics_data_path) as f:
    data: List[Dict[str, Any]] = json.load(f)

for unparsed_topic in data:
    parsed_topic = DebateTopic(**unparsed_topic)
    print(parsed_topic.topic_description)
