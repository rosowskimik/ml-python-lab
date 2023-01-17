import re


def reg_match(s: str) -> bool:
    return re.fullmatch(r"^(gfedcba|gagagaa|abcdefg)$", s) is not None


def main():
    print("Should match")
    for s in ["gfedcba", "gagagaa", "abcdefg"]:
        print(f"{s} -> {'match' if reg_match(s) else 'no match'}")

    print("\nShould not match")
    for s in ["abcdefz", "abc"]:
        print(f"{s} -> {'match' if reg_match(s) else 'no match'}")


if __name__ == "__main__":
    main()
