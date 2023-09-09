from typing import List, Tuple

def arrange_servers(servers: List[Tuple[int, int]], power_capacity: int) -> List[List[Tuple[int, int]]]:
    n = len(servers)
    dp = [[0 for _ in range(power_capacity + 1)] for _ in range(n + 1)]
    for i in range(1, n + 1):
        performance, power = servers[i - 1]
        for j in range(1, power_capacity + 1):
            if power <= j:
                dp[i][j] = max(dp[i - 1][j], performance + dp[i - 1][j - power])
            else:
                dp[i][j] = dp[i - 1][j]

    # reconstruct the solution
    grid = []
    i, j = n, power_capacity
    while i > 0 and j > 0:
        if dp[i][j] != dp[i - 1][j]:
            server = servers[i - 1]
            if server[1] > j:  # if the server's power requirement exceeds the remaining power capacity
                break  # do not place the server on the grid
            if not grid or len(grid[-1]) == 2:  # if the last row is full or grid is empty
                grid.append([server])  # start a new row
            else:
                grid[-1].append(server)  # add server to the last row
            j -= server[1]
        i -= 1

    return grid