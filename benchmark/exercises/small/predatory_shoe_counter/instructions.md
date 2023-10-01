# Predatory Shoe Counter
In a parallel universe, shoes are predatory creatures that prey upon socks. You work for a company that has created a protective device which alerts when a shoe is about to attack. The device calculates proximity of the shoe and timing of its attacks based on captured surveillance data. 

## Instructions
1. Create a function that takes two arrays; one that represents the distance of shoes from the socks in millimeters, and the other representing the time it would take for a shoe to attack in milliseconds. The lengths of both arrays are always equal, representing the same instances of shoe attacks. 
2. The function should calculate and return the total number of socks that would be lost if all the shoes attack at their calculated times.

## Constraints
1. The lengths of arrays can be between 1 and 10^5.
2. The values in the distance and time arrays are non-negative integers.
3. The time values in the arrays do not exceed 10^3 milliseconds.
4. A shoe can only prey upon one sock at its calculated time of attack. If two or more shoes have the exact same attack time, only a single sock is lost.

## Evaluation Criteria
1. The function correctly calculates the number of lost socks.
2. The function executes efficiently even for the maximum size of input arrays.