def roman(number):
    # Define the symbols for each numeral
    roman_numerals = {
        1000: 'M',
        900: 'CM',
        500: 'D',
        400: 'CD',
        100: 'C',
        90: 'XC',
        50: 'L',
        40: 'XL',
        10: 'X',
        9: 'IX',
        5: 'V',
        4: 'IV',
        1: 'I'
    }

    # Initialize the result string
    result = ''

    # Iterate through the symbols in descending order
    for value, numeral in roman_numerals.items():
        # Determine the number of times the current symbol appears in the number
        count = number // value

        # Add the current symbol to the result string
        result += numeral * count

        # Subtract the value of the current symbol from the number
        number -= value * count

    return result
