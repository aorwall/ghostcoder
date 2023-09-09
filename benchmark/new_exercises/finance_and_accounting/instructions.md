# FinStat - Finance and Accounting Program 

Write a program to calculate the liabilities and shareholder's equity for a company using a given array of assets and a provided debt-equity ratio.

## Instructions
1. Define a function that takes two parameters: An array representing the total assets of a company at different periods and a single float representing the debt-equity ratio.
2. This function should return an array of objects, where each object represents the period, total assets, liabilities, and shareholder's equity for that period.
3. First, calculate total equity using the formula Equity = Total Assets / (1 + Debt/Equity Ratio). 
4. Once the equity is calculated, find the liabilities using the formula Liabilities = Total Assets - Equity.
5. The results should be calculated in chronological order, i.e., the first number in the assets array corresponds to the first period; the second number corresponds to the second period; and so on.

## Constraints
1. The asset array will contain positive numbers only. Each number represents total assets for a specific period. A period can be a year, a quarter, a month, etc.
2. The debt-equity ratio will be a float number and will always be positive.
3. The function should be able to handle at least 100 periods, i.e., the array could contain up to 100 elements.
4. Round your result to the nearest integer for both liabilities and equity.
