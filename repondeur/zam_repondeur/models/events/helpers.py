from difflib import Differ
from html import escape
from itertools import groupby
from operator import attrgetter
from typing import Iterable, NamedTuple


differ = Differ()


CODES_TO_TAGS = {"+ ": "ins", "- ": "del", "  ": None}


class Delta(NamedTuple):
    code: str
    text: str

    @classmethod
    def create(cls, delta_string: str) -> "Delta":
        return cls(code=delta_string[:2], text=delta_string[2:])

    @classmethod
    def merge(cls, code: str, deltas: Iterable["Delta"]) -> "Delta":
        return cls(code, " ".join(delta.text for delta in deltas))

    def to_html(self) -> str:
        tag = CODES_TO_TAGS[self.code]
        text = escape(self.text)
        if tag:
            return f"<{tag}>{text}</{tag}>"
        return text


def html_diff(old_text: str, new_text: str) -> str:
    old_words = old_text.split()
    new_words = new_text.split()
    word_deltas = (Delta.create(s) for s in differ.compare(old_words, new_words))
    merged_deltas = (
        Delta.merge(code, word_deltas)
        for code, word_deltas in groupby(word_deltas, key=attrgetter("code"))
        if code != "? "
    )
    html_fragments = (delta.to_html() for delta in merged_deltas)
    return " ".join(html_fragments).strip()