class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"({self.x}, {self.y})"


class WordSearch:
    def __init__(self, puzzle):
        self.puzzle = puzzle
        self.rows = len(puzzle)
        self.cols = len(puzzle[0])

    def search(self, word):
        result = []
        for row in range(self.rows):
            for col in range(self.cols):
                if self.puzzle[row][col] == word[0]:
                    start = Point(row, col)
                    path = [start]
                    found = self._find_word(word, 1, start, path)
                    if found:
                        result.append(path)
        return result

    def _find_word(self, word, index, point, path):
        if index == len(word):
            return True

        row, col = point.x, point.y
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        for dr, dc in directions:
            new_point = Point(row + dr, col + dc)
            if (
                self.is_valid(new_point)
                and self.puzzle[new_point.x][new_point.y] == word[index]
            ):
                path.append(new_point)
                if self._find_word(word, index + 1, new_point, path):
                    return True
                path.pop()
        return False

    def is_valid(self, point):
        return 0 <= point.x < self.rows and 0 <= point.y < self.cols