from dotenv import load_dotenv
import click
from pathlib import Path
from anthropic import Anthropic
import os
from pydantic import BaseModel, HttpUrl
from rich.progress import track
from submit_batch import Profile

class ExtraInfo(BaseModel):
    id: str
    extra_info: str

def make_refinement_request(profile: Profile, site_info: str):
    request = {
        "model": "claude-3-7-sonnet-latest",
        "temperature": 0,
        "max_tokens": 2048,
        "system": "You are part of the AI system. Give the output with tool calls. No need to pretend that you're interacting with a human.",
        "messages": [
            {
                "role": "user",
                "content": f"""
                    Given the profile of a person (name, short description, long description, etc) and the scraped website info, refine the profile of this person using the website info. Your response can add a little bit or a lot to the long description depends on how much real info there is in the websites. Keep the short description concise.

                    Profile: {profile.model_dump_json(indent=4)}

                    Scraped website info:
                    {site_info}
                """,
            }
        ],
        "tools": [
            {
                "name": "output_refined_profile",
                "description": "Your response. Make sure `links` and `contacts` are lists.",
                "input_schema": Profile.model_json_schema()
            }
        ],
        "tool_choice": {"type": "tool", "name": "output_refined_profile"},
    }
    return request

@click.command()
@click.argument('batch_id')
def refine_profiles(batch_id: str):
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    profiles = []

    for result in client.messages.batches.results(
        batch_id,
    ):
        match result.result.type:
            case "succeeded":
                print(f"Success! {result.custom_id}")
                for content in result.result.message.content: # type: ignore
                    if content.type == "tool_use" and content.name == "create_profile":
                        profile = content.input
                        profiles.append(Profile(**profile)) # type: ignore
                        break
            case "errored":
                if result.result.error.type == "invalid_request": # type: ignore
                    # Request body must be fixed before re-sending request
                    print(f"Validation error {result.custom_id}")
                else:
                    # Request can be retried directly
                    print(f"Server error {result.custom_id}")
            case "expired":
                print(f"Request expired {result.custom_id}")

    # refinement
    data_dir = Path("data/")
    names = [d.name for d in (data_dir / 'linkedin_profiles').iterdir()]
    requests = []
    for i, (name, profile) in enumerate(zip(names, profiles)):
        lower_name = name.lower().replace(' ', '_')
        dir = data_dir / 'raw' / lower_name
        if not dir.exists() or dir.is_file():
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
            "params": make_refinement_request(profile, raw_info)
        })
    response = client.messages.batches.create(requests=requests) # type: ignore
    print(response)

if __name__ == "__main__":
    load_dotenv()
    refine_profiles()
