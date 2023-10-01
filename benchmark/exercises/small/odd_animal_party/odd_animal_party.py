def odd_animal_party(animals):
    # Check if the number of animals is odd
    if len(animals) % 2 == 0:
        return (False, "")

    # Check if all animals have the same color
    colors = set(animal['color'] for animal in animals)
    if len(colors) == 1:
        return (True, "color")

    # Check if all animals have the same number of legs
    legs = set(animal['legs'] for animal in animals)
    if len(legs) == 1:
        return (True, "legs")

    # If neither color nor legs are the same for all animals
    return (False, "")