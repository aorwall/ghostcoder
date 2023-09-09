from typing import List, Dict

def calculate_liabilities_and_equity(assets: List[int], debt_equity_ratio: float) -> List[Dict[str, int]]:
    """
    Calculate the liabilities and equity for each period given the total assets and the debt-equity ratio.
    
    Parameters:
    - assets (List[int]): A list of total assets for each period.
    - debt_equity_ratio (float): The debt-equity ratio.
    
    Returns:
    - List[Dict[str, int]]: A list of dictionaries where each dictionary represents a period and contains the total assets, liabilities, and equity for that period.
    
    Note:
    - Equity is calculated as Total Assets / (1 + Debt/Equity Ratio).
    - Liabilities is calculated as Total Assets - Equity.
    - The results should be rounded to the nearest integer.
    """
    pass