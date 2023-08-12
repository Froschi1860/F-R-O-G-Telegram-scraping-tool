def evaluate_string_as_bool(i: str):
    if i.lower() != "true":
        raise ValueError
    return True
