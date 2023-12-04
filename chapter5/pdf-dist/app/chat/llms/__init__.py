from functools import partial
from .chatopenai import build_llm

llm_map = {
    # builder(chat_args, model_name) 과 같이 인수 전달
    "gpt-4": partial(build_llm, model_name="gpt-4"),
    "gpt-3.5-turbo": partial(build_llm, model_name="gpt-3.5-turbo")
}