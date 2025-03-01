import os
import json
from queriers import LLMQuerier
import prompts
from person import Person


class Matcher:
    def __init__(self, data_dir: str, model_config: str) -> None:
        # load data
        self.people: dict[str, Person] = {}

        # Iterate through all json files in data directory
        for filename in os.listdir(data_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(data_dir, filename)
                with open(filepath, "r") as f:
                    data = json.load(f)

                    # Create new Person and populate fields
                    person = Person(
                        name=data.get("name", ""),
                        picture_file=data.get("picture_file", ""),
                        context=data.get("context", ""),
                        related_links=data.get("relevant_links", []),
                    )

                    self.people[person.name.lower()] = person

        self.llmq = LLMQuerier("logs/matching_logs", "matching_cache.json", 12800)

        self.model_config = model_config

    def query(self, query_str: str) -> Person:
        query = prompts.get_simple_prompt(query_str, list(self.people.values()))

        output = self.llmq.generate(self.model_config, [query], max_tokens=4096, temperature=0.5, top_p=0.95)[0]

        reason, name = prompts.parse_simple_prompt_response(output)
        name = name.lower()

        if name not in self.people:
            raise ValueError(f"{name} not found in list of people.")

        return self.people[name]


def main():
    m = Matcher("sample_data", "model_configs/sonnet-3-5.json")
    p = m.query("I am Rex Liu. I want to meet with someone who has interned at Jane Street.")
    print("OUTPUT PERSON:", p)


if __name__ == "__main__":
    main()
