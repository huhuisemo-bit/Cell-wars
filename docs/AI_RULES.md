# Cell Wars AI 開發規範

## 語言
Python 3

## 引擎
Pygame

## UI
- 中文介面
- 專有名詞中英雙語

## 開發原則
- Game 是唯一管理遊戲狀態的類別
- ReactionEngine 只判斷反應，不直接修改玩家狀態
- UI 不直接修改 Player
- 新功能需保持 Hot Seat、Battle Log、Victory System 相容