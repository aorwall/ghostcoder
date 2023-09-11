# Alien Matrix Resizer

In a distant galaxy, an alien species communicates with humans using numeric matrices. The catch? They can only understand matrices of specific lengths. 

Your task is to write a function that takes a matrix and a number as input. The function should take the matrix and ensure it fits the length provided. If the matrix is too long, the function should remove rows from the end. If the matrix is too short, it should add rows filled with zeros at the end. 

Note: For simplicity's sake, you can assume the input matrix will always be a 2-dimensional array, and the input number (length) is always a positive integer. All matrices and numbers are provided by the alien species. 

## Instructions 
1. Define a function that takes a two-dimensional array & an integer as input.
2. If the number of rows in the array is longer than the input integer, remove the excess rows. The function should not modify the original matrix.
3. If the number of rows in the array is shorter than the input integer, add new rows filled with zeros to meet the length. 

## Constraints
1. The input matrix will always be a 2D array.
2. The input integer will always be a positive integer. 

## Evaluation Criteria 
1. The function outputs the correct resized matrix.
2. The function successfully adds rows with zeroes if the array lacks rows and removes rows if the array has excess.
3. The function does not modify the original matrix.