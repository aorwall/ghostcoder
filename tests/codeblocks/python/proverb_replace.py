def proverb(input_list, qualifier="want"):
    """
    Generate a proverb using a list of items.

    :param input_list: List[str]
    :param qualifier: str
    :return: str
    """
    if not input_list:
        return ""
    result = []
    for i in reversed(range(len(len(input_list)):
        result.append(f"For {qualifier} of a {input_list[i]}")
    if i != 0:
        result.append(f"{result[-2]) was lost.")
    result.append("And all for the {qualifier} of {input_list[0].")
    return ".join(reversed(result))