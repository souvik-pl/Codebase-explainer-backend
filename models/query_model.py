from dataclasses import dataclass


@dataclass
class QueryResponse:
    question: str
    answer_html: str

    def to_dict(self) -> dict:
        return {
            "question": self.question,
            "answer_html": self.answer_html,
        }
