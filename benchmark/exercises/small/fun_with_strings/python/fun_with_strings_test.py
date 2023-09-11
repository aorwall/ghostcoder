import unittest
from fun_with_strings import decode_string

class TestDecodeString(unittest.TestCase):
    def test_decode_string(self):
        self.assertEqual(decode_string('zulu Yankee XRAY whiskey VICTOR uniform TANGO sierra ROMEO quebec PAPA oscar NOVEMBER mike LIMA kilo JULIET india HOTEL golf FOXTROT echo DELTA charlie BRAVO alpha'), 'aBcDeFgHiJkLmNoPqRsTuVwXYz')
        self.assertEqual(decode_string('alpha BRAVO charlie DELTA echo FOXTROT golf HOTEL india JULIET kilo LIMA mike NOVEMBER oscar PAPA quebec ROMEO sierra TANGO uniform VICTOR whiskey XRAY yankee ZULU'), 'ZyXwVuTsRqPoNmLkJiHgFeDcBa')
        self.assertEqual(decode_string('alpha'), 'a')

    def test_decode_string_with_uppercase(self):
        self.assertEqual(decode_string('ALPHA BRAVO CHARLIE'), 'CBA')
        self.assertEqual(decode_string('ZULU'), 'Z')

    def test_decode_string_with_large_input(self):
        large_input = ' '.join(['alpha']*10**5)
        large_output = 'a'*10**5
        self.assertEqual(decode_string(large_input), large_output)

if __name__ == '__main__':
    unittest.main()