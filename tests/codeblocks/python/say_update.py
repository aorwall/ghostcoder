def say(number):
    if not 0 <= number <= 999_999_999_999:
        raise ValueError("input out of range")

    # Handle numbers from 0 to 99
    if number < 100:
        if number == 0:
            return "zero"
        elif number < 20:
            return _small_numbers[number]
        else:
            tens, ones = divmod(number, 10)
            return f"{_tens[tens]} {_small_numbers[ones]}"

    # Handle numbers from 100 to 999
    elif number < 1000:
        hundreds = number // 100
        rest = number % 100
        if rest == 0:
            return f"{_small_numbers[hundreds]} hundred"
        else:
            return f"{_small_numbers[hundreds]} hundred and {say(rest)}"

    # Handle numbers from 1000 to 999,999,999,999
    else:
        thousands = number // 1000
        rest = number % 1000
        if rest == 0:
            return f"{say(thousands)} thousand"
        else:
            return f"{say(thousands)} thousand and {say(rest)}"
