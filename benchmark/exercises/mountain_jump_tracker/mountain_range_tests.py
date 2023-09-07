import unittest

from benchmark.exercises.mountain_jump_tracker.examples.mountain_range import MountainRange


class TestMountainRange(unittest.TestCase):
    def test_mission_possible(self):
        mr = MountainRange([1, 2, 3, 4], 10)
        self.assertTrue(mr.can_complete_mission())

    def test_mission_impossible_due_to_jump_limit(self):
        mr = MountainRange([1, 100, 1], 50)
        self.assertFalse(mr.can_complete_mission())

    def test_mission_impossible_due_to_insufficient_jumps(self):
        mr = MountainRange([1, 5, 1, 5, 1], 5)
        self.assertFalse(mr.can_complete_mission())


if __name__ == '__main__':
    unittest.main()
