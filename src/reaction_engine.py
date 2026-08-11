from reaction import Reaction
from collections import Counter

PHOTOSYNTHESIS_RACES = {"Plant Cell"}


class ReactionEngine:
    def __init__(self, difficulty="普通"):
        self.difficulty = difficulty
        self.reactions = []
        self.load_default_reactions()

    def find_reaction(self, selected_cards, player):
        selected_reactants = [
            card.en_name
            for card in selected_cards
            if card.type != "structure"
        ]
        selected_structures = {
            card.en_name
            for card in selected_cards
            if card.type == "structure"
        }

        for reaction in self.reactions:
            if sorted(selected_reactants) != sorted(reaction.reactants):
                continue

            if reaction.required_race and reaction.required_race != player.race:
                continue

            blocked_structures = set(getattr(player, "blocked_structures", set()))
            built_structures = {card.en_name for card in player.structures if card.en_name not in blocked_structures}
            available_structures = built_structures | selected_structures
            if "Chloroplast" in available_structures and player.race not in PHOTOSYNTHESIS_RACES:
                available_structures.remove("Chloroplast")
            if not set(reaction.required_structures).issubset(available_structures):
                continue

            return reaction

        return None

    def available_reactions(self, player):
        hand_names = Counter(card.en_name for card in player.hand)
        blocked_structures = set(getattr(player, "blocked_structures", set()))
        built_structures = {card.en_name for card in player.structures if card.en_name not in blocked_structures}
        hand_structures = {
            card.en_name
            for card in player.hand
            if card.type == "structure"
        }
        available_structures = built_structures | hand_structures
        if "Chloroplast" in available_structures and player.race not in PHOTOSYNTHESIS_RACES:
            available_structures.remove("Chloroplast")
        reactions = []

        for reaction in self.reactions:
            if reaction.required_race and reaction.required_race != player.race:
                continue

            reactants = Counter(reaction.reactants)
            if any(hand_names[name] < amount for name, amount in reactants.items()):
                continue

            if not set(reaction.required_structures).issubset(available_structures):
                continue

            reactions.append(reaction)

        return reactions

    def load_default_reactions(self):
        self.reactions.append(
            Reaction(
                name="Cellular Respiration",
                reactants=["Glucose", "Oxygen"],
                products=["Carbon Dioxide", "Water"],
                atp_gain=8,
                required_structures=["Mitochondria"],
                zh_name="細胞呼吸",
            )
        )

        photosynthesis_reactants = ["Carbon Dioxide", "Water"] if self.difficulty == "簡單" else ["Carbon Dioxide", "Water", "Light Energy"]
        self.reactions.append(
            Reaction(
                name="Photosynthesis",
                reactants=photosynthesis_reactants,
                products=["Glucose", "Oxygen"],
                atp_gain=5,
                required_structures=["Chloroplast"],
                required_race="Plant Cell",
                zh_name="光合作用",
            )
        )

        if self.difficulty == "簡單":
            return

        self.reactions.append(
            Reaction(
                name="Photosynthesis Light Substitutes CO2",
                reactants=["Water", "Light Energy", "Light Energy"],
                products=["Glucose", "Oxygen"],
                atp_gain=5,
                required_structures=["Chloroplast"],
                required_race="Plant Cell",
                zh_name="光合作用",
            )
        )

        self.reactions.append(
            Reaction(
                name="Photosynthesis Light Substitutes Water",
                reactants=["Carbon Dioxide", "Light Energy", "Light Energy"],
                products=["Glucose", "Oxygen"],
                atp_gain=5,
                required_structures=["Chloroplast"],
                required_race="Plant Cell",
                zh_name="光合作用",
            )
        )

        self.reactions.append(
            Reaction(
                name="Alcoholic Fermentation",
                reactants=["Glucose"],
                products=["Carbon Dioxide"],
                atp_gain=3,
                required_race="Yeast",
                zh_name="酒精發酵",
            )
        )

        self.reactions.append(
            Reaction(
                name="Bacterial Respiration",
                reactants=["Glucose", "Oxygen"],
                products=["Carbon Dioxide", "Water"],
                atp_gain=6,
                required_structures=["Cell Membrane"],
                required_race="Bacteria",
                zh_name="細菌膜上呼吸",
            )
        )

        self.reactions.append(
            Reaction(
                name="Glycolysis",
                reactants=["Glucose"],
                products=[],
                atp_gain=2,
                zh_name="簡化糖解作用",
            )
        )
