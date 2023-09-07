import unittest

from mars_rover_manager_solution import MarsRoverManager


class TestMarsRoverManager(unittest.TestCase):

    def test_no_tasks(self):
        mgr = MarsRoverManager([10, 20, 30])
        self.assertEqual(mgr.assign_tasks(), [[], [], []])

    def test_impossible_tasks(self):
        mgr = MarsRoverManager([10, 20])
        mgr.add_task(50)
        self.assertIsNone(mgr.assign_tasks())

    def test_single_rover(self):
        mgr = MarsRoverManager([30])
        mgr.add_task(10)
        mgr.add_task(20)
        self.assertEqual(mgr.assign_tasks(), [[10, 20]])

    def test_multiple_rovers(self):
        mgr = MarsRoverManager([30, 40, 50])
        mgr.add_task(20)
        mgr.add_task(30)
        mgr.add_task(40)
        result = mgr.assign_tasks()
        self.assertTrue(
            result == [[20], [30], [40]] or
            result == [[30], [20], [40]] or
            result == [[40], [30], [20]]
        )

    def test_zero_energy_level(self):
        mgr = MarsRoverManager([0])
        mgr.add_task(10)
        self.assertEqual(mgr.assign_tasks(), [[]])

    def test_zero_energy_cost(self):
        mgr = MarsRoverManager([10])
        mgr.add_task(0)
        self.assertEqual(mgr.assign_tasks(), [[0]])

    def test_all_rovers_same_energy(self):
        mgr = MarsRoverManager([20, 20, 20])
        mgr.add_task(10)
        mgr.add_task(5)
        mgr.add_task(15)
        result = mgr.assign_tasks()
        # Check if all rovers got one task
        self.assertTrue(all(len(tasks) == 1 for tasks in result))

    def test_unassignable_tasks(self):
        mgr = MarsRoverManager([10, 15])
        mgr.add_task(20)
        mgr.add_task(5)
        self.assertIsNone(mgr.assign_tasks())

    def test_no_tasks_can_be_assigned(self):
        mgr = MarsRoverManager([5, 6])
        mgr.add_task(10)
        mgr.add_task(12)
        self.assertIsNone(mgr.assign_tasks())

if __name__ == '__main__':
    unittest.main()
