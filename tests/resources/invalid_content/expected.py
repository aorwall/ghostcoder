def proverb(input_list, qualifier="want"):
    if not input_list:
        return ""
    else:
        result = []
        for i in reversed(range(len(input_list))):
            result.append(f"For {qualifier} of {input_list[i]}")
            if i != 0:
                result.append(f"{result[-1]} was lost.")
                result.append(f"And all for the {qualifier} of {input_list[0]}")
        return " ".join(reversed(result))