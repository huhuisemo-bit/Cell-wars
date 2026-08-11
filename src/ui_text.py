CARD_TYPE_LABELS = {
    "resource": "資源",
    "structure": "結構",
    "action": "行動",
    "defense": "防禦",
    "environment": "環境",
}

RACE_LABELS = {
    "Plant Cell": "植物細胞",
    "Animal Cell": "動物細胞",
    "Yeast": "酵母菌",
    "Bacteria": "細菌",
}

CHEMICAL_LABELS = {
    "Glucose": "葡萄糖",
    "Oxygen": "氧氣",
    "Carbon Dioxide": "二氧化碳",
    "Water": "水",
    "Light Energy": "光能",
    "Mitochondria": "線粒體",
    "Chloroplast": "葉綠體",
    "Ribosome": "核糖體",
    "Cell Membrane": "細胞膜",
    "Cell Wall": "細胞壁",
    "Lysosome": "溶體",
    "ATP Theft": "ATP竊取",
    "Virus": "病毒",
    "Repair": "修復",
    "Immune Response": "免疫反應",
    "Hypoxia": "缺氧",
    "Sunlight": "日照",
    "Night": "夜晚",
    "ATP": "ATP",
}


def card_name(card):
    return card.zh_name


def card_type_label(card):
    return CARD_TYPE_LABELS.get(card.type, card.type)


def card_list(cards, empty="無"):
    names = [card_name(card) for card in cards]
    return "、".join(names) if names else empty


def race_name(race):
    return RACE_LABELS.get(race, race)


def reaction_name(reaction):
    return getattr(reaction, "zh_name", reaction.name)


def reaction_formula(reaction):
    reactants = " + ".join(CHEMICAL_LABELS.get(name, name) for name in reaction.reactants)
    products = " + ".join(CHEMICAL_LABELS.get(name, name) for name in reaction.products)
    return f"{reactants} -> {products}"
