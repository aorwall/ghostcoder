# Instructions
Build a simplified real-time messaging system with support for user accounts and chat rooms. Your system should support the following operations:

* User registration
* User login/logout
* Creating a chat room
* Joining a chat room
* Leaving a chat room
* Sending a message to a chat room

Your class should expose the following methods:

* register_user(username, password): Register a new user.
* login(username, password): Log in as a user.
* logout(username): Log out the currently logged-in user.
* create_room(room_name): Create a new chat room.
* join_room(username, room_name): A user joins a chat room.
* leave_room(username, room_name): A user leaves a chat room.
* send_message(username, room_name, message): Send a message to a chat room.
* get_messages(room_name): Retrieve all messages in a chat room.

Constraints
* All inputs are strings and can have a maximum length of 100 characters.
* Do not use any third-party libraries.
* A user must be logged in to join a room, leave a room, or send a message.
* A user can be a part of multiple rooms but can't create a room with the same name.