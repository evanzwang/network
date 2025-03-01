from typing import Dict, List, Union, Any, Optional


Message = Dict[str, str]
Conversation = List[Message]
Prompt = Union[str, Conversation]


def logprobs_to_cumulative(logprobs):  # NOTE: normalized
    c = 0
    for logprob in logprobs:
        c += logprob
    return c / len(logprobs)


class Completion:
    def __init__(self, code: str, cumulative_logprob: float, num_tokens: int, orm_score: Optional[float] = None):
        self.code = code
        self.cumulative_logprob = cumulative_logprob
        self.num_tokens = num_tokens
        self.orm_score = orm_score

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "code": self.code,
            "cumulative_logprob": self.cumulative_logprob,
            "num_tokens": self.num_tokens,
        }

        if self.orm_score is not None:
            d["orm_score"] = self.orm_score

        return d

    def __repr__(self) -> str:
        return f"Completion({self.code}, {self.cumulative_logprob}, {self.num_tokens})"

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Completion":
        assert "code" in d, "Missing 'code' key"
        assert "cumulative_logprob" in d, "Missing 'cumulative_logprob' key"
        assert "num_tokens" in d, "Missing 'num_tokens' key"
        return Completion(
            d["code"],
            d["cumulative_logprob"],
            d["num_tokens"],
            orm_score=d.get("orm_score", None),
        )
