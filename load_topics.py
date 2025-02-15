from models import DebateTopic, TopicCategory


def get_baseline_topic() -> DebateTopic:
    return DebateTopic(
        topic_description="This House would create a global carbon market",
        category=TopicCategory.GLOBAL_GOVERNANCE_AND_ECONOMICS,
    )
