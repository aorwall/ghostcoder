class MessagingSystem:
    def __init__(self):
        self.users = {}  # {username: password}
        self.logged_in_users = set()  # {username}
        self.rooms = {}  # {room_name: set(usernames)}
        self.messages = {}  # {room_name: [(username, message)]}

    def check_length(self, *args):
        return all(len(arg) <= 100 for arg in args)

    def register_user(self, username, password):
        if not self.check_length(username, password):
            return False
        if username in self.users:
            return False
        self.users[username] = password
        return True

    def login(self, username, password):
        if not self.check_length(username, password):
            return False
        if username in self.logged_in_users:
            return False
        if username in self.users and self.users[username] == password:
            self.logged_in_users.add(username)
            return True
        return False

    def logout(self, username):
        if username not in self.logged_in_users:
            return False
        self.logged_in_users.remove(username)
        return True

    def create_room(self, room_name):
        if room_name in self.rooms:
            return False
        self.rooms[room_name] = set()
        self.messages[room_name] = []
        return True

    def join_room(self, username, room_name):
        if username not in self.logged_in_users or room_name not in self.rooms:
            return False
        self.rooms[room_name].add(username)
        return True

    def leave_room(self, username, room_name):
        if username not in self.logged_in_users or room_name not in self.rooms:
            return False
        if username not in self.rooms[room_name]:
            return False
        self.rooms[room_name].remove(username)
        return True

    def send_message(self, username, room_name, message):
        if username not in self.logged_in_users or room_name not in self.rooms:
            return False
        if username not in self.rooms[room_name]:
            return False
        self.messages[room_name].append((username, message))
        return True

    def get_messages(self, room_name):
        if room_name not in self.rooms:
            return None
        return self.messages[room_name]
