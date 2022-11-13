import re

RE_EMOJI = re.compile("[\U00010000-\U0010ffff]", flags=re.UNICODE)


def remove_emoji_from_text(text: str) -> str:
    return RE_EMOJI.sub(r"", text)
