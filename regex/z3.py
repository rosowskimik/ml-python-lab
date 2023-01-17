import re

from util import get_text


def phone_numbers(s: str) -> list[str]:
    phone_numbers = re.findall(r"((?:\+?\d{2})?(?:(?: |-|\.)?(?:\d{3})){3})", s)
    return phone_numbers


def main():
    for number in phone_numbers(get_text()):
        print(number)


if __name__ == "__main__":
    main()
