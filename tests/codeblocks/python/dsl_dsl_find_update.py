for item in data:
    # ...
    elif item[0] == EDGE:
        if len(item) != 3 or not isinstance(item[1], str) or not isinstance(item[2], str) or not isinstance(item[3], dict):
            raise ValueError("Edge is malformed")
        self.edges.append(Edge(item[1], item[2], item[3]))