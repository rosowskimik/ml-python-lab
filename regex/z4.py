import re

from util import get_text


def email(s: str) -> list[str]:
    emails = re.findall(
        r"[a-zA-Z0-9.!#$%=&`*+{|}^_~\-\/]+@[a-zA-Z0-9\-]+(?:\.[a-zA-Z0-9\-]+)*", s
    )
    return emails


def main():
    for mail in email(get_text()):
        print(mail)


if __name__ == "__main__":
    main()
