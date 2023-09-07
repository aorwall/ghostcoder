import unittest
from precision_cut import RawMaterial

class TestRawMaterial(unittest.TestCase):

    def setUp(self):
        self.material = RawMaterial(100, 100, 100)

    def test_initial_size(self):
        self.assertEqual(self.material.get_current_size(), (100, 100, 100))

    def test_max_initial_size(self):
        with self.assertRaises(ValueError):
            RawMaterial(10001, 10000, 10000)

    def test_precise_cut_valid(self):
        response = self.material.precise_cut(10, 10, 10)
        self.assertEqual(response, "Cut successful. New dimensions are: 90, 90, 90")

    def test_precise_cut_invalid(self):
        response = self.material.precise_cut(110, 110, 110)
        self.assertEqual(response, "Invalid cut. Dimensions of the cut must be smaller than the dimensions of the raw material.")

    def test_precise_cut_edge_case(self):
        response = self.material.precise_cut(100, 100, 100)
        self.assertEqual(response, "Invalid cut. Dimensions of the cut must be smaller than the dimensions of the raw material.")

    def test_get_current_size(self):
        self.material.precise_cut(10, 10, 10)
        size = self.material.get_current_size()
        self.assertEqual(size, (90, 90, 90))

    def test_get_volume(self):
        self.material.precise_cut(10, 10, 10)
        volume = self.material.get_volume()
        self.assertEqual(volume, 90*90*90)

if __name__ == '__main__':
    unittest.main()