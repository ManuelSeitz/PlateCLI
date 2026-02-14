def normalize_argentina(text: str) -> str:
    if len(text) == 7:
        return f"{text[:2]} {text[2:5]} {text[5:]}"

    if len(text) == 6:
        return f"{text[:3]} {text[3:]}"

    return text


def normalize_chile(text: str) -> str:
    if len(text) == 6 and text[:4].isalpha():
        return f"{text[:4]} {text[4:]}"

    if len(text) == 6 and text[:2].isalpha():
        return f"{text[:2]} {text[2:4]} {text[4:]}"

    return text


def normalize_text(text: str, country: str) -> str:
    text = text.replace(" ", "").upper()

    RULES = {"argentina": normalize_argentina, "chile": normalize_chile}

    if country not in RULES:
        return text

    return RULES[country](text)
