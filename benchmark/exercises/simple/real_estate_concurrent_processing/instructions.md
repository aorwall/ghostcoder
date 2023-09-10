# Concurrent Property Price Calculator
In this exercise, you will implement a property price calculator that processes multiple properties concurrently. The prices of properties are calculated based on provided parameters for each property.

## Instructions
1. Define a class or structure to hold property data. The data should include attributes like location, square footage, number of bedrooms, number of bathrooms, and age of the property.
2. Initialize a list, or similar data structure, of these property objects. This list will serve as a set of properties for which the price needs to be calculated.
3. Write a method or function to calculate the price of a property based on its attributes. The calculation can involve simple arbitrary rules. For example, you can consider every square foot as $200, each bedroom as an additional $5000, and each year of age as a deduction of $1000 from the total price.
4. This calculator method or function should serve as the task to be performed concurrently for each property in the list of properties. Implement concurrent processing to calculate prices of all properties simultaneously (or as supported by the machine running your code).
5. Once all price calculations are done, return and display the property data along with their calculated prices.

## Constraints
1. Do not use third-party libraries, the standard library should be enough.
2. The prices calculated do not have to be realistic. Simple rules for price calculation are acceptable.
3. Your solution must use concurrent or multithreaded processing. Avoid calculating the prices for the properties in a sequential manner.
4. Consider thread-safety according to the specific paradigms of the chosen programming language.

## Evaluation
Your solution will be evaluated based on:
1. Correct implementation of concurrency or multithreading.
2. Proper use of data structures.
3. Code readability and organization.
4. Correct calculation of property prices.