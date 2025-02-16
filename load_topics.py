from typing import List
from models import DebateTopic, TopicCategory

topics: List[DebateTopic] = [

    DebateTopic(
        topic_description="This House believes that offensive art should be commissioned for public spaces (Museums, Parks, Squares, etc.)",
        category=TopicCategory.CULTURE_AND_VALUES
    ),

    DebateTopic(
        topic_description="This House prefers a world where instead of charging tuition fees to students upfront, universities collect a portion of their income upon graduation",
        category=TopicCategory.GLOBAL_GOVERNANCE_AND_ECONOMICS
    ),

    DebateTopic(
        topic_description="This House would create a global carbon market",
        category=TopicCategory.GLOBAL_GOVERNANCE_AND_ECONOMICS
    ),

    DebateTopic(
        topic_description="This House would implement fairness doctrines on broadcast news media with significant audience reach",
        category=TopicCategory.POLITICS_AND_GOVERNANCE
    ),

    DebateTopic(
        topic_description="This House would require all elected officials to stand for a recall election if a significant minimum threshold of voters within their constituency demand it.",
        category=TopicCategory.POLITICS_AND_GOVERNANCE
    ),



    DebateTopic(
        topic_description="This House would overstate the impact of minority forces (Japanese American 442nd Battalion during WW2, Russia's Women's Battalion of Death during WW1, 4th Indian Infantry Division during WW2) in wars, even at the cost of historical accuracy.",
        category=TopicCategory.CULTURE_AND_VALUES
    ),

    DebateTopic(
        topic_description="This House is for the commercialisation of space",
        category=TopicCategory.GLOBAL_GOVERNANCE_AND_ECONOMICS
    ),

    DebateTopic(
        topic_description="This House believes that the International Olympic Committee should recognise an athlete's right to protest",
        category=TopicCategory.POLITICS_AND_GOVERNANCE
    ),

    DebateTopic(
        topic_description="This House is for academic activism",
        category=TopicCategory.CULTURE_AND_VALUES
    ),

    DebateTopic(
        topic_description="This House believes that developing countries should privatise their State-Owned Enterprises (such as airlines, railways, utility companies)",
        category=TopicCategory.GLOBAL_GOVERNANCE_AND_ECONOMICS
    )

]

def get_baseline_topic() -> DebateTopic:
    return DebateTopic(
        topic_description="This House would create a global carbon market",
        category=TopicCategory.GLOBAL_GOVERNANCE_AND_ECONOMICS,
    )

def get_all_topics() -> List[DebateTopic]:
    return topics
