# Odd Animal Party
Imagine a scenario where animals can speak like humans. They decide to have a party but with a catch: For a party to be valid, it must have an odd number of animals. But these animals also need to share at least one common attribute, like color, number of legs, etc. Your task is to create a function that accepts a list of dictionaries wherein each dictionary represents an animal, with properties represented as key-value pairs.

## Instructions
1. Write a function that takes in a list of dictionaries.
2. Each dictionary represents an animal having various properties like color and number of legs. These properties are represented as key-value pairs. All animals will definitely have the 'color' and 'legs' fields. However, they might have other extra attributes too.
3. The function should return a tuple. The first element of the tuple is a boolean that verifies whether the party is valid or not. The party is considered valid iff there are an odd number of animals and all animals share at least one common attribute. The second element of the tuple is a string that denotes the shared attribute: 'color' or 'legs'; if the party is invalid, return an empty string.

## Constraints
1. The list can contain up to 10^3 animals.
2. The 'color' attribute is always a string, and 'legs' attribute is always a positive integer.
3. All animals will have at least 'color' and 'legs' keys. They may have more attributes.
4. The function should return a tuple of (boolean, string).
5. If there is more than one shared attribute, the shared attribute in the output should be 'color'.

## Evaluation Criteria
1. The code should be able to handle and process large lists efficiently.
2. Correct use of data structures.
3. If there is more than one shared attribute, the shared attribute in the output should be 'color'.