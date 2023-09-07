class RawMaterial:

    def __init__(self, length, width, height):
        self.length = length
        self.width = width
        self.height = height

    def precise_cut(self, cut_length, cut_width, cut_height):
        # Check if the cut dimensions are valid
        if cut_length <= 0 or cut_width <= 0 or cut_height <= 0:
            return "Invalid cut dimensions"

        # Check if the cut dimensions exceed the current dimensions of the material
        if cut_length > self.length or cut_width > self.width or cut_height > self.height:
            return "Cut dimensions exceed material dimensions"

        # Update the dimensions of the material after the cut
        self.length -= cut_length
        self.width -= cut_width
        self.height -= cut_height

        return f"Material dimensions after cut: {self.length} x {self.width} x {self.height}"

    def get_current_size(self):
        return f"Current material dimensions: {self.length} x {self.width} x {self.height}"

    def get_volume(self):
        return self.length * self.width * self.height