# Data Center Optimization

In the IT industry, one of the challenges is to organize and place servers efficiently in a data center. This exercise is designed to test your ability to optimize the configuration of a data center.

## Instructions
1. Develop a program that simulates a grid to represent the arrangement of servers in a data center. Each server is represented as a unit square on the grid.
2. Servers have different performance capabilities and power requirements. These are represented by a pair of integer values - performance and power.
3. Your task is to write an algorithm that takes a list of servers (each represented as a performance, power pair) and the total power capacity of the data center as inputs. The algorithm should arrange the servers on the grid in a way that maximizes the total performance without exceeding the total power capacity of the data center.
4. The data center grid does not have a fixed size and can grow to accommodate servers as needed.
5. The output of your program should be the layout of the grid. This should be represented as a two-dimensional array where each slot contains the details of the assigned server or is empty if no server was placed there.

## Constraints

1. The performance and power of a server are positive integers not exceeding 10,000.
2. The total power capacity of the data center is a positive integer not exceeding 1,000,000.
3. The server list for input will contain a maximum of 1,000 servers.
4. If there are multiple optimal arrangements, your program can return any one of them.
5. Your program should be designed to execute within a reasonable time frame. Keep performance considerations in mind when designing your algorithm.