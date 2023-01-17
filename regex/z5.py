import re

from util import get_text


def link(s: str) -> list[str]:
    links = re.findall(
        r"\b((?:https?)?:\/\/(?:www\.)?[a-zA-Z0-9\-_%]+\.[a-zA-Z]{2,}(?:\/[a-zA-Z0-9\-_%]+)*\/?)",
        s,
    )
    return links


def main():
    for a in link(get_text()):
        print(a)


if __name__ == "__main__":
    main()
