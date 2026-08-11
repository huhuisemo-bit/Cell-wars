class Card:

    def __init__(self, zh_name, en_name, ctype, value=0):

        self.zh_name = zh_name
        self.en_name = en_name
        self.type = ctype
        self.value = value

    def display_name(self):
        return f"{self.zh_name} ({self.en_name})"

    def __repr__(self):
        return self.display_name()