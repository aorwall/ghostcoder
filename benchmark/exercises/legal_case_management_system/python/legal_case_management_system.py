class Team:
    def __init__(self, name, workload):
        self.name = name
        self.workload = workload

class Case:
    def __init__(self, id, workload):
        self.id = id
        self.workload = workload

class ManagementSystem:
    def __init__(self):
        self.teams = []

    def add_team(self, team):
        pass

    def assign_case(self, case):
        pass

    def get_team_workload(self, team_name):
        pass

    def print_all_workloads(self):
        pass
