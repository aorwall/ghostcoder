class Calculator:

    def add(self, a, b):
        return a + b

    def subtract(self, a, b):
        return a - b

    def multiply(self, a, b):
        return a * b

if __name__ == "__main__":
    calc = Calculator()
    print("Addition of 3 and 4: ", calc.add(3, 4))
    print("Subtraction of 10 and 4: ", calc.subtract(10, 4))
    print("Multiplication of 2 and 3: ", calc.multiply(2, 3))