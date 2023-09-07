from typing import List


def sum_of_multiples(level: int, factors: List[int]) -> int:
    """Calculate the total energy points earned by the player based on the level and the base values of the magical items.

    Args:
        level (int): The level that was just finished.
        factors (List[int]): The base values of the magical items collected by the player.

    Returns:
        int: Total energy points earned by the player.

    """

    def get_multiples(base: int) -> set:
        return {i * base for i in range(1, level // base + 1)}

    # Get all multiples of each factor up to the level
    multiples = [get_multiples(factor) for factor in factors]

    # Combine them into one set and remove duplicates
    combined_multiples =