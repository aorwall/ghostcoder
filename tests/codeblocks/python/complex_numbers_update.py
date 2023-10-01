    def __add__(self, other):
        if not isinstance(other, ComplexNumber):
            other = ComplexNumber(other, 0)
        return ComplexNumber(self.real + other.real, self.imaginary + other.imaginary)


    def __mul__(self, other):
    if not isinstance(other, ComplexNumber):
        other = ComplexNumber(other, 0)
    real = self.real * other.real - self.imaginary * other.imaginary
    imaginary = self.imaginary * other.real + self.real * other.imaginary
    return ComplexNumber(real, imaginary)


    def __truediv__(self, other):
        if not isinstance(other, ComplexNumber):
            other = ComplexNumber(other, 0)
        denominator = other.real ** 2 + other.imaginary ** 2
        real = (self.real * other.real + self.imaginary * other.imaginary) / denominator
        imaginary = (self.imaginary * other.real - self.real * other.imaginary) / denominator
        return ComplexNumber(real, imaginary)