import unittest
from alien_encounters import resize_matrix

class TestAlienEncounters(unittest.TestCase):
    def test_resize_matrix_removes_rows(self):
        matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        length = 2
        expected = [[1, 2, 3], [4, 5, 6]]
        self.assertEqual(resize_matrix(matrix, length), expected)

    def test_resize_matrix_adds_rows(self):
        matrix = [[1, 2, 3], [4, 5, 6]]
        length = 3
        expected = [[1, 2, 3], [4, 5, 6], [0, 0, 0]]
        self.assertEqual(resize_matrix(matrix, length), expected)

    def test_resize_matrix_does_not_modify_original(self):
        matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        length = 2
        original = matrix.copy()
        resize_matrix(matrix, length)
        self.assertEqual(matrix, original)

    def test_resize_matrix_handles_empty_matrix(self):
        matrix = []
        length = 3
        expected = [[0], [0], [0]]
        self.assertEqual(resize_matrix(matrix, length), expected)

if __name__ == '__main__':
    unittest.main()