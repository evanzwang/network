from dotenv import load_dotenv
import click
from pathlib import Path
from anthropic import Anthropic
import os
from pydantic import BaseModel, HttpUrl
from rich.progress import track


class Profile(BaseModel):
    name: str
    profile_pic: str
    contacts: list[str]
    links: list[HttpUrl]
    description: str

def make_request(raw_html: str):
    request = {
        "model": "claude-3-5-haiku-latest",
        "temperature": 0,
        "max_tokens": 1024,
        "system": "You are summarizing the scraped raw html info about a person. Use tool calls to output the expected json schema.",
        "messages": [
            {
                "role": "user",
                "content": raw_html,
            }
        ],
        "tools": [
            {
                "name": "create_profile",
                "description": "Output a profile summarized from the raw data.",
                "input_schema": Profile.model_json_schema()
            }
        ],
        "tool_choice": {"type": "tool", "name": "create_profile"},
    }
    return request

def parse(client: Anthropic, raw_html: str) -> Profile:
    # return Profile(name='1', profile_pic='1', contacts=[], links=[], description="")
    response = client.messages.create(**make_request(raw_html=raw_html))
    profile: Profile
    for content in response.content:
        if content.type == "tool_use" and content.name == "create_profile":
            profile = content.input
            break
    return profile # type: ignore


@click.command()
def parse_html():
    data_dir = Path("data/raw")
    people_dirs = list(data_dir.iterdir())
    print(os.getenv("ANTHROPIC_API_KEY"))
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    requests = []
    for i, dir in enumerate(track(people_dirs)):
        if dir.is_file():
            continue
        raw_htmls = []
        for file in dir.iterdir():
            with open(file, 'r') as f:
                s = f.read()
                if len(s) > 50000:
                    print(f"skipping {file}")
                    continue
                raw_htmls.append(s)
        raw_html = "\n".join(raw_htmls)
        requests.append({
            "custom_id": str(i),
            "params": make_request(raw_html)
        })

    response = client.messages.batches.create(requests=requests) # type: ignore
    print(response)

if __name__ == "__main__":
    load_dotenv()
    parse_html()
