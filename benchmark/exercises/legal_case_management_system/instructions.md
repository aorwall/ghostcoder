Title: Legal Case Management System Optimization

Description: 
In the context of our company's business scope, your task is to design a solution for a simplified legal case management system. You will need to create a program to assign cases to legal teams in a way that optimizes the workload across those teams. The system should keep track of the teams and their workloads and, when a new case comes in, assign it to the team with the currently lowest overall workload. 

Instructions:
1. Create a 'Team' class which holds information about a legal team. It should include, at least, the team name and the current workload.
2. Create a 'Case' class which represents a legal case. It should have, at the very minimum, an identifier and a workload value associated with it.
3. Implement a 'ManagementSystem' class that maintains a list of all teams and has the ability to add new teams to the list.
4. The 'ManagementSystem' class should also accept new cases and assign them to the team with the lowest workload at the moment of assignment. 
    - If several teams possess the same minimum workload, the case can be assigned to any of them.
    - The case's workload gets added to the team's current workload when the case is assigned.
    - If there are no teams in the system when a case is added, the system should throw an appropriate error.
5. The 'ManagementSystem' should also support querying for a team's current workload and a functionality to print the workload of all teams.

Constraints:
1. Workload values will always be positive integers.
2. No two cases can have the same identifier.
3. After a case has been assigned to a team, it cannot be reassigned.

This exercise is meant to assess your ability to design and implement an efficient solution to a problem. Pay particular attention to how your solution scales when the number of teams and cases grows.
