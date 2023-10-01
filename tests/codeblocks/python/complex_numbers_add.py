    def __radd__(self, other):
        return self.__add__(other)


    def __rmul__(self, other):
        return self.__mul__(other)


    def __rtruediv__(self, other):
        if not isinstance(other, ComplexNumber):
            other = ComplexNumber(other, 0)
        return other.__truediv__(self)