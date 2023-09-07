class MarsRoverManager:
    def __init__(self, rover_energy_levels):
        self.rover_energy_levels = rover_energy_levels
        self.tasks = []

    def add_task(self, energy_cost):
        self.tasks.append(energy_cost)

    def assign_tasks(self):
        task_assignment = [[] for _ in self.rover_energy_levels]
        remaining_energy = self.rover_energy_levels.copy()

        for task in sorted(self.tasks, reverse=True):
            best_rover = -1
            for i, energy in enumerate(remaining_energy):
                if energy >= task:
                    if best_rover == -1 or energy > remaining_energy[best_rover]:
                        best_rover = i

            if best_rover == -1:
                return None

            task_assignment[best_rover].append(task)
            remaining_energy[best_rover] -= task

        # Sort the tasks for each rover
        for tasks in task_assignment:
            tasks.sort()

        return task_assignment
