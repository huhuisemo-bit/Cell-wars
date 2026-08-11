# game.py

import random

from card import Card
from deck import create_card, create_deck
from player import Player
from reaction_engine import ReactionEngine
from ui_text import card_name, race_name, reaction_name

SIMPLE_WIN_ATP = 30
NORMAL_WIN_ATP = 50
STARTING_HAND = 4
MAX_HAND_SIZE = 8
PHOTOSYNTHESIS_RACES = {"Plant Cell"}
STRUCTURE_PITY_TURNS = 3
ATP_THEFT_COST = 2
ATP_THEFT_AMOUNT = 1
RACES = ["Plant Cell", "Animal Cell", "Yeast", "Bacteria"]
SIMPLE_RACES = ["Plant Cell", "Animal Cell"]
NORMAL_RACES = ["Plant Cell", "Animal Cell", "Yeast", "Bacteria"]
SYNTHESIS_RESOURCES = ["Glucose", "Oxygen", "Water", "Carbon Dioxide", "Light Energy"]

CARD_DEFS = {
    "Glucose": ("葡萄糖", "resource"),
    "Oxygen": ("氧氣", "resource"),
    "Carbon Dioxide": ("二氧化碳", "resource"),
    "Water": ("水", "resource"),
    "Light Energy": ("光能", "resource"),
    "Mitochondria": ("粒線體", "structure"),
    "Chloroplast": ("葉綠體", "structure"),
    "Ribosome": ("核糖體", "structure"),
    "Cell Membrane": ("細胞膜", "structure"),
    "Cell Wall": ("細胞壁", "structure"),
    "Lysosome": ("溶體", "structure"),
}

RACE_STRUCTURES = {
    "Plant Cell": {"Chloroplast", "Mitochondria", "Ribosome", "Nucleus", "Vacuole", "Cell Membrane", "Cell Wall"},
    "Animal Cell": {"Mitochondria", "Ribosome", "Nucleus", "Lysosome", "Cell Membrane"},
    "Yeast": {"Mitochondria", "Ribosome", "Nucleus", "Vacuole", "Cell Membrane", "Cell Wall"},
    "Bacteria": {"Ribosome", "Cell Membrane", "Cell Wall", "Plasmid", "Flagellum"},
}


class Game:
    def __init__(self, ai_enabled=True, difficulty="普通"):
        self.ai_enabled = ai_enabled
        self.difficulty = difficulty
        self.reaction_engine = ReactionEngine(difficulty)
        self.win_atp = SIMPLE_WIN_ATP if difficulty == "簡單" else NORMAL_WIN_ATP
        self.deck = create_deck(difficulty)

        player_race, opponent_race = random.sample(self.available_races(), 2)
        self.player = Player("玩家Ａ", player_race)
        self.opponent = Player("玩家Ｂ", opponent_race)
        self.current_player = self.player

        self.turn = 1
        self.game_over = False
        self.winner = None
        self.messages = ["遊戲開始"]
        self.reaction_table = []
        self.preview = None
        self.waiting_for_deck_draw_after_discard = False
        self.discard_offer_card = None
        self.pending_discard_offer_card = None
        self.discard_pile = []
        self.waiting_to_discard_for_offer = False
        self.synthesis_mode = False
        self.synthesis_selected_cards = []
        self.synthesis_target = None
        self.structure_draw_misses = {}
        self.environment = None
        self.environment_turns = 0
        self.cell_barrier_used = {}
        self.respiration_bonus_used = {}
        self.repair_discount_used = {}
        self.lysosome_used = {}

        for _ in range(STARTING_HAND):
            self.player.draw(self.deck)
            self.opponent.draw(self.deck)

        self.initialize_race_traits()

        self.structure_draw_misses = {
            self.player: 0,
            self.opponent: 0,
        }

        self.add_log(f"玩家Ａ種族：{race_name(self.player.race)}")
        self.add_log(f"玩家Ｂ種族：{race_name(self.opponent.race)}")
        self.add_log("輪到玩家Ａ")

    def available_races(self):
        if self.difficulty == "簡單":
            return SIMPLE_RACES
        return NORMAL_RACES

    def initialize_race_traits(self):
        for player in (self.player, self.opponent):
            player.blocked_structures = set()
            player.blocked_structure_turns = {}
            player.immune_protection = False
            self.cell_barrier_used[player] = False
            self.respiration_bonus_used[player] = False
            self.repair_discount_used[player] = False
            self.lysosome_used[player] = False

        if self.difficulty != "簡單":
            if self.player.race == "Plant Cell":
                self.add_starting_structure(self.player, "Chloroplast")
            if self.opponent.race == "Plant Cell":
                self.add_starting_structure(self.opponent, "Chloroplast")
            if self.player.race == "Animal Cell":
                self.add_starting_structure(self.player, "Mitochondria")
            if self.opponent.race == "Animal Cell":
                self.add_starting_structure(self.opponent, "Mitochondria")

    def add_starting_structure(self, player, structure_name):
        if self.has_structure(player, structure_name):
            return
        zh_name, ctype = CARD_DEFS[structure_name]
        player.structures.append(Card(zh_name, structure_name, ctype))

    def make_card(self, en_name):
        card = create_card(en_name, self.difficulty)
        if card is not None:
            return card
        if en_name in CARD_DEFS:
            zh_name, ctype = CARD_DEFS[en_name]
            return Card(zh_name, en_name, ctype)
        return None

    @property
    def waiting_for_player(self):
        return not self.game_over and (self.current_player == self.player or not self.ai_enabled)

    @property
    def selected_cards(self):
        return self.reaction_table

    @selected_cards.setter
    def selected_cards(self, cards):
        self.reaction_table = list(cards)

    def opponent_of(self, player):
        return self.opponent if player == self.player else self.player

    def add_log(self, text):
        self.messages.append(text)
        if len(self.messages) > 10:
            self.messages.pop(0)

    def draw_cards(self, player, amount=1, use_structure_pity=False):
        drawn = 0
        for _ in range(amount):
            if len(player.hand) >= MAX_HAND_SIZE:
                self.add_log(f"{player.name} 手牌已滿")
                break

            force_structure = use_structure_pity and self.should_force_usable_structure_draw(player)
            card = self.draw_one_card(player, force_usable_structure=force_structure)
            if card is None:
                self.add_log("牌庫已空")
                break

            if use_structure_pity:
                self.record_structure_draw(player, card)
            drawn += 1
        return drawn

    def draw_one_card(self, player, force_usable_structure=False):
        if not self.deck:
            return None

        index = len(self.deck) - 1
        if force_usable_structure:
            forced_index = self.find_usable_structure_in_deck(player)
            if forced_index is not None:
                index = forced_index

        card = self.deck.pop(index)
        if self.environment and self.environment.en_name == "Hypoxia" and card.en_name == "Oxygen":
            card.hypoxia_usable = False
        player.hand.append(card)
        if force_usable_structure and card.type == "structure":
            self.add_log(f"{player.name} 保底抽到{card_name(card)}")
        return card

    def is_usable_structure_card(self, player, card):
        if card.type != "structure":
            return False
        if self.has_structure(player, card.en_name):
            return False
        return self.can_use_structure_card(player, card)

    def player_has_usable_structure_in_hand(self, player):
        return any(self.is_usable_structure_card(player, card) for card in player.hand)

    def find_usable_structure_in_deck(self, player):
        for index in range(len(self.deck) - 1, -1, -1):
            if self.is_usable_structure_card(player, self.deck[index]):
                return index
        return None

    def should_force_usable_structure_draw(self, player):
        if self.player_has_usable_structure_in_hand(player):
            self.structure_draw_misses[player] = 0
            return False
        if self.find_usable_structure_in_deck(player) is None:
            return False
        return self.structure_draw_misses.get(player, 0) >= STRUCTURE_PITY_TURNS - 1

    def record_structure_draw(self, player, card):
        if self.is_usable_structure_card(player, card):
            self.structure_draw_misses[player] = 0
            return

        if self.player_has_usable_structure_in_hand(player):
            self.structure_draw_misses[player] = 0
            return

        self.structure_draw_misses[player] = self.structure_draw_misses.get(player, 0) + 1

    def can_current_player_form_reaction(self):
        return bool(self.available_reactions(self.current_player))

    def available_reactions(self, player):
        return [
            reaction
            for reaction in self.reaction_engine.available_reactions(player)
            if self.is_reaction_allowed(reaction, player, log=False)
        ]

    def is_reaction_allowed(self, reaction, player, log=True):
        if self.difficulty != "簡單" and reaction.name.startswith("Photosynthesis") and self.environment and self.environment.en_name == "Night":
            if log:
                self.add_log("夜晚期間不能進行光合作用")
            return False
        if self.difficulty != "簡單" and reaction.name.startswith("Photosynthesis Light Substitutes"):
            if not self.environment or self.environment.en_name != "Sunlight":
                if log:
                    self.add_log("只有日照期間，光能才可代替水或二氧化碳")
                return False
        return True

    def current_player_hand_full(self):
        return len(self.current_player.hand) >= MAX_HAND_SIZE

    def current_player_needs_discard_before_draw(self):
        return self.current_player_hand_full() and not self.waiting_for_deck_draw_after_discard

    def has_discard_offer(self):
        return self.discard_offer_card is not None

    def selected_single_card(self):
        if len(self.reaction_table) == 1:
            return self.reaction_table[0]
        return None

    def can_single_play_card(self, card):
        return card is not None and card.type in {"structure", "action", "defense", "environment"}

    def has_structure(self, player, structure_name):
        return any(card.en_name == structure_name for card in player.structures)

    def has_active_structure(self, player, structure_name):
        blocked = set(getattr(player, "blocked_structures", set()))
        return structure_name not in blocked and self.has_structure(player, structure_name)

    def can_use_structure_card(self, player, card):
        if self.difficulty != "簡單" and card.en_name not in RACE_STRUCTURES.get(player.race, set()):
            return False
        if card.en_name == "Chloroplast" and player.race not in PHOTOSYNTHESIS_RACES:
            return False
        return True

    def structure_reject_reason(self, player, card):
        if self.difficulty != "簡單" and card.en_name not in RACE_STRUCTURES.get(player.race, set()):
            return f"{race_name(player.race)}無法使用{card_name(card)}"
        if card.en_name == "Chloroplast" and player.race not in PHOTOSYNTHESIS_RACES:
            return "此種族無法使用葉綠體"
        return None

    def discard_card(self, player, card, reason):
        if card in player.hand:
            player.hand.remove(card)
        self.pending_discard_offer_card = card
        self.add_log(f"{player.name} {reason}{card_name(card)}")

    def decline_discard_offer(self):
        if not self.discard_offer_card:
            return False
        card = self.discard_offer_card
        self.deck.insert(0, card)
        self.discard_offer_card = None
        self.waiting_to_discard_for_offer = False
        self.add_log(f"未拿取{card_name(card)}，放回牌堆")
        return True

    def take_discard_offer(self):
        if not self.discard_offer_card:
            self.add_log("目前沒有可拿取的棄牌")
            return False

        if self.current_player_hand_full():
            self.waiting_to_discard_for_offer = True
            self.add_log("手牌已滿：選 1 張按 Shift 丟棄後拿取棄牌")
            return False

        card = self.discard_offer_card
        self.current_player.hand.append(card)
        self.discard_offer_card = None
        self.waiting_to_discard_for_offer = False
        self.add_log(f"{self.current_player.name} 拿走棄牌{card_name(card)}")
        return True

    def discard_selected_card_for_offer(self):
        if self.game_over or len(self.reaction_table) != 1:
            self.add_log("請選擇 1 張要丟棄的卡牌")
            return False
        if not self.discard_offer_card:
            self.waiting_to_discard_for_offer = False
            return False

        offered_card = self.discard_offer_card
        card = self.reaction_table[0]
        self.discard_card(self.current_player, card, "丟棄")
        self.clear_reaction_table()

        self.current_player.hand.append(offered_card)
        self.discard_offer_card = None
        self.waiting_to_discard_for_offer = False
        self.add_log(f"{self.current_player.name} 拿走棄牌{card_name(offered_card)}")
        return True

    def draw_from_deck_and_pass(self):
        if self.game_over:
            return False

        if self.waiting_to_discard_for_offer:
            self.add_log("請先選 1 張按 Shift 丟棄後拿取棄牌")
            return False

        self.decline_discard_offer()

        if self.waiting_for_deck_draw_after_discard:
            drawn = self.draw_cards(self.current_player, 1)
            if drawn:
                self.add_log(f"{self.current_player.name} 補抽 1 張牌並結束回合")
            else:
                self.add_log(f"{self.current_player.name} 無法補抽，結束回合")
            self.waiting_for_deck_draw_after_discard = False
            self.end_turn(draw_start_card=False)
            return True

        if self.current_player_hand_full():
            self.add_log("手牌已滿：選 1 張牌按 Shift 丟棄")
            return False

        if self.difficulty == "簡單" and self.can_current_player_form_reaction():
            self.add_log("目前手牌可形成反應，不能抽牌跳過")
            return False

        drawn = self.draw_cards(self.current_player, 1)
        if drawn:
            self.add_log(f"{self.current_player.name} 抽 1 張牌並結束回合")
        else:
            self.add_log(f"{self.current_player.name} 無法抽牌，結束回合")
        self.end_turn(draw_start_card=False)
        return True

    def start_turn(self, player, draw_start_card=True):
        self.current_player = player
        self.clear_reaction_table()
        self.cancel_synthesis()
        self.preview = None
        self.waiting_for_deck_draw_after_discard = False
        self.waiting_to_discard_for_offer = False
        self.discard_offer_card = self.pending_discard_offer_card
        self.pending_discard_offer_card = None
        self.cell_barrier_used[player] = False
        self.respiration_bonus_used[player] = False
        self.repair_discount_used[player] = False
        player.has_synthesized_this_turn = False
        player.immune_protection = False
        self.add_log(f"輪到{player.name}")
        if draw_start_card:
            self.draw_cards(player, 1, use_structure_pity=True)
        if self.difficulty != "簡單" and player.race == "Bacteria" and len(player.hand) < 4:
            if self.draw_cards(player, 1):
                self.add_log(f"{player.name} 細菌特性：手牌少於 4 張，額外抽 1 張")
        self.try_auto_lysosome_cleanup(player)

    def end_turn(self, draw_start_card=True):
        if self.game_over:
            return
        self.tick_player_blocks(self.current_player)
        self.tick_environment()
        self.turn += 1
        self.start_turn(self.opponent_of(self.current_player), draw_start_card=draw_start_card)

    def tick_environment(self):
        if not self.environment:
            return
        self.environment_turns -= 1
        if self.environment_turns <= 0:
            self.add_log(f"{self.environment.zh_name}環境結束")
            self.environment = None

    def tick_player_blocks(self, player):
        blocked_turns = getattr(player, "blocked_structure_turns", {})
        if not blocked_turns:
            return
        expired = []
        for name in list(blocked_turns):
            blocked_turns[name] -= 1
            if blocked_turns[name] <= 0:
                expired.append(name)
        for name in expired:
            del blocked_turns[name]
            player.blocked_structures.discard(name)
            self.add_log(f"{player.name} 的{CARD_DEFS.get(name, (name,))[0]}封鎖解除")

    def try_auto_lysosome_cleanup(self, player):
        if player.race != "Animal Cell" or self.lysosome_used.get(player):
            return
        if not self.has_active_structure(player, "Lysosome"):
            return
        blocked = list(getattr(player, "blocked_structures", set()))
        if not blocked:
            return
        name = blocked[0]
        player.blocked_structures.discard(name)
        getattr(player, "blocked_structure_turns", {}).pop(name, None)
        self.lysosome_used[player] = True
        self.add_log(f"{player.name} 使用溶體解除{CARD_DEFS.get(name, (name,))[0]}封鎖")

    def select_card(self, index):
        if self.game_over or index < 0 or index >= len(self.current_player.hand):
            return
        if self.waiting_for_deck_draw_after_discard:
            self.add_log("請先點擊牌堆補抽 1 張")
            return
        if self.discard_offer_card and not self.waiting_to_discard_for_offer:
            self.decline_discard_offer()

        card = self.current_player.hand[index]
        if card in self.reaction_table:
            self.reaction_table.remove(card)
        else:
            self.reaction_table.append(card)

        self.preview_reaction()

    def enter_synthesis_mode(self):
        if not self.waiting_for_player:
            self.add_log("目前不是可操作玩家的回合")
            return False
        if self.difficulty == "簡單":
            self.add_log("資源合成只在普通模式可用")
            return False
        if self.current_player.has_synthesized_this_turn:
            self.add_log("本回合已進行過資源合成")
            return False
        if self.waiting_for_deck_draw_after_discard:
            self.add_log("請先點擊牌堆補抽 1 張")
            return False
        if self.waiting_to_discard_for_offer:
            self.add_log("請先完成棄牌拿取")
            return False
        self.synthesis_mode = True
        self.synthesis_selected_cards = []
        self.synthesis_target = None
        self.add_log("資源合成：請選擇 2 張資源牌")
        return True

    def cancel_synthesis(self):
        self.synthesis_mode = False
        self.synthesis_selected_cards = []
        self.synthesis_target = None

    def select_synthesis_card(self, index):
        if not self.synthesis_mode or index < 0 or index >= len(self.current_player.hand):
            return False
        card = self.current_player.hand[index]
        if card in self.synthesis_selected_cards:
            self.synthesis_selected_cards.remove(card)
            self.synthesis_target = None
            return True
        if card.type != "resource":
            self.add_log("只能選擇資源牌作為合成材料")
            return False
        if len(self.synthesis_selected_cards) >= 2:
            self.add_log("資源合成只能選擇 2 張材料")
            return False
        self.synthesis_selected_cards.append(card)
        self.synthesis_target = None
        return True

    def set_synthesis_target(self, target_resource_name):
        if target_resource_name not in SYNTHESIS_RESOURCES:
            self.add_log("目標資源不合法")
            return False
        self.synthesis_target = target_resource_name
        return True

    def can_synthesize(self, player, selected_cards):
        if self.game_over:
            return False, "遊戲已結束"
        if player != self.current_player:
            return False, "只能由目前回合玩家進行資源合成"
        if not self.waiting_for_player:
            return False, "目前不是可操作玩家的回合"
        if self.difficulty == "簡單":
            return False, "資源合成只在普通模式可用"
        if player.has_synthesized_this_turn:
            return False, "本回合已進行過資源合成"
        if len(selected_cards) != 2:
            return False, "資源合成必須剛好選擇 2 張材料"
        if len({id(card) for card in selected_cards}) != 2:
            return False, "資源合成必須選擇 2 張不同卡牌"
        for card in selected_cards:
            if card not in player.hand:
                return False, "選取的材料不在目前手牌中"
            if card.type != "resource":
                return False, "只能選擇資源牌作為合成材料"
        return True, ""

    def synthesize_resource(self, player, selected_cards, target_resource_name):
        allowed, reason = self.can_synthesize(player, selected_cards)
        if not allowed:
            self.add_log(reason)
            return False
        if target_resource_name not in SYNTHESIS_RESOURCES:
            self.add_log("目標資源不合法")
            return False

        new_card = self.make_card(target_resource_name)
        if new_card is None:
            self.add_log("無法建立目標資源牌")
            return False

        material_cards = list(selected_cards)
        for card in material_cards:
            player.hand.remove(card)
            self.discard_pile.append(card)
            if card in self.reaction_table:
                self.reaction_table.remove(card)
        player.hand.append(new_card)
        player.has_synthesized_this_turn = True
        material_names = " 與 ".join(card_name(card) for card in material_cards)
        self.add_log(f"{player.name} 消耗了{material_names}，合成{card_name(new_card)}")
        self.preview_reaction()
        self.cancel_synthesis()
        return True

    def discard_selected_card_for_draw(self):
        if self.game_over or len(self.reaction_table) != 1:
            self.add_log("請選擇 1 張要丟棄的卡牌")
            return False

        if not self.current_player_hand_full():
            self.add_log("手牌未滿，不需要丟棄補抽")
            return False

        card = self.reaction_table[0]
        self.discard_card(self.current_player, card, "丟棄")
        self.clear_reaction_table()
        self.waiting_for_deck_draw_after_discard = True
        return True

    def discard_selected_card(self):
        if self.game_over or len(self.reaction_table) != 1:
            self.add_log("請選擇 1 張要丟棄的卡牌")
            return False

        if self.waiting_to_discard_for_offer:
            return self.discard_selected_card_for_offer()

        if self.current_player_hand_full():
            return self.discard_selected_card_for_draw()

        self.decline_discard_offer()
        card = self.reaction_table[0]
        self.discard_card(self.current_player, card, "丟棄")
        self.clear_reaction_table()
        self.end_turn()
        return True

    def play_single_card(self, card):
        if self.game_over or card not in self.current_player.hand:
            return False
        self.decline_discard_offer()

        if card.type == "structure":
            if self.has_structure(self.current_player, card.en_name):
                self.add_log(f"已擁有{card_name(card)}，請按 Shift 丟棄")
                return False

            reject_reason = self.structure_reject_reason(self.current_player, card)
            if reject_reason:
                self.add_log(reject_reason)
                return False

            self.current_player.hand.remove(card)
            self.current_player.structures.append(card)
            self.add_log(f"{self.current_player.name} 打出{card_name(card)}")
            self.clear_reaction_table()
            self.end_turn()
            return True

        if card.type == "environment":
            return self.play_environment_card(card)

        if card.en_name == "ATP Theft":
            return self.play_atp_theft(card)

        if card.en_name == "Virus":
            return self.play_virus(card)

        if card.en_name in {"Repair", "Immune Response"}:
            return self.play_defense_card(card)

        return False

    def play_environment_card(self, card):
        self.current_player.hand.remove(card)
        if self.environment:
            self.add_log(f"{card_name(card)}取代{card_name(self.environment)}")
        self.environment = card
        self.environment_turns = 4
        if card.en_name == "Hypoxia":
            for player in (self.player, self.opponent):
                for hand_card in player.hand:
                    if hand_card.en_name == "Oxygen":
                        hand_card.hypoxia_usable = True
        self.add_log(f"環境變為{card_name(card)}，持續 2 個完整輪次")
        self.clear_reaction_table()
        self.end_turn()
        return True

    def play_atp_theft(self, card):
        if self.current_player.atp < ATP_THEFT_COST:
            self.add_log("ATP不足，無法使用ATP竊取")
            return False
        self.current_player.atp -= ATP_THEFT_COST
        self.current_player.hand.remove(card)
        target = self.opponent_of(self.current_player)
        stolen_amount = ATP_THEFT_AMOUNT
        if self.has_active_structure(target, "Cell Membrane") or self.has_active_structure(target, "Cell Wall"):
            if not self.cell_barrier_used.get(target):
                stolen_amount = max(0, stolen_amount - 1)
                self.cell_barrier_used[target] = True
        stolen = min(stolen_amount, target.atp)
        target.atp -= stolen
        self.current_player.gain_atp(stolen)
        self.add_log(f"{self.current_player.name} 使用ATP竊取，花費 {ATP_THEFT_COST} ATP，偷取 {stolen} ATP")
        self.clear_reaction_table()
        self.check_win()
        if not self.game_over:
            self.end_turn()
        return True

    def play_virus(self, card):
        if self.current_player.atp < ATP_THEFT_COST:
            self.add_log("ATP不足，無法使用病毒")
            return False
        target = self.opponent_of(self.current_player)
        if getattr(target, "immune_protection", False):
            self.current_player.atp -= ATP_THEFT_COST
            self.current_player.hand.remove(card)
            target.immune_protection = False
            self.add_log(f"{target.name} 的免疫保護抵消病毒")
            self.clear_reaction_table()
            self.end_turn()
            return True

        targetable = [structure for structure in target.structures if structure.en_name not in getattr(target, "blocked_structures", set())]
        if not targetable:
            self.add_log("對方沒有可封鎖的結構")
            return False
        self.current_player.atp -= ATP_THEFT_COST
        self.current_player.hand.remove(card)
        structure = targetable[0]
        duration = 2 if target.race == "Bacteria" else 1
        target.blocked_structures.add(structure.en_name)
        target.blocked_structure_turns[structure.en_name] = duration
        self.add_log(f"{self.current_player.name} 使用病毒封鎖{target.name}的{card_name(structure)}")
        self.clear_reaction_table()
        self.end_turn()
        return True

    def defense_cost(self, card):
        cost = 1
        if self.has_active_structure(self.current_player, "Ribosome") and not self.repair_discount_used.get(self.current_player):
            cost = 0
        return cost

    def play_defense_card(self, card):
        cost = self.defense_cost(card)
        if self.current_player.atp < cost:
            self.add_log(f"ATP不足，無法使用{card_name(card)}")
            return False
        blocked = list(getattr(self.current_player, "blocked_structures", set()))
        if card.en_name == "Repair" and not blocked:
            self.add_log("目前沒有可修復的封鎖")
            return False

        self.current_player.atp -= cost
        if cost == 0 and self.has_active_structure(self.current_player, "Ribosome"):
            self.repair_discount_used[self.current_player] = True
        self.current_player.hand.remove(card)

        if blocked:
            name = blocked[0]
            self.current_player.blocked_structures.discard(name)
            self.current_player.blocked_structure_turns.pop(name, None)
            self.add_log(f"{self.current_player.name} 使用{card_name(card)}解除{CARD_DEFS.get(name, (name,))[0]}封鎖")
        if card.en_name == "Immune Response":
            self.current_player.immune_protection = True
            self.add_log(f"{self.current_player.name} 獲得免疫保護")

        self.clear_reaction_table()
        self.end_turn()
        return True

    def clear_reaction_table(self):
        self.reaction_table = []
        self.preview = None

    def preview_reaction(self):
        self.preview = self.reaction_engine.find_reaction(
            self.reaction_table,
            self.current_player,
        )
        if self.preview:
            if self.is_reaction_allowed(self.preview, self.current_player):
                self.add_log(f"預覽：{reaction_name(self.preview)} +{self.reaction_atp_gain(self.preview, self.current_player, commit=False)} ATP")
            else:
                self.preview = None
        elif self.can_single_play_card(self.selected_single_card()):
            selected_card = self.selected_single_card()
            if selected_card.type == "structure" and self.has_structure(self.current_player, selected_card.en_name):
                self.add_log(f"重複結構：按 Shift 丟棄{card_name(selected_card)}")
            else:
                reject_reason = None
                if selected_card.type == "structure":
                    reject_reason = self.structure_reject_reason(self.current_player, selected_card)
                self.add_log(reject_reason or f"可單獨打出：{card_name(selected_card)}")
        elif self.reaction_table:
            self.add_log("尚未形成有效反應")
        return self.preview

    def resolve_reaction(self):
        if self.game_over or not self.reaction_table:
            return False
        if self.waiting_to_discard_for_offer:
            self.add_log("請按 Shift 丟棄選取卡牌")
            return False
        if self.waiting_for_deck_draw_after_discard:
            self.add_log("請先點擊牌堆補抽 1 張")
            return False

        self.decline_discard_offer()

        reaction = self.reaction_engine.find_reaction(
            self.reaction_table,
            self.current_player,
        )
        if reaction is None:
            selected_card = self.selected_single_card()
            if self.can_single_play_card(selected_card):
                return self.play_single_card(selected_card)
            if self.current_player_hand_full() and selected_card:
                self.add_log("手牌已滿，請按 Shift 丟棄選取卡牌")
                return False
            self.add_log("無法執行反應")
            return False

        if not self.is_reaction_allowed(reaction, self.current_player):
            return False
        if not self.is_hypoxia_oxygen_allowed(reaction):
            return False

        for card in list(self.reaction_table):
            if card.type == "structure":
                if card in self.current_player.hand and not self.has_structure(self.current_player, card.en_name):
                    self.current_player.hand.remove(card)
                    self.current_player.structures.append(card)
                    self.add_log(f"{self.current_player.name} 建立反應結構：{card_name(card)}")
                continue

            if card in self.current_player.hand:
                self.current_player.hand.remove(card)

        gained_atp = self.reaction_atp_gain(reaction, self.current_player, commit=True)
        self.current_player.gain_atp(gained_atp)
        self.add_product_cards(self.current_player, reaction.products)
        self.add_log(f"{self.current_player.name} 執行{reaction_name(reaction)} +{gained_atp} ATP")
        self.clear_reaction_table()
        self.preview = None
        self.check_win()
        if not self.game_over:
            self.end_turn()
        return True

    def is_hypoxia_oxygen_allowed(self, reaction):
        if self.difficulty == "簡單" or not self.environment or self.environment.en_name != "Hypoxia":
            return True
        if reaction.name not in {"Cellular Respiration", "Bacterial Respiration"}:
            return True
        oxygen_cards = [card for card in self.reaction_table if card.en_name == "Oxygen"]
        if not oxygen_cards:
            return True
        if any(getattr(card, "hypoxia_usable", False) for card in oxygen_cards):
            return True
        self.add_log("缺氧期間不能用新抽到的氧氣進行細胞呼吸")
        return False

    def reaction_atp_gain(self, reaction, player, commit=False):
        gained_atp = reaction.atp_gain
        if self.difficulty == "簡單":
            return gained_atp
        if reaction.name.startswith("Photosynthesis") and self.environment and self.environment.en_name == "Sunlight":
            gained_atp += 1
        if reaction.name == "Cellular Respiration" and player.race == "Animal Cell" and not self.respiration_bonus_used.get(player):
            gained_atp += 1
            if commit:
                self.respiration_bonus_used[player] = True
        if reaction.name == "Alcoholic Fermentation" and self.environment and self.environment.en_name == "Hypoxia":
            gained_atp += 1
        return gained_atp

    def add_product_cards(self, player, product_names):
        for product_name in product_names:
            if len(player.hand) >= MAX_HAND_SIZE:
                continue
            card = self.make_card(product_name)
            if card is None:
                continue
            player.hand.append(card)
            self.add_log(f"{player.name} 產生{card_name(card)}")

    def play_card(self, index):
        if self.game_over or index < 0 or index >= len(self.current_player.hand):
            return False
        self.decline_discard_offer()
        card = self.current_player.hand[index]
        if self.can_single_play_card(card):
            self.reaction_table = [card]
            return self.play_single_card(card)
        self.add_log("資源牌不單獨產生 ATP，必須透過有效反應打出")
        return False

    def ai_take_turn(self):
        if self.game_over or self.current_player != self.opponent:
            return

        self.add_log(f"{self.opponent.name} 思考中...")

        if self.discard_offer_card:
            if not self.current_player_hand_full():
                self.take_discard_offer()
            else:
                self.decline_discard_offer()

        # Try the strongest valid reaction available.
        for reaction in sorted(self.available_reactions(self.opponent), key=lambda item: item.atp_gain, reverse=True):
            indexes = []
            used = set()
            built_structures = {card.en_name for card in self.opponent.structures}
            needed_structures = [
                name
                for name in reaction.required_structures
                if name not in built_structures
            ]
            needed_cards = list(reaction.reactants) + needed_structures
            for reactant in needed_cards:
                for i, card in enumerate(self.opponent.hand):
                    if i not in used and card.en_name == reactant:
                        indexes.append(i)
                        used.add(i)
                        break
            if len(indexes) == len(needed_cards):
                self.selected_cards = [self.opponent.hand[i] for i in indexes]
                self.resolve_reaction()
                return

        if not self.game_over:
            structure_index = next((i for i, card in enumerate(self.opponent.hand) if card.type == "structure"), None)
            if structure_index is not None:
                if self.play_card(structure_index):
                    return

        if not self.game_over:
            attack_index = next((i for i, card in enumerate(self.opponent.hand) if card.en_name == "ATP Theft"), None)
            if attack_index is not None and self.player.atp > 0:
                if self.play_card(attack_index):
                    return

        if not self.game_over:
            if self.current_player_hand_full():
                self.discard_card(self.opponent, self.opponent.hand[0], "丟棄")
                self.waiting_for_deck_draw_after_discard = True
            self.draw_from_deck_and_pass()

    def check_win(self):
        if self.game_over:
            return

        if self.player.atp >= self.win_atp:
            self.game_over = True
            self.winner = self.player.name
            self.add_log(f"{self.player.name} 達到 {self.win_atp} ATP！")
        elif self.opponent.atp >= self.win_atp:
            self.game_over = True
            self.winner = self.opponent.name
            self.add_log(f"{self.opponent.name} 達到 {self.win_atp} ATP！")
