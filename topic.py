from pydantic import BaseModel
from enum import Enum


class TopicCategory(Enum):
    GLOBAL_GOVERNANCE_AND_ECONOMICS = "global_governance_and_economics"
    SOCIAL_JUSTICE_AND_IDENTITY = "social_justice_and_identity"
    CULTURE_AND_VALUES = "culture_and_values"
    POLITICS_AND_GOVERNANCE = "politics_and_governance"
    LAW_AND_CRIMINAL_JUSTICE = "law_and_criminal_justice"


class DebateTopic(BaseModel):
    topic_description: str
    category: TopicCategory
