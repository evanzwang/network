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
    contacts: list[str]
    links: list[str]
    short_description: str
    long_description: str


if __name__ == "__main__":
    load_dotenv()
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    batch_id = "msgbatch_01JMRYJuuiAjsLPGXbVJ3KSY"
    message_batch = client.messages.batches.retrieve(batch_id)
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
                        profiles.append(Profile(**profile))
                        break
            case "errored":
                if result.result.error.type == "invalid_request":
                    # Request body must be fixed before re-sending request
                    print(f"Validation error {result.custom_id}")
                else:
                    # Request can be retried directly
                    print(f"Server error {result.custom_id}")
            case "expired":
                print(f"Request expired {result.custom_id}")
    # dump into a dir
    save_dir = Path("data/processed")
    for profile in profiles:
        print(profile)
        with open(save_dir / f"{profile.id}.json", 'w') as f:
            f.write(profile.model_dump_json(indent=4))
