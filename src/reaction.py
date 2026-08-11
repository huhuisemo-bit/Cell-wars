class Reaction:

    def __init__(
        self,
        name,
        reactants,
        products,
        atp_gain=0,
        required_structures=None,
        required_race=None,
        zh_name=None,
    ):

        self.name = name
        self.zh_name = zh_name or name

        self.reactants = reactants

        self.products = products

        self.atp_gain = atp_gain

        self.required_structures = required_structures or []

        self.required_race = required_race
