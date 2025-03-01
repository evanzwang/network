from dotenv import load_dotenv
import click
from pathlib import Path
from anthropic import Anthropic
import os
from pydantic import BaseModel, HttpUrl
from rich.progress import track


class Profile(BaseModel):
    id: str
    name: str
    profile_pic: str
    links: list[str]
    short_description: str
    long_description: str

def make_request(raw_info: str):
    request = {
        "model": "claude-3-7-sonnet-latest",
        "temperature": 0,
        "max_tokens": 2048,
        "system": "You are summarizing the scraped raw linkedin info about a person. Use tool calls to output the expected json schema.",
        "messages": [
            {
                "role": "user",
                "content": f"""
                    Output a profile object from the raw linkedin data. The `id` field is the linkedin public id. Make two versions of descriptions: short one should be a few sentences. The long one can be as long as needed to incorporate all relevant information about the person. `links` should include a list of links to personal websites, social accounts, etc. For contacts and links, make sure to output a list even with one element. You are looking at a participant in an AI hackathon. Most people are students or recent graduates with some experience in AI. You response should highlight their uniqueness (e.g. subfields, experiences) rather just stating their interests in AI. Don't mention trivial stats like number of connections, followers, and test scores.

                    Linkedin Data:
                    {raw_info}
                """,
            }
        ],
        "tools": [
            {
                "name": "create_profile",
                "description": "Your response. Make sure `links` and `contacts` are lists.",
                "input_schema": Profile.model_json_schema()
            }
        ],
        "tool_choice": {"type": "tool", "name": "create_profile"},
    }
    return request

def parse_info():
    data_dir = Path("data/linkedin_profiles")
    people_dirs = list(data_dir.iterdir())
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    requests = []
    for i, dir in enumerate(track(people_dirs)):
        if dir.is_file():
            continue
        raw_infos = []
        for file in dir.iterdir():
            with open(file, 'r') as f:
                s = f.read()
                if len(s) > 100000:
                    print(f"skipping {file}")
                    continue
                raw_infos.append(s)
        raw_info = "\n".join(raw_infos)
        requests.append({
            "custom_id": str(i),
            "params": make_request(raw_info)
        })

    response = client.messages.batches.create(requests=requests) # type: ignore
    print(response)
    

if __name__ == "__main__":
    load_dotenv()
    parse_info()
