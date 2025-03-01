from dotenv import load_dotenv
import click
from pathlib import Path
from anthropic import Anthropic
import os
from pydantic import BaseModel, HttpUrl
from rich.progress import track
from submit_batch import Profile


@click.command()
@click.argument("batch_id")
def save_processed_data(batch_id: str):
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    message_batch = client.messages.batches.retrieve(batch_id)
    profiles = []

    for result in client.messages.batches.results(
        batch_id,
    ):
        match result.result.type:
            case "succeeded":
                print(f"Success! {result.custom_id}")
                for content in result.result.message.content: # type: ignore
                    if content.type == "tool_use":
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
        # print(profile)
        with open(save_dir / f"{profile.id}.json", 'w') as f:
            f.write(profile.model_dump_json(indent=4))
    print(f"Updated {len(profiles)} profiles.")

if __name__ == "__main__":
    load_dotenv()
    save_processed_data()
