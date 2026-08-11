# Cell Wars

Cell Wars 是一款以細胞代謝與生化反應為核心的 Pygame 回合制卡牌遊戲。玩家操控不同生命類型，收集資源、建立胞器與結構，並在實驗室中組合卡牌產生 ATP。

## 專案結構

```text
CellWars/
├── assets/          # 圖片與其他資產
├── docs/            # 設計文件與開發筆記
├── src/             # 遊戲主要程式碼
├── tests/           # 可獨立執行的測試
├── dist/web/        # 已建置的 WebAssembly 網頁版
├── game.py          # 專案根目錄啟動檔
├── main.py          # pygbag Web 入口檔
├── requirements.txt
└── README.md
```

## 安裝

建議使用 Python 3.11 以上版本。

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows PowerShell 可改用：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 執行遊戲

在專案根目錄執行：

```bash
python3 game.py
```

Windows 也可使用：

```powershell
python game.py
```

## WebAssembly / 網頁版

本專案已使用 `pygbag` 建置網頁版，產物位於：

```text
dist/web/
├── index.html
├── cellwars_web_noto.apk
├── cellwars_web_noto.tar.gz
└── favicon.png
```

可用任一靜態伺服器啟動測試：

```bash
python3 -m http.server 8000 --directory dist/web
```

接著打開：

```text
http://localhost:8000/
```

重新建置 Web 版時，需要先安裝 pygbag：

```bash
python3 -m pip install pygbag
python3 -m pygbag --build .
```

若要產生單檔 HTML，可以使用：

```bash
python3 -m pygbag --build --html .
```

注意：單檔 HTML 會把中文字型一起嵌入，檔案可能超過 GitHub 單檔 100MB 限制；提交 GitHub 時建議使用目前的 `dist/web/index.html + .apk + .tar.gz` 形式。

## 字型

為避免網頁版缺少中文字型，專案內已放入開源 Noto CJK 字型：

```text
assets/fonts/NotoSansCJKtc-Regular.otf
```

遊戲會優先載入這個專案內字型，桌面版與 WebAssembly 版都會使用同一份字型。

## 基本操作

- 左鍵點擊手牌：加入或移出實驗室
- Enter：執行反應或打出可單獨使用的卡牌
- Shift：丟棄目前選取的卡牌
- X：查看目前選取手牌的卡牌說明
- 點擊牌堆：抽 1 張牌並跳過本回合
- Esc：關閉彈窗或離開遊戲

## 目前功能

- 玩家 A / 玩家 B 回合制對戰
- AI 對戰開關
- 簡單 / 普通 / 困難難度選擇
- 隨機種族
- 實驗室與反應預覽
- ATP 勝利系統
- 資源合成系統
- 卡牌圖鑑與遊戲說明
- 棄牌拿取與牌堆抽牌
- 結構保底抽牌機制

## 測試

目前沒有使用 pytest；測試檔可直接執行：

```bash
python3 tests/test_resource_synthesis.py
```

## 開發備註

正式程式碼位於 `src/`。根目錄的 `game.py` 只負責把 `src/` 加入 Python 路徑並啟動 `src/main.py`。
