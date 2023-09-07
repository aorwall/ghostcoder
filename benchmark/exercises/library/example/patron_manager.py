class PatronManager:
    def __init__(self):
        self.patrons = []

    def add_patron(self, name):
        if len(name) <= 100:
            self.patrons.append(name)

    def remove_patron(self, name):
        self.patrons = [patron for patron in self.patrons if patron != name]

    def get_patrons(self):
        return self.patrons
