import os
import json
from .queriers import LLMQuerier
from .prompts import (
    get_simple_prompt,
    get_comparison_prompt,
    parse_simple_list_prompt,
    parse_simple_prompt_response,
    get_reason_prompt,
)
from .person import Person
import random
from .elo import update_elo_batch
from .bm25wrapper import BM25SWrapper
from typing import Optional
import chromadb
import numpy as np


class Matcher:
    ALLOWED_METHODS = {"simple", "elo"}

    def __init__(self, data_dir: str, model_config: str, db_dir: str = "rag_db", rrf_offset: float = 60.0) -> None:
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

                    self.people[person.name.lower().strip()] = person

        self.llmq = LLMQuerier("logs/matching_logs", "matching_cache.json", 12800)

        self.model_config = model_config

        self.cdb_client = chromadb.PersistentClient(path=db_dir)
        self.cdb_client.get_or_create_collection(name="cdb_people")
        self.cdb_client.delete_collection(name="cdb_people")
        self.cdb_collection = self.cdb_client.create_collection("cdb_people")

        # Add all people to cdb collection
        self.cdb_collection.add(
            ids=list(self.people.keys()), documents=[person.long_description for person in self.people.values()]
        )

        self.bm25w = BM25SWrapper()
        self.bm25w.init_bm25({n: p.long_description for n, p in self.people.items()})
        self.bm25w.save(db_dir)
        self.rrf_offset = rrf_offset

    def generate(self, queries: list[dict[str, str]]) -> list[str]:
        return self.llmq.generate(self.model_config, queries, max_tokens=4096, temperature=0.5, top_p=0.95)

    def simple_query(self, query_str: str, k: int, names: Optional[list[str]] = None) -> list[Person]:
        if names is None:
            names = list(self.people.values())
        query = get_simple_prompt(query_str, [self.people[name] for name in names], k)
        output = self.generate([query])[0]

        reason, output_names = parse_simple_list_prompt(output)
        output_names = [name.lower() for name in output_names]
        assert len(output_names) == k

        return [self.people[name] for name in output_names]

    def elo_query(
        self, query_str: str, k: int, names: Optional[list[str]] = None, num_pairs: int = 100
    ) -> list[Person]:
        # Initialize Elo ratings for all people

        # Generate random pairs of people for comparison
        pairs = []
        if names is None:
            names = list(self.people.values())

        for _ in range(num_pairs):
            # Sample 2 different people
            p1, p2 = random.sample(names, k=2)
            pairs.append((p1, p2))

        queries = [get_comparison_prompt(query_str, self.people[p1], self.people[p2]) for p1, p2 in pairs]
        outputs = self.generate(queries)
        winning_names = [parse_simple_prompt_response(output)[1] for output in outputs]

        ratings = {name: 1500.0 for name in self.people}
        update_elo_batch(ratings, [(p1, p2, win.lower()) for (p1, p2), win in zip(pairs, winning_names)])
        sorted_elos = sorted([(r, n) for n, r in ratings.items()], reverse=True)
        return [self.people[n] for _, n in sorted_elos[:k]]

    def query(self, query_str: str, method: str, k: int = 1, max_rag: int = 25, **kwargs) -> list[Person]:
        max_rag = max(max_rag, k)
        chroma_results = self.cdb_collection.query(query_texts=[query_str], n_results=len(self.people))
        chroma_result_ids = chroma_results["ids"]

        bm25_result_ids = self.bm25w.query([query_str], k=len(self.people))

        # Combine document IDs and create mapping
        all_ids = list(self.people.keys())
        id_to_idx = {doc_id: i for i, doc_id in enumerate(all_ids)}

        # Calculate rankings matrix
        rankings = np.ones((1, len(all_ids), 2)) * len(self.people)
        for i, (sub_chroma_result_ids, sub_bm25_result_ids) in enumerate(zip(chroma_result_ids, bm25_result_ids)):
            for j, (chroma_id, bm25_id) in enumerate(zip(sub_chroma_result_ids, sub_bm25_result_ids)):
                if not (method == "semantic"):
                    rankings[i, id_to_idx[bm25_id], 1] = j
                if not (method == "bm25"):
                    rankings[i, id_to_idx[chroma_id], 0] = j

        # Calculate RRF scores and get top results
        ratings = np.sum(1 / (self.rrf_offset + rankings + 1), axis=2)
        top_k_idxs = np.argsort(-ratings, axis=1)[:, :max_rag]
        top_names = np.array(all_ids)[top_k_idxs].tolist()[0]

        if method not in self.ALLOWED_METHODS:
            raise ValueError(f"Method {method} not in {self.ALLOWED_METHODS}")

        if method == "simple":
            return self.simple_query(query_str, k, names=top_names, **kwargs)

        if method == "elo":
            return self.elo_query(query_str, k, names=top_names, **kwargs)

    def get_everyone(self) -> list[Person]:
        return list(self.people.values())

    def get_specific_reason(self, query: str, names: list[str]) -> list[str]:
        names = [name.strip().lower() for name in names]
        prompts = [get_reason_prompt(query, self.people[name]) for name in names]
        return self.generate(prompts)


def main():
    random.seed(42)
    # m = Matcher("data", "model_configs/haiku-3-5.json")
    m = Matcher("data", "model_configs/gpt-4o-mini.json")
    # p = m.query(
    #     "I am Rex Liu. I want to meet with someone who is interested in AI safety and has done cybersecurity/pentesting.",
    #     "elo",
    #     num_pairs=4200,
    #     k=3,
    # )
    p = m.query(
        "I am Rex Liu. I want to meet with someone who is interested in AI safety and has interned at Jane Street.",
        # "Astrazeneca working Ramp, General Analysis Jane Street",
        "simple",
        k=2,
    )
    # p = m.query("I am Rex Liu. I want to meet with someone who has interned at Jane Street.", "elo", num_pairs=15)
    # p = m.query("I am Rex Liu. I want to meet with someone who has interned at Jane Street.", "simple")
    # print("OUTPUT PERSON:", p[0].__repr__(), p[1], p[2].__repr__())
    print("OUTPUT PERSON:", p[0].__repr__(), p[1].__repr__())
    print(m.llmq.current_price, "EEE")
    # print(
    #     m.get_specific_reason(
    #         "I am Rex Liu. I want to meet with someone who is interested in AI safety and has done cybersecurity/pentesting.",
    #         ["aaquib syed", "david bai"],
    #     )
    # )


if __name__ == "__main__":
    main()
