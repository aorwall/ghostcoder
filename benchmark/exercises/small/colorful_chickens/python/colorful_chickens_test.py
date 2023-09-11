import unittest
from colorful_chickens import chicken_color_group

class TestChickenColorGroup(unittest.TestCase):
    def test_red_group(self):
        self.assertEqual(chicken_color_group('apple'), 'Red Group')
        self.assertEqual(chicken_color_group('rose'), 'Red Group')
        self.assertEqual(chicken_color_group('tomato'), 'Red Group')

    def test_green_group(self):
        self.assertEqual(chicken_color_group('leaf'), 'Green Group')
        self.assertEqual(chicken_color_group('grass'), 'Green Group')
        self.assertEqual(chicken_color_group('lime'), 'Green Group')

    def test_blue_group(self):
        self.assertEqual(chicken_color_group('sky'), 'Blue Group')
        self.assertEqual(chicken_color_group('ocean'), 'Blue Group')
        self.assertEqual(chicken_color_group('blueberry'), 'Blue Group')

    def test_invalid_color_description(self):
        self.assertEqual(chicken_color_group('banana'), 'Invalid color description')
        self.assertEqual(chicken_color_group('grape'), 'Invalid color description')

if __name__ == '__main__':
    unittest.main()