class Example:

    my_variable = 10

    def __init__(self):
        self.instance_variable = 20

    def my_method(self, parameter):
        self.my_variable = parameter

        if parameter > 5:
            print("Parameter is greater than 5")

        for i in range(10):
            print(f"For loop iteration: {i}")

        while parameter < 10:
            print(f"While loop, parameter: {parameter}")
            parameter += 1

        try:
            if parameter == 8:
                raise ValueError("Random exception")
        except ValueError as e:
            print(f"Caught exception: {e}")
        finally:
            print("Finally block executed")

    addition = lambda self, a, b: a + b

    class InnerClass:
        def inner_method(self):
            print("This is an inner class method")

    @staticmethod
    def static_example_method():
        print("Static method executed")

    @classmethod
    def class_example_method(cls):
        print("Class method executed")

