import unittest

from benchmark.exercises.messaging_system.messaging_system_solution import MessagingSystem


class TestMessagingSystem(unittest.TestCase):

    def setUp(self):
        self.sys = MessagingSystem()

    def test_user_registration_and_login(self):
        self.assertTrue(self.sys.register_user("Alice", "password"))
        self.assertTrue(self.sys.login("Alice", "password"))

    def test_input_length_constraint(self):
        long_string = "a" * 101
        self.assertFalse(self.sys.register_user(long_string, "password"))

    def test_login_without_registration(self):
        self.assertFalse(self.sys.login("Bob", "password"))

    def test_create_and_join_room(self):
        self.sys.register_user("Alice", "password")
        self.sys.login("Alice", "password")

        self.assertTrue(self.sys.create_room("general"))
        self.assertTrue(self.sys.join_room("Alice", "general"))

    def test_join_room_without_login(self):
        self.sys.register_user("Alice", "password")
        self.assertFalse(self.sys.join_room("Alice", "general"))

    def test_send_and_receive_message(self):
        self.sys.register_user("Alice", "password")
        self.sys.login("Alice", "password")
        self.sys.create_room("general")
        self.sys.join_room("Alice", "general")

        self.assertTrue(self.sys.send_message("Alice", "general", "Hi everyone!"))
        self.assertEqual(self.sys.get_messages("general"), [("Alice", "Hi everyone!")])

    def test_send_message_without_login(self):
        self.sys.register_user("Alice", "password")
        self.assertFalse(self.sys.send_message("Alice", "general", "Hi everyone!"))

    def test_create_duplicate_room(self):
        self.sys.register_user("Alice", "password")
        self.sys.login("Alice", "password")
        self.assertTrue(self.sys.create_room("general"))
        self.assertFalse(self.sys.create_room("general"))

    def test_user_in_multiple_rooms(self):
        self.sys.register_user("Alice", "password")
        self.sys.login("Alice", "password")
        self.assertTrue(self.sys.create_room("general"))
        self.assertTrue(self.sys.create_room("random"))

        self.assertTrue(self.sys.join_room("Alice", "general"))
        self.assertTrue(self.sys.join_room("Alice", "random"))

        self.assertTrue(self.sys.send_message("Alice", "general", "Hi general!"))
        self.assertTrue(self.sys.send_message("Alice", "random", "Hi random!"))

        self.assertEqual(self.sys.get_messages("general"), [("Alice", "Hi general!")])
        self.assertEqual(self.sys.get_messages("random"), [("Alice", "Hi random!")])

if __name__ == '__main__':
    unittest.main()
