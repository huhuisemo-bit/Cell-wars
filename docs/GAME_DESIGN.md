# Cell Wars Game Design

## Goal

Players race to reach 30 ATP by playing resource cards, building cell structures, and resolving biochemical reactions.

## Core Loop

1. Start turn and draw one card.
2. Gain race-specific passive effects.
3. Play cards or select reactants.
4. Resolve a valid reaction for ATP.
5. End turn.

## Current Reactions

- Cellular Respiration: Glucose + Oxygen, requires Mitochondria, gains 8 ATP.
- Photosynthesis: CO2 + Water, requires Chloroplast and Plant Cell, gains 5 ATP.

## UI Principles

- UI reads state from `Game`.
- UI calls `Game` methods for actions.
- `ReactionEngine` only matches reactions; it does not mutate players.

# Cell Wars 遊戲規格

## 種族

Plant Cell

Animal Cell

Yeast

Bacteria

Virus

---

## ATP

所有行動都需要 ATP。

---

## Laboratory

玩家將卡牌放入 Laboratory。

Reaction Engine 判斷是否形成反應。

---

## 教育模式

長按卡牌

↓

顯示：

功能

反應式

用途

常見考點
