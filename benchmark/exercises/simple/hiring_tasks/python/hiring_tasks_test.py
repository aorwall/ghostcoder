import unittest
from hiring_tasks import arrange_servers

class TestArrangeServers(unittest.TestCase):
    def test_arrange_servers(self):
        servers = [(1000, 200), (2000, 400), (1500, 300), (500, 100)]
        power_capacity = 1000
        result = arrange_servers(servers, power_capacity)
        self.assertEqual(len(result), 2)
        self.assertEqual(sum([server[1] for row in result for server in row]), 1000)
        self.assertEqual(sum([server[0] for row in result for server in row]), 5000)

    def test_empty_servers(self):
        servers = []
        power_capacity = 1000
        result = arrange_servers(servers, power_capacity)
        self.assertEqual(result, [])

    def test_zero_power_capacity(self):
        servers = [(1000, 200), (2000, 400), (1500, 300), (500, 100)]
        power_capacity = 0
        result = arrange_servers(servers, power_capacity)
        self.assertEqual(result, [])

    def test_exceed_power_capacity(self):
        servers = [(10000, 20000), (20000, 40000)]
        power_capacity = 1000
        result = arrange_servers(servers, power_capacity)
        self.assertEqual(result, [])

    def test_power_capacity_equal_to_single_server(self):
        servers = [(1000, 200), (2000, 400), (1500, 300), (500, 100)]
        power_capacity = 200
        result = arrange_servers(servers, power_capacity)
        self.assertEqual(len(result), 1)
        self.assertEqual(sum([server[1] for row in result for server in row]), 200)
        self.assertEqual(sum([server[0] for row in result for server in row]), 1000)

    def test_power_capacity_less_than_least_power_server(self):
        servers = [(1000, 200), (2000, 400), (1500, 300), (500, 100)]
        power_capacity = 150
        result = arrange_servers(servers, power_capacity)
        self.assertEqual(result, [[(500, 100)]])

if __name__ == '__main__':
    unittest.main()