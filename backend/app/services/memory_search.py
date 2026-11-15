import re

_WORD = re.compile(r"\w{3,}", re.UNICODE)


def _words(text: str) -> set[str]:
    return {w.lower() for w in _WORD.findall(text or "")}


def select_relevant_memories(memories: list, query: str, limit: int) -> list:
    """memories newest-first aani chahiye. Match na ho to latest wali milti hain."""
    query_words = _words(query)
    scored = []
    for index, memory in enumerate(memories):
        text = f"{memory.title or ''} {memory.content}"
        scored.append((len(query_words & _words(text)), -index, memory))
    scored.sort(key=lambda item: (item[0], item[1]), reverse=True)
    return [item[2] for item in scored[:limit]]