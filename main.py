from run_debate import run_debate
from openai import OpenAI
from dotenv import load_dotenv
import os
from debate_prompts import get_debator_prompts
from load_topics import get_baseline_topic
from pathlib import Path

load_dotenv()


prop_model = "meta-llama/llama-3.3-70b-instruct"
opposition_model = "openai/gpt-4o-mini"

client = OpenAI(
    base_url="https://openrouter.ai/api/v1", api_key=os.getenv("OPENROUTER_API_KEY")
)

debator_prompts = get_debator_prompts()

topic = get_baseline_topic()

path = Path("test_topic.json")

run_debate(
    proposition_model=prop_model,
    opposition_model=opposition_model,
    prompts=debator_prompts,
    client=client,
    motion=topic,
    path=path,
    judge_models=["qwen/qwen-plus"]
)
