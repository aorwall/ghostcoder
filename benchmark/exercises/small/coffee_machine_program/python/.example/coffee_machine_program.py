def max_coffee_cups(coffee_grams: int, water_ml: int) -> int:
    """
    Function to calculate the maximum number of cups of coffee that can be produced
    given the amount of coffee beans and water.
    """
    # Constants for coffee and water required for one cup
    COFFEE_PER_CUP = 18
    WATER_PER_CUP = 200

    # Calculate the number of cups that can be made from the coffee and water
    coffee_cups = coffee_grams // COFFEE_PER_CUP
    water_cups = water_ml // WATER_PER_CUP

    # Return the minimum of the two, as that's the maximum number of cups we can make
    return min(coffee_cups, water_cups)