from typing import List, Dict

def calculate_liabilities_and_equity(assets: List[int], debt_equity_ratio: float) -> List[Dict[str, int]]:
    result = []
    for i, total_assets in enumerate(assets):
        equity = round(total_assets / (1 + debt_equity_ratio))
        liabilities = total_assets - equity
        result.append({
            'period': i + 1,
            'total_assets': total_assets,
            'liabilities': liabilities,
            'equity': equity
        })
    return result