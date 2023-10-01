
class WordSearch:
    # ... existing methods remain unchanged ...

    def search(self, word):
        result = []
        for row in range(self.rows):
            for col in range(self.cols):
                if self.puzzle[row][col] == word[0]:
                    start = Point(row, col)
                    path = [start]
                    found = self._find_word(word, 1, start, path)
                    if found:
                        result.append([point for point in path])
        return result or None

    # ... existing methods remain unchanged ...