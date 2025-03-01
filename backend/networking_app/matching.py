import os
import json
from .queriers import LLMQuerier
from .prompts import get_simple_prompt, get_comparison_prompt, parse_simple_prompt_response
from .person import Person
import random
from .elo import update_elo_batch


class Matcher:
    ALLOWED_METHODS = {"simple", "elo"}

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
                        profile_pic=data.get("profile_pic", ""),
                        contacts=data.get("contacts", []),
                        links=data.get("links", []),
                        short_description=data.get("short_description", ""),
                        long_description=data.get("long_description", ""),
                    )

                    self.people[person.name.lower()] = person

        self.llmq = LLMQuerier("logs/matching_logs", "matching_cache.json", 12800)

        self.model_config = model_config

    def generate(self, queries: list[dict[str, str]]) -> list[str]:
        return self.llmq.generate(self.model_config, queries, max_tokens=4096, temperature=0.5, top_p=0.95)

    def simple_query(self, query_str: str) -> Person:
        query = get_simple_prompt(query_str, list(self.people.values()))

        output = self.generate([query])[0]

        reason, name = parse_simple_prompt_response(output)
        name = name.lower()

        if name not in self.people:
            raise ValueError(f"{name} not found in list of people.")

        return self.people[name]

    def elo_query(self, query_str: str, k: int, num_pairs: int = 100) -> list[Person]:
        # Initialize Elo ratings for all people

        # Generate random pairs of people for comparison
        pairs = []
        people_list = list(self.people.keys())

        for _ in range(num_pairs):
            # Sample 2 different people
            p1, p2 = random.sample(people_list, k=2)
            pairs.append((p1, p2))

        queries = [get_comparison_prompt(query_str, self.people[p1], self.people[p2]) for p1, p2 in pairs]
        outputs = self.generate(queries)
        winning_names = [parse_simple_prompt_response(output)[1] for output in outputs]

        ratings = {name: 1500.0 for name in self.people}
        update_elo_batch(ratings, [(p1, p2, win.lower()) for (p1, p2), win in zip(pairs, winning_names)])
        sorted_elos = sorted([(r, n) for n, r in ratings.items()], reverse=True)
        return [self.people[n] for _, n in sorted_elos[:k]]

    def query(self, query_str: str, method: str, k: int = 1, **kwargs) -> list[Person]:
        if method not in self.ALLOWED_METHODS:
            raise ValueError(f"Method {method} not in {self.ALLOWED_METHODS}")

        if method == "simple":
            if k != 1:
                raise ValueError("k must be 1 for simple method")

            return [self.simple_query(query_str, **kwargs)]

        if method == "elo":
            return self.elo_query(query_str, k, **kwargs)
    
    def get_everyone(self) -> list[Person]:
        return list(self.people.values())


def main():
    random.seed(42)
    # m = Matcher("data", "model_configs/haiku-3-5.json")
    m = Matcher("data", "model_configs/gpt-4o-mini.json")
    p = m.query(
        "I am Rex Liu. I want to meet with someone who is interested in AI safety and has done cybersecurity/pentesting.",
        "elo",
        num_pairs=4200,
        k=3,
    )
    # p = m.query("I am Rex Liu. I want to meet with someone who has interned at Jane Street.", "elo", num_pairs=15)
    # p = m.query("I am Rex Liu. I want to meet with someone who has interned at Jane Street.", "simple")
    print("OUTPUT PERSON:", p[0].__repr__(), p[1], p[2].__repr__())
    print(m.llmq.current_price, "EEE")


if __name__ == "__main__":
    main()
