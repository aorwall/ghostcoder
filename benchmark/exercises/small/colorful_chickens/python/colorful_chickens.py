def chicken_color_group(color_description):
    red_group = ['apple', 'rose', 'tomato']
    green_group = ['leaf', 'grass', 'lime']
    blue_group = ['sky', 'ocean', 'blueberry']

    if color_description in red_group:
        return 'Red Group'
    elif color_description in green_group:
        return 'Green Group'
    elif color_description in blue_group:
        return 'Blue Group'
    else:
        return 'Invalid color description'