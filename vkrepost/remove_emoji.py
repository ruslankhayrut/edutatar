import re

RE_EMOJI = re.compile("[\U00010000-\U0010ffff]", flags=re.UNICODE)


def strip_emoji(text):
    return RE_EMOJI.sub(r"", text)
