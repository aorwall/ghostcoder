import unittest
from legal_case_management_system import Team, Case, ManagementSystem

class TestLegalCaseManagementSystem(unittest.TestCase):
    def setUp(self):
        self.system = ManagementSystem()

    def test_team_creation(self):
        team = Team("Team A", 0)
        self.assertEqual(team.name, "Team A")
        self.assertEqual(team.workload, 0)

    def test_case_creation(self):
        case = Case("Case 1", 10)
        self.assertEqual(case.id, "Case 1")
        self.assertEqual(case.workload, 10)

    def test_add_team_to_system(self):
        team = Team("Team A", 0)
        self.system.add_team(team)
        self.assertIn(team, self.system.teams)

    def test_assign_case_to_team(self):
        team = Team("Team A", 0)
        self.system.add_team(team)
        case = Case("Case 1", 10)
        self.system.assign_case(case)
        self.assertEqual(team.workload, 10)

    def test_assign_case_with_no_teams(self):
        case = Case("Case 1", 10)
        with self.assertRaises(Exception):
            self.system.assign_case(case)

    def test_get_team_workload(self):
        team = Team("Team A", 0)
        self.system.add_team(team)
        case = Case("Case 1", 10)
        self.system.assign_case(case)
        self.assertEqual(self.system.get_team_workload("Team A"), 10)

    def test_print_all_workloads(self):
        team1 = Team("Team A", 0)
        team2 = Team("Team B", 0)
        self.system.add_team(team1)
        self.system.add_team(team2)
        case1 = Case("Case 1", 10)
        case2 = Case("Case 2", 20)
        self.system.assign_case(case1)
        self.system.assign_case(case2)
        self.assertEqual(self.system.print_all_workloads(), {"Team A": 10, "Team B": 20})

    def test_assign_case_to_lowest_workload_team(self):
        team1 = Team("Team A", 0)
        team2 = Team("Team B", 0)
        self.system.add_team(team1)
        self.system.add_team(team2)
        case1 = Case("Case 1", 10)
        case2 = Case("Case 2", 20)
        self.system.assign_case(case1)
        self.system.assign_case(case2)
        self.assertEqual(self.system.get_team_workload("Team A"), 10)
        self.assertEqual(self.system.get_team_workload("Team B"), 20)

    def test_case_reassignment(self):
        team = Team("Team A", 0)
        self.system.add_team(team)
        case = Case("Case 1", 10)
        self.system.assign_case(case)
        with self.assertRaises(Exception):
            self.system.assign_case(case)

    def test_multiple_teams_same_workload(self):
        team1 = Team("Team A", 0)
        team2 = Team("Team B", 0)
        self.system.add_team(team1)
        self.system.add_team(team2)
        case1 = Case("Case 1", 10)
        case2 = Case("Case 2", 10)
        self.system.assign_case(case1)
        self.system.assign_case(case2)
        self.assertEqual(self.system.get_team_workload("Team A"), 10)
        self.assertEqual(self.system.get_team_workload("Team B"), 10)

if __name__ == '__main__':
    unittest.main()
