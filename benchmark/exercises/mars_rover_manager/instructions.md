In this exercise, you are tasked with managing a fleet of rovers exploring Mars. You need to schedule tasks for these rovers efficiently. Each rover has a limited energy level and each task consumes a certain amount of energy. Your goal is to allocate tasks to the rovers in such a way that they get completed while respecting the energy limitations.

Write a Python class called MarsRoverManager that has the following methods:

* __init__(self, rover_energy_levels): Initialize a new MarsRoverManager with a list of energy levels for each rover.
* add_task(self, energy_cost): Add a new task to the list of tasks to be completed. Each task will consume energy_cost amount of energy.
* assign_tasks(self): Assign tasks to rovers. Return a list of lists where each sub-list represents the list of task energy costs assigned to one rover. Return None if it's not possible to complete all tasks.

* You may assume that the tasks can be done in any order, and that rovers can share the tasks.

Constraints:

rover_energy_levels and energy_cost are lists of non-negative integers.
Do not use any third-party libraries.
