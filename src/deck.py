# deck.py

import random
from card import Card


SIMPLE_CARDS = [
    (8, "葡萄糖", "Glucose", "resource"),
    (6, "氧氣", "Oxygen", "resource"),
    (4, "二氧化碳", "Carbon Dioxide", "resource"),
    (3, "水", "Water", "resource"),
    (5, "線粒體", "Mitochondria", "structure"),
    (5, "葉綠體", "Chloroplast", "structure"),
    (5, "ATP竊取", "ATP Theft", "action"),
]

NORMAL_CARDS = [
    (9, "葡萄糖", "Glucose", "resource"),
    (7, "氧氣", "Oxygen", "resource"),
    (6, "二氧化碳", "Carbon Dioxide", "resource"),
    (6, "水", "Water", "resource"),
    (5, "光能", "Light Energy", "resource"),
    (4, "粒線體", "Mitochondria", "structure"),
    (4, "葉綠體", "Chloroplast", "structure"),
    (4, "核糖體", "Ribosome", "structure"),
    (4, "細胞膜", "Cell Membrane", "structure"),
    (4, "細胞壁", "Cell Wall", "structure"),
    (3, "溶體", "Lysosome", "structure"),
    (5, "ATP竊取", "ATP Theft", "action"),
    (3, "病毒", "Virus", "action"),
    (4, "修復", "Repair", "defense"),
    (3, "免疫反應", "Immune Response", "defense"),
    (3, "缺氧", "Hypoxia", "environment"),
    (3, "日照", "Sunlight", "environment"),
    (3, "夜晚", "Night", "environment"),
]


def create_card(en_name, difficulty="普通"):
    card_pool = SIMPLE_CARDS if difficulty == "簡單" else NORMAL_CARDS
    for _count, zh_name, card_en_name, ctype in card_pool:
        if card_en_name == en_name:
            return Card(zh_name, card_en_name, ctype)
    return None


def create_deck(difficulty="普通"):
    deck = []
    card_pool = SIMPLE_CARDS if difficulty == "簡單" else NORMAL_CARDS
    for count, zh_name, en_name, ctype in card_pool:
        for _ in range(count):
            deck.append(Card(zh_name, en_name, ctype))
    random.shuffle(deck)
    return deck
