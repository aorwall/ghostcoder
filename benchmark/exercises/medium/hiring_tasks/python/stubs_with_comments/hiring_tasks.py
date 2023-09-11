from typing import List, Tuple

def arrange_servers(servers: List[Tuple[int, int]], power_capacity: int) -> List[List[Tuple[int, int]]]:
    """
    Arrange the servers on a grid in a way that maximizes the total performance without exceeding the total power capacity.
    
    Parameters:
    - servers (List[Tuple[int, int]]): A list of servers, each represented as a performance, power pair.
    - power_capacity (int): The total power capacity of the data center.
    
    Returns:
    - List[List[Tuple[int, int]]]: The layout of the grid, represented as a two-dimensional array where each slot contains the details of the assigned server or is empty if no server was placed there.
    """
    pass