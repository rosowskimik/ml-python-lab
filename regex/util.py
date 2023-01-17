def get_text() -> str:
    with open("text.txt") as f:
        return f.read()
