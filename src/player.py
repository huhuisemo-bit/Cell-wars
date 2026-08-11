# player.py

class Player:
    def __init__(self, name, race):

        self.name = name
        self.race = race

        self.atp = 5

        self.hand = []

        self.structures = []

        self.has_synthesized_this_turn = False
    def draw(self, deck):
        if deck:
            self.hand.append(deck.pop())

    def gain_atp(self, amount):
        self.atp += amount

    def spend_atp(self, amount):
        if self.atp >= amount:
            self.atp -= amount
            return True
        return False
    
