# The Mysterious Fruit Heist 

In the small town of Oodle, people have been reporting mysterious fruit disappearances from their gardens. To solve this fruit heist, they have decided to track the inventory of the fruits in their gardens. 

## Instructions 
1. Create a function that accepts two arguments, a current state of the fruits inventory (as a list of fruit names) and a list containing the names of fruits one by one as they disappear. 
2. The function should update the inventory using the disappeared fruits and return a new list of fruits left in the inventory.

## Constraints
1. The items in the inventory should be stored and returned as strings.
2. The inventory can contain the same fruit more than once and each fruit must be removed individually.
3. If a fruit name in the disappeared list does not exist in the inventory, it should be ignored.
4. Both the inventory list and disappeared list can have any length. 

## Evaluation Criteria 
1. The function must correctly update the fruit inventory according to the disappeared fruits.
2. The function should be able to handle input in any order and quantity.
3. The function should ignore any fruit from the disappeared list that do not exist in the inventory. 
4. Code readability, simplicity and comment clarity will be considered during evaluation.