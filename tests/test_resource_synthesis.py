import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from deck import create_card
from game import Game


def make_cards(*names):
    return [create_card(name, "普通") for name in names]


def assert_can(game, player, cards):
    allowed, reason = game.can_synthesize(player, cards)
    assert allowed, reason


def test_successful_synthesis():
    game = Game(ai_enabled=False, difficulty="普通")
    player = game.current_player
    water, oxygen = make_cards("Water", "Oxygen")
    player.hand = [water, oxygen]

    assert_can(game, player, [water, oxygen])
    assert game.synthesize_resource(player, [water, oxygen], "Glucose")
    assert water not in player.hand
    assert oxygen not in player.hand
    assert [card.en_name for card in game.discard_pile[-2:]] == ["Water", "Oxygen"]
    assert any(card.en_name == "Glucose" for card in player.hand)
    assert player.has_synthesized_this_turn


def test_invalid_material_counts_and_types():
    game = Game(ai_enabled=False, difficulty="普通")
    player = game.current_player
    water, oxygen, carbon, theft = make_cards("Water", "Oxygen", "Carbon Dioxide", "ATP Theft")
    player.hand = [water, oxygen, carbon, theft]

    assert not game.can_synthesize(player, [water])[0]
    assert not game.can_synthesize(player, [water, oxygen, carbon])[0]
    assert not game.can_synthesize(player, [water, theft])[0]
    assert not game.can_synthesize(player, [water, water])[0]


def test_only_once_per_turn_and_resets_on_new_turn():
    game = Game(ai_enabled=False, difficulty="普通")
    player = game.current_player
    water, oxygen, carbon, light = make_cards("Water", "Oxygen", "Carbon Dioxide", "Light Energy")
    player.hand = [water, oxygen, carbon, light]

    assert game.synthesize_resource(player, [water, oxygen], "Glucose")
    assert not game.synthesize_resource(player, [carbon, light], "Water")

    game.end_turn(draw_start_card=False)
    game.end_turn(draw_start_card=False)
    assert not player.has_synthesized_this_turn


def test_cancel_keeps_hand_discard_and_reaction_table():
    game = Game(ai_enabled=False, difficulty="普通")
    player = game.current_player
    water, oxygen, glucose = make_cards("Water", "Oxygen", "Glucose")
    player.hand = [water, oxygen, glucose]
    game.reaction_table = [glucose]
    before_hand = list(player.hand)
    before_discard = list(game.discard_pile)

    assert game.enter_synthesis_mode()
    assert game.select_synthesis_card(0)
    assert game.select_synthesis_card(1)
    game.cancel_synthesis()

    assert player.hand == before_hand
    assert game.discard_pile == before_discard
    assert game.reaction_table == [glucose]
    assert not game.synthesis_selected_cards


def test_synthesis_does_not_clear_reaction_table():
    game = Game(ai_enabled=False, difficulty="普通")
    player = game.current_player
    water, oxygen, glucose, carbon = make_cards("Water", "Oxygen", "Glucose", "Carbon Dioxide")
    player.hand = [water, oxygen, glucose, carbon]
    game.reaction_table = [glucose, carbon]

    assert game.synthesize_resource(player, [water, oxygen], "Light Energy")
    assert game.reaction_table == [glucose, carbon]


def test_synthesis_removes_consumed_cards_from_reaction_table_only():
    game = Game(ai_enabled=False, difficulty="普通")
    player = game.current_player
    water, oxygen, glucose = make_cards("Water", "Oxygen", "Glucose")
    player.hand = [water, oxygen, glucose]
    game.reaction_table = [water, oxygen, glucose]

    assert game.synthesize_resource(player, [water, oxygen], "Light Energy")
    assert water not in game.reaction_table
    assert oxygen not in game.reaction_table
    assert game.reaction_table == [glucose]


def test_normal_mode_can_draw_and_pass_even_with_available_reaction():
    game = Game(ai_enabled=False, difficulty="普通")
    player = game.current_player
    glucose, oxygen = make_cards("Glucose", "Oxygen")
    player.structures = [create_card("Mitochondria", "普通")]
    player.hand = [glucose, oxygen]
    before_turn = game.turn

    assert game.can_current_player_form_reaction()
    assert game.draw_from_deck_and_pass()
    assert game.turn == before_turn + 1
    assert game.current_player != player


def test_simple_mode_still_blocks_draw_when_reaction_available():
    game = Game(ai_enabled=False, difficulty="簡單")
    player = game.current_player
    glucose = create_card("Glucose", "簡單")
    oxygen = create_card("Oxygen", "簡單")
    player.structures = [create_card("Mitochondria", "簡單")]
    player.hand = [glucose, oxygen]
    before_turn = game.turn

    assert game.can_current_player_form_reaction()
    assert not game.draw_from_deck_and_pass()
    assert game.turn == before_turn


def run_all():
    test_successful_synthesis()
    test_invalid_material_counts_and_types()
    test_only_once_per_turn_and_resets_on_new_turn()
    test_cancel_keeps_hand_discard_and_reaction_table()
    test_synthesis_does_not_clear_reaction_table()
    test_synthesis_removes_consumed_cards_from_reaction_table_only()
    test_normal_mode_can_draw_and_pass_even_with_available_reaction()
    test_simple_mode_still_blocks_draw_when_reaction_available()
    print("resource synthesis tests passed")


if __name__ == "__main__":
    run_all()
