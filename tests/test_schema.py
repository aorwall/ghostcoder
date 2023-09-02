from ghostcoder.schema import Message, TextItem, FileItem, UpdatedFileItem, Stats


def test_message_to_string():

    human_msg = Message(sender="Human", items=[
        FileItem(file_path="src/main/java/com/example/demo/DemoApplication.java", language="java", content="System.out.println(\"Hello World\");"),
        TextItem(text="Update the file")]
    )
    ai_message = Message(sender="AI", items=[
        TextItem(text="Hello I updated the file"),
        FileItem(file_path="src/main/java/com/example/demo/DemoApplication.java", language="java", content="System.out.println(\"Updated\")", diff="@@ -1,3 +1,3 @@\n-System.out.println(\"Hello World\");\n+System.out.println(\"Updated\");")]
    )

    human_msg == """Filepath: src/main/java/com/example/demo/DemoApplication.java
```java
System.out.println("Hello World");
```
Update the file"""

    ai_message == """Hello I updated the file
Updated.
Filepath: src/main/java/com/example/demo/DemoApplication.java
```java
@@ -1,3 +1,3 @@
-System.out.println("Hello World");
+System.out.println("Updated");
```"""


def test_updated_file():
    item = UpdatedFileItem(file_path="path/to/updated_file", diff="+ updated file content", content="updated file content")
    assert item.dict() == {'type': 'updated_file', 'file_path': 'path/to/updated_file', 'content': 'updated file content', 'invalid': False, 'error': None, 'language': None, 'readonly': False}


def test_message():
    message = Message(
        sender="Human",
        items=[
            UpdatedFileItem(file_path="path/to/updated_file", diff="+ updated file content",
                            content="updated file content", information="foo"),
            TextItem(text="Hello, world!"),
            FileItem(file_path="path/to/file", content="file content", information="foo"),
        ],
        usage=[
            Stats(
                prompt="prompt",
                model_name="model_name",
                total_tokens=100,
                prompt_tokens=50,
                completion_tokens=50,
                duration=1,
            )
        ],
    )

    message_dict = message.dict()
    parsed_message = Message(**message_dict)
    assert parsed_message == message

