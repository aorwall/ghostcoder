# Precision Manufacturing 
Modern manufacturing & production businesses require careful control and precise attention to detail, especially when you are tasked to cut the material for use. In this task, you are to implement a small class that will simulate precision cutting on a manufacturing line.

## Instructions
1. Create a class to represent a single piece of raw material. The raw material should have parameters for length, width, and height.
2. Implement a method within the class, which takes in three cutting measurements (length, width, height) as parameters. This should simulate a precision cut of the raw piece in-place, effectively reducing its size.
    * Ensure the cut does not result in any dimension of the raw material becoming negative or zero. If any such cut is attempted, then it should be considered as invalid. 
    * After a successful cut, update the size of the raw material and return an appropriate message with the new dimensions.
    * In case of an invalid cut, return an appropriate error message.
3. Implement a method which returns the current dimensions of the material.
4. Implement a method which returns the volume of the material after all the applied cuts.

## Constraints
1. The initial length, width, and height of a piece of raw material should not exceed 10000 units.
2. All dimensions are positive integers.
3. Each method should be able to handle a maximum of 100 function calls within 1 second.