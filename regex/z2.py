import re

from util import get_text


def postal_codes(s: str) -> list[str]:
    postal_codes = re.findall(r"\b(\d{2}-\d{3})", s)
    return postal_codes


def main():
    text = get_text()

    for code in postal_codes(text):
        print(code)


if __name__ == "__main__":
    main()
