def odd_animal_party(animals):
    if len(animals) % 2 == 0:
        return (False, '')
    color = animals[0]['color']
    legs = animals[0]['legs']
    for animal in animals[1:]:
        if animal['color'] != color and animal['legs'] != legs:
            return (False, '')
    return (True, 'color' if color == animals[1]['color'] else 'legs')