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
        _, rest = divmod(number, 1000)
        return f"{say(rest)} thousand"


_small_numbers = {
    0: "zero",
    1: "one",
    2: "two",
    3: "three",
    4: "four",
    5: "five",
    6: "six",
    7: "seven",
    8: "eight",
    9: "nine",
    10: "ten",
    11: "eleven",
    12: "twelve",
    13: "thirteen",
    14: "fourteen",
    15: "fifteen",
    16: "sixteen",
    17: "seventeen",
    18: "eighteen",
    19: "nineteen",
}

_tens = {
    2: "twenty",
    3: "thirty",
    4: "forty",
    5: "fifty",
    6: "sixty",
    7: "seventy",
    8: "eighty",
    9: "ninety",
}
