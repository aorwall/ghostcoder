# The Chicken Color Coordinator 

Your task is to help a farmer who has a problem with his chickens. The farmer is colorblind and has trouble distinguishing the colors of his chickens. He has three types of chickens in his chicken coop; red, green, and blue. He wants to group them according to their colors, but due to his color-blindness, he can't do it.

He needs a function that he can describe the color of a chicken to, and it will tell him which group that chicken belongs to. He will describe the colors by naming things in nature which have similar colors. For example, he might describe a red chicken as 'apple-like' or a green chicken as 'leaf-like'.

The function should take one parameter: the input string containing the farmer's description of a chicken's color. If the description suggests the color is red, return 'Red Group'. If the description suggests the color is green, return 'Green Group'. If the description suggests the color is blue, return 'Blue Group'.

Possible descriptions for each color are:
- Red: 'apple', 'rose', 'tomato'
- Green: 'leaf', 'grass', 'lime'
- Blue: 'sky', 'ocean', 'blueberry'

## Instructions
1. Implement a function that takes a string as input.
2. The function should return a string indicating the correct group (Red Group, Green Group, Blue Group) based on the description of the color provided in the input string.

## Constraints
1. The input string will always be in lowercase.
2. The input string will contain only alphabetic characters.
3. The input string will be a single word.
4. The input string will not contain any special characters or numbers.

## Evaluation Criteria
1. Function correctly classifies the input descriptions to their corresponding groups.
2. Code is clean, well-structured, and easy to read.
3. The solution does not use any built-in language functions or libraries that takes away the implementation of the problem from the developer.
4. The function handles invalid inputs correctly.