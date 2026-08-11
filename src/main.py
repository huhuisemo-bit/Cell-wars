# =========================
# Cell Wars MVP
# main.py
# =========================

import asyncio
import os

import pygame

from card import Card
from card_sprite import CARD_WIDTH, CardSprite
from game import Game, SYNTHESIS_RESOURCES
from text_fit import draw_text_in_rect, draw_wrapped_text_in_rect, text_tokens, token_join, wrap_text
from ui_text import card_list, card_name, card_type_label, race_name, reaction_formula, reaction_name

SCREEN_SIZE = (1200, 800)
MIN_PAGE_FONT_SIZE = 26
BG = (246, 250, 255)
PANEL = (255, 255, 252)
PANEL_TINT = (242, 248, 255)
TEXT = (41, 55, 76)
MUTED = (91, 108, 132)
LINE = (199, 216, 237)
BLUE = (56, 111, 208)
BLUE_SOFT = (222, 235, 255)
GREEN = (36, 148, 82)
GREEN_SOFT = (232, 247, 235)
ACCENT = (30, 132, 86)
GOLD = (245, 184, 58)
WARN = (235, 91, 65)
CARD_BACK = (112, 157, 205)

DIFFICULTIES = ["簡單", "普通", "困難"]
CATALOG_TABS = [
    ("action", "行動牌", WARN),
    ("resource", "資源牌", GREEN),
    ("structure", "構造牌", GOLD),
    ("defense", "防禦牌", BLUE),
    ("environment", "環境牌", MUTED),
]
CATALOG_CARDS = [
    Card("葡萄糖", "Glucose", "resource"),
    Card("氧氣", "Oxygen", "resource"),
    Card("二氧化碳", "Carbon Dioxide", "resource"),
    Card("水", "Water", "resource"),
    Card("光能", "Light Energy", "resource"),
    Card("粒線體", "Mitochondria", "structure"),
    Card("葉綠體", "Chloroplast", "structure"),
    Card("核糖體", "Ribosome", "structure"),
    Card("細胞膜", "Cell Membrane", "structure"),
    Card("細胞壁", "Cell Wall", "structure"),
    Card("溶體", "Lysosome", "structure"),
    Card("ATP竊取", "ATP Theft", "action"),
    Card("病毒", "Virus", "action"),
    Card("修復", "Repair", "defense"),
    Card("免疫反應", "Immune Response", "defense"),
    Card("缺氧", "Hypoxia", "environment"),
    Card("日照", "Sunlight", "environment"),
    Card("夜晚", "Night", "environment"),
]

CARD_DETAIL_LINES = {
    "Glucose": [
        "卡牌名稱：葡萄糖 Glucose",
        "卡牌類型：資源 Resource",
        "細胞呼吸：C6H12O6 + 6O2 -> 6CO2 + 6H2O + 能量。條件：需有粒線體；細菌則需有細胞膜。消耗：葡萄糖 x1、氧氣 x1。可得：基礎 8 ATP。",
        "酒精發酵：C6H12O6 -> 2C2H5OH + 2CO2 + 能量。條件：酵母菌可直接進行。消耗：葡萄糖 x1。可得：3 ATP。",
        "簡化糖解作用：葡萄糖 -> 丙酮酸 + 少量 ATP。條件：任何生命類型皆可進行。消耗：葡萄糖 x1。可得：2 ATP。",
        "普通模式功能：最主要的能源資源，也是呼吸作用與發酵的核心材料。資源牌不單獨結算 ATP，只有反應完成時獲得該反應額定 ATP。",
    ],
    "Oxygen": [
        "卡牌名稱：氧氣 Oxygen",
        "卡牌類型：資源 Resource",
        "細胞呼吸：C6H12O6 + 6O2 -> 6CO2 + 6H2O + 能量。條件：需有粒線體；細菌則使用細胞膜。消耗：氧氣 x1、葡萄糖 x1。可得：基礎 8 ATP。",
        "光合作用產物：6CO2 + 6H2O -> C6H12O6 + 6O2。條件：需有葉綠體與光能。產生：氧氣 x1。",
        "普通模式功能：有氧呼吸的必要資源；缺氧環境下較難取得或無法使用。",
    ],
    "Carbon Dioxide": [
        "卡牌名稱：二氧化碳 Carbon Dioxide",
        "卡牌類型：資源 Resource",
        "光合作用：6CO2 + 6H2O + 光能 -> C6H12O6 + 6O2。條件：需有葉綠體。消耗：二氧化碳 x1、水 x1、光能 x1。產生：葡萄糖 x1、氧氣 x1。",
        "細胞呼吸產物：細胞呼吸完成後，產生二氧化碳 x1。",
        "酒精發酵產物：酒精發酵完成後，產生二氧化碳 x1。",
        "普通模式功能：植物細胞的重要原料，也可作為呼吸與發酵產物重新投入循環。",
    ],
    "Water": [
        "卡牌名稱：水 Water",
        "卡牌類型：資源 Resource",
        "光合作用：6CO2 + 6H2O + 光能 -> C6H12O6 + 6O2。條件：需有葉綠體。消耗：水 x1、二氧化碳 x1、光能 x1。產生：葡萄糖 x1、氧氣 x1。",
        "細胞呼吸產物：C6H12O6 + 6O2 -> 6CO2 + 6H2O + 能量。完成呼吸作用後產生水 x1。",
        "普通模式功能：光合作用的必要資源，也能作為部分防禦或修復卡的條件。",
    ],
    "Light Energy": [
        "卡牌名稱：光能 Light Energy",
        "卡牌類型：資源／條件 Resource",
        "光合作用：6CO2 + 6H2O + 光能 -> C6H12O6 + 6O2。條件：需有葉綠體。消耗：光能 x1、二氧化碳 x1、水 x1。產生：葡萄糖 x1、氧氣 x1。",
        "普通模式功能：光合作用的能量來源。夜晚期間不能使用，但已抽到的光能牌可保留。",
    ],
    "Mitochondria": [
        "卡牌名稱：粒線體 Mitochondria",
        "卡牌類型：胞器 Organelle",
        "解鎖細胞呼吸：葡萄糖 + 氧氣 -> 二氧化碳 + 水 + 8 ATP。",
        "動物細胞特色：每回合第一次細胞呼吸額外 +1 ATP。",
        "普通模式功能：打出後永久留在場上，不會因進行呼吸作用而消耗。植物、動物與酵母菌可使用；細菌不可使用。",
    ],
    "Chloroplast": [
        "卡牌名稱：葉綠體 Chloroplast",
        "卡牌類型：胞器 Organelle",
        "解鎖光合作用：二氧化碳 + 水 + 光能 -> 葡萄糖 + 氧氣。",
        "在日照環境下，光合作用額外獲得 1 ATP 的遊戲獎勵。",
        "普通模式功能：植物細胞可使用。打出後永久留在場上，不會被光合作用消耗。",
        "為避免誤解，光合作用的主要淨產物仍是葡萄糖與氧氣；額外 ATP 屬於遊戲平衡獎勵。",
    ],
    "Ribosome": [
        "卡牌名稱：核糖體 Ribosome",
        "卡牌類型：胞器／結構 Organelle & Structure",
        "簡化蛋白質合成：胺基酸 + ATP -> 蛋白質。普通模式暫時不放入胺基酸牌，因此不直接執行完整蛋白質合成。",
        "普通模式功能：每回合第一次打出「修復」或「免疫反應」時，成本減少 1 ATP。打出後永久留在場上。四種普通模式生命類型皆可使用。",
    ],
    "Cell Membrane": [
        "卡牌名稱：細胞膜 Cell Membrane",
        "卡牌類型：結構 Structure",
        "細菌膜上呼吸：葡萄糖 + 氧氣 -> 二氧化碳 + 水 + 6 ATP。條件：使用者為細菌。其他生命類型不以細胞膜取代粒線體進行有氧呼吸。",
        "普通模式功能：每回合第一次被偷取 ATP 時，減少被偷取量 1 點。細菌可利用細胞膜進行簡化呼吸作用。打出後永久留在場上。",
    ],
    "Cell Wall": [
        "卡牌名稱：細胞壁 Cell Wall",
        "卡牌類型：結構 Structure",
        "反應式：無直接化學反應。",
        "普通模式功能：植物細胞、酵母菌與細菌可使用。每回合第一次受到 ATP 竊取時，減少被偷取量 1 點。若同時具有細胞膜與細胞壁，仍最多只減少 1 點，避免完全免疫攻擊。",
    ],
    "Lysosome": [
        "卡牌名稱：溶體 Lysosome",
        "卡牌類型：胞器 Organelle",
        "反應式：無直接 ATP 反應；代表細胞內物質分解與回收。",
        "普通模式功能：僅動物細胞可使用。每局一次，可解除自己一個被病毒封鎖的胞器。使用能力後，溶體仍留在場上，但不能再次發動主動效果。",
    ],
    "ATP Theft": [
        "卡牌名稱：ATP 竊取 ATP Theft",
        "卡牌類型：攻擊 Attack",
        "反應式：無；屬於遊戲化資源干擾。",
        "普通模式效果：發動成本 2 ATP。選擇一名對手，偷取 1 ATP。",
        "若目標具有細胞膜或細胞壁，本次偷取量減少 1，最低為 0。使用後棄置。",
    ],
    "Virus": [
        "卡牌名稱：病毒 Virus",
        "卡牌類型：攻擊／感染 Attack",
        "反應式：無單一化學反應；代表病毒利用宿主細胞機制。",
        "普通模式效果：發動成本 2 ATP。選擇對手場上一個胞器或結構，該結構到目標玩家下一回合結束前無法參與反應。",
        "若目標是細菌，封鎖額外延長一個回合。可被「免疫反應」「修復」或溶體能力解除。",
    ],
    "Repair": [
        "卡牌名稱：修復 Repair",
        "卡牌類型：防禦 Defense",
        "反應式：無固定反應式；代表細胞修復與受損結構恢復。",
        "普通模式效果：發動成本 1 ATP。解除自己一個被封鎖的胞器／結構，或移除一個一般負面狀態。",
        "若場上具有核糖體，本回合第一次使用修復時成本降為 0 ATP。使用後棄置。",
    ],
    "Immune Response": [
        "卡牌名稱：免疫反應 Immune Response",
        "卡牌類型：防禦 Defense",
        "反應式：無單一反應式；代表辨識並清除感染源。",
        "普通模式效果：可在自己回合使用，解除既有病毒封鎖。使用後獲得「免疫保護」至下回合開始，同期間不能再次被病毒封鎖。",
        "若場上具有核糖體，發動成本減少 1 ATP。",
    ],
    "Hypoxia": [
        "卡牌名稱：缺氧 Hypoxia",
        "卡牌類型：全場環境 Environment",
        "反應式：無；改變氧氣供應與代謝路線。",
        "普通模式效果：持續 2 個完整輪次。期間不能以新抽到的氧氣牌進行細胞呼吸。原本已在手中的氧氣仍可使用一次。",
        "酒精發酵不受影響。酵母菌在缺氧期間每次發酵額外 +1 ATP。",
    ],
    "Sunlight": [
        "卡牌名稱：日照 Sunlight",
        "卡牌類型：全場環境 Environment",
        "強化光合作用：二氧化碳 + 水 + 光能 -> 葡萄糖 + 氧氣。",
        "普通模式效果：持續 2 個完整輪次。植物細胞每次光合作用額外獲得 1 ATP。",
        "光能牌可代替一次水牌或二氧化碳牌，但每次反應最多代替一張。夜晚出現時，日照立即被取代。",
    ],
    "Night": [
        "卡牌名稱：夜晚 Night",
        "卡牌類型：全場環境 Environment",
        "反應式：無直接反應；限制光能供應。",
        "普通模式效果：持續 2 個完整輪次。期間不能執行光合作用。植物細胞仍可利用葡萄糖與粒線體進行細胞呼吸。",
        "每名植物細胞玩家每回合可棄 1 張光能牌並重抽 1 張，避免完全卡手。日照出現時，夜晚立即被取代。",
    ],
}

CHINESE_FONT_PATHS = [
    "assets/fonts/NotoSansCJKtc-Regular.otf",
    "../assets/fonts/NotoSansCJKtc-Regular.otf",
    "assets/fonts/STHeiti-Medium.ttc",
    "../assets/fonts/STHeiti-Medium.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/STHeiti Light.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "C:/Windows/Fonts/msjh.ttc",
    "C:/Windows/Fonts/msyh.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
]


def load_font(size):
    src_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(src_dir)
    project_font = os.path.join(project_root, "assets", "fonts", "NotoSansCJKtc-Regular.otf")
    font_paths = [project_font, *CHINESE_FONT_PATHS]
    for path in font_paths:
        try:
            return pygame.font.Font(path, size)
        except FileNotFoundError:
            continue
        except pygame.error:
            continue
    return pygame.font.SysFont("arialunicode,notosanscjk,heiti,msjh", size)


def draw_shadowed_panel(screen, rect, fill=PANEL, border=LINE, radius=8):
    shadow = pygame.Surface((rect.width + 8, rect.height + 8), pygame.SRCALPHA)
    pygame.draw.rect(shadow, (44, 76, 120, 24), pygame.Rect(4, 5, rect.width, rect.height), border_radius=radius)
    screen.blit(shadow, (rect.x, rect.y))
    pygame.draw.rect(screen, fill, rect, border_radius=radius)
    pygame.draw.rect(screen, border, rect, 1, border_radius=radius)


def draw_flask_icon(screen, center, color, scale=1.0):
    cx, cy = center
    neck_w = int(10 * scale)
    neck_h = int(18 * scale)
    body_w = int(34 * scale)
    body_h = int(28 * scale)
    top_y = cy - int(24 * scale)
    pygame.draw.line(screen, color, (cx - neck_w // 2, top_y), (cx - neck_w // 2, top_y + neck_h), 3)
    pygame.draw.line(screen, color, (cx + neck_w // 2, top_y), (cx + neck_w // 2, top_y + neck_h), 3)
    pygame.draw.line(screen, color, (cx - neck_w, top_y), (cx + neck_w, top_y), 3)
    points = [
        (cx - neck_w // 2, top_y + neck_h),
        (cx - body_w // 2, top_y + neck_h + body_h),
        (cx + body_w // 2, top_y + neck_h + body_h),
        (cx + neck_w // 2, top_y + neck_h),
    ]
    pygame.draw.lines(screen, color, False, points, 3)
    pygame.draw.line(
        screen,
        color,
        (cx - int(body_w * 0.32), top_y + neck_h + int(body_h * 0.62)),
        (cx + int(body_w * 0.32), top_y + neck_h + int(body_h * 0.62)),
        3,
    )


def draw_leaf_icon(screen, center, color, scale=1.0):
    cx, cy = center
    pygame.draw.ellipse(screen, color, pygame.Rect(cx - int(7 * scale), cy - int(18 * scale), int(14 * scale), int(22 * scale)))
    pygame.draw.ellipse(screen, color, pygame.Rect(cx - int(22 * scale), cy - int(5 * scale), int(20 * scale), int(12 * scale)))
    pygame.draw.ellipse(screen, color, pygame.Rect(cx + int(2 * scale), cy - int(5 * scale), int(20 * scale), int(12 * scale)))
    pygame.draw.line(screen, color, (cx, cy - int(16 * scale)), (cx, cy + int(18 * scale)), 3)
    pygame.draw.line(screen, color, (cx, cy + int(2 * scale)), (cx - int(16 * scale), cy + int(12 * scale)), 3)
    pygame.draw.line(screen, color, (cx, cy + int(2 * scale)), (cx + int(16 * scale), cy + int(12 * scale)), 3)


def draw_dot_icon(screen, center, color, scale=1.0):
    pygame.draw.circle(screen, color, center, int(12 * scale))


def draw_panel(screen, rect, title, font, body_lines, accent=BLUE):
    draw_shadowed_panel(screen, rect)
    header_rect = pygame.Rect(rect.x, rect.y, rect.width, 42)
    pygame.draw.rect(screen, PANEL_TINT, header_rect, border_top_left_radius=8, border_top_right_radius=8)
    pygame.draw.line(screen, LINE, (rect.x, rect.y + 42), (rect.right, rect.y + 42), 1)
    draw_wrapped_text_in_rect(
        screen,
        title,
        pygame.Rect(rect.x + 16, rect.y + 12, rect.width - 32, 30),
        font,
        accent,
        max_lines=1,
    )
    line_height = font.get_linesize()
    for i, line in enumerate(body_lines):
        draw_wrapped_text_in_rect(
            screen,
            line,
            pygame.Rect(rect.x + 16, rect.y + 56 + i * (line_height + 2), rect.width - 32, line_height),
            font,
            MUTED,
            max_lines=2,
        )


def build_header_menu_rect(width):
    return pygame.Rect(width - 188, 14, 168, 42)


def draw_header(screen, width, font, game):
    pygame.draw.line(screen, LINE, (18, 58), (width - 18, 58), 1)
    tab = pygame.Rect(18, 18, 110, 36)
    pygame.draw.rect(screen, BLUE, tab, border_radius=9)
    draw_wrapped_text_in_rect(screen, f"回合 {game.turn}", tab.inflate(-18, -8), font, (255, 255, 255), max_lines=1, align="center", v_align="center")
    draw_wrapped_text_in_rect(screen, f"{game.current_player.name} 的回合", pygame.Rect(150, 18, 260, 36), font, BLUE, max_lines=1, v_align="center")
    menu_rect = build_header_menu_rect(width)
    draw_flask_icon(screen, (menu_rect.x + 20, menu_rect.centery + 2), BLUE, 0.55)
    draw_wrapped_text_in_rect(screen, "Cell Wars", pygame.Rect(menu_rect.x + 38, menu_rect.y + 4, menu_rect.width - 38, 34), font, BLUE, max_lines=1, align="right", v_align="center")


def draw_atp_bar(screen, rect, value, maximum, color):
    pygame.draw.rect(screen, (222, 231, 242), rect, border_radius=8)
    fill_width = int(rect.width * min(1, max(0, value / maximum)))
    if fill_width:
        pygame.draw.rect(screen, color, pygame.Rect(rect.x, rect.y, fill_width, rect.height), border_radius=8)


def structure_summary(player):
    if not player.structures:
        return "無"
    return f"{len(player.structures)} 種"


def player_detail_lines(player, lab_text=None):
    lines = [
        f"手牌：{len(player.hand)}",
        f"結構：{card_list(player.structures)}",
    ]
    if lab_text is not None:
        lines.append(f"實驗室：{lab_text}")
    return lines


def player_panel_height(player, font, width, expanded=False, lab_text=None):
    if not expanded:
        return 188 if lab_text is None else 218

    content_width = max(80, width - 104)
    line_count = 0
    for line in player_detail_lines(player, lab_text):
        line_count += len(wrap_text(line, font, content_width))
    return max(218, 142 + line_count * (font.get_linesize() + 2))


def draw_player_panel(screen, rect, player, font, active=False, accent=BLUE, expanded=False, lab_text=None, max_atp=30):
    fill = (251, 255, 250) if accent == GREEN else PANEL
    border = (164, 218, 174) if accent == GREEN else LINE
    draw_shadowed_panel(screen, rect, fill=fill, border=border)
    avatar = pygame.Rect(rect.x + 16, rect.y + 36, 54, 54)
    pygame.draw.ellipse(screen, (255, 255, 255), avatar)
    pygame.draw.ellipse(screen, accent, avatar, 2)
    if accent == GREEN:
        draw_leaf_icon(screen, avatar.center, accent, 0.9)
    else:
        draw_dot_icon(screen, avatar.center, accent, 0.85)
    draw_wrapped_text_in_rect(screen, player.name, pygame.Rect(rect.x + 88, rect.y + 18, rect.width - 104, 34), font, accent, max_lines=1)
    draw_wrapped_text_in_rect(screen, f"種族：{race_name(player.race)}", pygame.Rect(rect.x + 88, rect.y + 56, rect.width - 104, 28), font, MUTED, max_lines=1)
    draw_wrapped_text_in_rect(screen, "ATP", pygame.Rect(rect.x + 88, rect.y + 92, 54, 28), font, TEXT, max_lines=1)
    draw_atp_bar(screen, pygame.Rect(rect.x + 140, rect.y + 100, max(40, rect.width - 230), 12), player.atp, max_atp, accent)
    draw_wrapped_text_in_rect(screen, f"{player.atp} / {max_atp}", pygame.Rect(rect.right - 92, rect.y + 88, 78, 30), font, TEXT, max_lines=1, align="right")

    detail_rect = pygame.Rect(rect.x + 88, rect.y + 126, rect.width - 104, rect.height - 132)
    if expanded:
        y = detail_rect.y
        for line in player_detail_lines(player, lab_text):
            lines = wrap_text(line, font, detail_rect.width)
            for wrapped_line in lines:
                draw_wrapped_text_in_rect(
                    screen,
                    wrapped_line,
                    pygame.Rect(detail_rect.x, y, detail_rect.width, font.get_linesize()),
                    font,
                    accent if wrapped_line.startswith("實驗室") else MUTED,
                    max_lines=1,
                )
                y += font.get_linesize() + 2
    else:
        summary_lines = [f"手牌：{len(player.hand)}", f"結構：{structure_summary(player)}"]
        if lab_text is not None:
            summary_lines.append("實驗室：有" if lab_text != "空" else "實驗室：空")
        y = detail_rect.y
        for line in summary_lines:
            draw_wrapped_text_in_rect(
                screen,
                line,
                pygame.Rect(detail_rect.x, y, detail_rect.width, font.get_linesize()),
                font,
                accent if line.startswith("實驗室") else MUTED,
                max_lines=1,
            )
            y += font.get_linesize() + 2

    hint_rect = pygame.Rect(rect.x + 16, rect.bottom - font.get_linesize() - 8, 86, font.get_linesize())
    draw_wrapped_text_in_rect(
        screen,
        "收合" if expanded else "展開",
        hint_rect,
        font,
        accent,
        max_lines=1,
    )
    if active:
        pygame.draw.rect(screen, accent, rect, 2, border_radius=8)


def draw_battle_log(screen, rect, font, messages):
    draw_shadowed_panel(screen, rect)
    pygame.draw.rect(screen, PANEL_TINT, pygame.Rect(rect.x, rect.y, rect.width, 42), border_top_left_radius=8, border_top_right_radius=8)
    pygame.draw.line(screen, LINE, (rect.x, rect.y + 42), (rect.right, rect.y + 42), 1)
    draw_wrapped_text_in_rect(
        screen,
        "戰鬥紀錄",
        pygame.Rect(rect.x + 18, rect.y + 10, rect.width - 36, 30),
        font,
        BLUE,
        max_lines=1,
    )

    body_rect = pygame.Rect(rect.x + 18, rect.y + 58, rect.width - 36, rect.height - 72)
    line_height = font.get_linesize()
    entry_gap = 10
    entries = []

    for message in messages[-8:]:
        lines = wrap_text(message, font, body_rect.width - 26)
        entries.append(lines)

    selected_entries = []
    used_height = 0
    for lines in reversed(entries):
        entry_height = len(lines) * line_height + entry_gap
        if selected_entries and used_height + entry_height > body_rect.height:
            break
        if not selected_entries and entry_height > body_rect.height:
            selected_entries.append(lines[: max(1, body_rect.height // line_height)])
            break
        selected_entries.append(lines)
        used_height += entry_height

    y = body_rect.y
    palette = [(82, 169, 102), (104, 157, 222), (238, 104, 78), (151, 163, 176)]
    visible_messages = messages[-len(selected_entries):]
    for entry_index, lines in enumerate(reversed(selected_entries)):
        dot_color = palette[(len(visible_messages) - len(selected_entries) + entry_index) % len(palette)]
        pygame.draw.circle(screen, dot_color, (body_rect.x + 7, y + line_height // 2), 5)
        for line in lines:
            if y + line_height > body_rect.bottom:
                return
            surface = font.render(line, True, MUTED)
            screen.blit(surface, (body_rect.x + 24, y))
            y += line_height
        y += entry_gap


def draw_button(screen, rect, label, font, active=False, accent=BLUE, enabled=True):
    fill = accent if active else (255, 255, 252)
    text_color = (255, 255, 255) if active else accent
    border = accent if active else LINE
    if not enabled:
        fill = (241, 245, 249)
        text_color = (150, 162, 178)
        border = (218, 227, 237)
    pygame.draw.rect(screen, fill, rect, border_radius=8)
    pygame.draw.rect(screen, border, rect, 2, border_radius=8)
    draw_wrapped_text_in_rect(
        screen,
        label,
        rect.inflate(-16, -8),
        font,
        text_color,
        max_lines=1,
        align="center",
        v_align="center",
    )


def build_settings_panel_rect(width, height):
    return pygame.Rect(width - 330, 66, 306, min(420, height - 90))


def draw_settings_panel(screen, rect, font, game):
    draw_shadowed_panel(screen, rect, fill=(255, 255, 252), border=LINE)
    pygame.draw.rect(screen, PANEL_TINT, pygame.Rect(rect.x, rect.y, rect.width, 42), border_top_left_radius=8, border_top_right_radius=8)
    pygame.draw.line(screen, LINE, (rect.x, rect.y + 42), (rect.right, rect.y + 42), 1)
    draw_wrapped_text_in_rect(screen, "設定與說明", pygame.Rect(rect.x + 18, rect.y + 10, rect.width - 36, 30), font, BLUE, max_lines=1)

    button_rects = {}
    y = rect.y + 62
    ai_rect = pygame.Rect(rect.x + 18, y, rect.width - 36, 44)
    draw_button(screen, ai_rect, f"AI 對戰：{'ON' if game.ai_enabled else 'OFF'}", font, active=game.ai_enabled, accent=BLUE)
    button_rects["ai"] = ai_rect

    y += 64
    draw_wrapped_text_in_rect(screen, "難度選擇", pygame.Rect(rect.x + 18, y, rect.width - 36, 28), font, MUTED, max_lines=1)
    y += 34
    difficulty_rects = []
    gap = 8
    button_w = (rect.width - 36 - gap * 2) / 3
    for i, difficulty in enumerate(DIFFICULTIES):
        button_rect = pygame.Rect(rect.x + 18 + i * (button_w + gap), y, button_w, 40)
        draw_button(screen, button_rect, difficulty, font, active=game.difficulty == difficulty, accent=GREEN)
        difficulty_rects.append((difficulty, button_rect))
    button_rects["difficulty"] = difficulty_rects

    y += 62
    help_rect = pygame.Rect(rect.x + 18, y, rect.width - 36, 44)
    draw_button(screen, help_rect, "遊戲說明", font, accent=BLUE)
    button_rects["help"] = help_rect

    y += 62
    close_panel_rect = pygame.Rect(rect.x + 18, y, rect.width - 36, 44)
    draw_button(screen, close_panel_rect, "關閉面板", font, accent=MUTED)
    button_rects["close_panel"] = close_panel_rect

    y += 62
    catalog_rect = pygame.Rect(rect.x + 18, y, rect.width - 36, 44)
    draw_button(screen, catalog_rect, "卡牌圖鑑", font, accent=GOLD)
    button_rects["catalog"] = catalog_rect
    return button_rects


def modal_rect(width, height):
    return pygame.Rect(width * 0.12, height * 0.10, width * 0.76, height * 0.82)


def catalog_modal_rect(width, height):
    return pygame.Rect(width * 0.10, height * 0.10, width * 0.80, height * 0.82)


def card_detail_modal_rect(width, height):
    modal_h = min(height * 0.76, 680)
    modal_w = modal_h * 0.75
    if modal_w > width * 0.58:
        modal_w = width * 0.58
        modal_h = modal_w * 4 / 3
    return pygame.Rect((width - modal_w) / 2, (height - modal_h) / 2, modal_w, modal_h)


def draw_modal_frame(screen, rect, font, title, accent=BLUE):
    shade = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
    shade.fill((246, 250, 255, 188))
    screen.blit(shade, (0, 0))
    draw_shadowed_panel(screen, rect, fill=(255, 255, 252), border=LINE)
    pygame.draw.rect(screen, PANEL_TINT, pygame.Rect(rect.x, rect.y, rect.width, 50), border_top_left_radius=8, border_top_right_radius=8)
    pygame.draw.line(screen, LINE, (rect.x, rect.y + 50), (rect.right, rect.y + 50), 1)
    draw_wrapped_text_in_rect(screen, title, pygame.Rect(rect.x + 24, rect.y + 12, rect.width - 96, 34), font, accent, max_lines=1)
    close_rect = pygame.Rect(rect.right - 54, rect.y + 10, 36, 32)
    pygame.draw.rect(screen, (255, 255, 252), close_rect, border_radius=8)
    pygame.draw.rect(screen, LINE, close_rect, 2, border_radius=8)
    pygame.draw.line(screen, WARN, (close_rect.x + 10, close_rect.y + 9), (close_rect.right - 10, close_rect.bottom - 9), 3)
    pygame.draw.line(screen, WARN, (close_rect.right - 10, close_rect.y + 9), (close_rect.x + 10, close_rect.bottom - 9), 3)
    return close_rect


def render_text(font, text, color, bold=False):
    original_bold = font.get_bold()
    font.set_bold(bold)
    surface = font.render(text, True, color)
    font.set_bold(original_bold)
    return surface


def styled_tokens(line):
    if line.startswith("## "):
        return [(token, True) for token in text_tokens(line[3:])]

    if "：" in line:
        prefix, rest = line.split("：", 1)
        if len(prefix) <= 12:
            tokens = [(token, True) for token in text_tokens(prefix + "：")]
            tokens.extend((token, False) for token in text_tokens(rest))
            return tokens

    return [(token, False) for token in text_tokens(line)]


def wrap_styled_line(line, font, max_width):
    rows = []
    current = []
    current_text = ""

    for token, bold in styled_tokens(line):
        candidate_text = token_join(current_text, token)
        display_token = candidate_text[len(current_text):] if current_text else token
        candidate = current + [(display_token, bold)]
        candidate_width = sum(font.size(part)[0] for part, _part_bold in candidate)
        if current and candidate_width > max_width:
            rows.append(current)
            current = [(token, bold)]
            current_text = token
        else:
            current = candidate
            current_text = candidate_text

    if current:
        rows.append(current)
    return rows or [[("", False)]]


def styled_lines_height(lines, font, width):
    total = 0
    line_height = font.get_linesize()
    for line in lines:
        if line == "":
            total += int(line_height * 0.65)
            continue
        total += len(wrap_styled_line(line, font, width)) * (line_height + 2)
        total += int(line_height * 0.35)
    return total


def draw_styled_paragraphs(screen, lines, rect, font, text_color=MUTED, accent=BLUE, scroll=0):
    rect = pygame.Rect(rect)
    line_height = font.get_linesize()
    y = rect.y - scroll
    previous_clip = screen.get_clip()
    screen.set_clip(rect)

    for line in lines:
        if line == "":
            y += int(line_height * 0.65)
            continue

        is_heading = line.startswith("## ")
        color = accent if is_heading else text_color
        paragraph_rows = wrap_styled_line(line, font, rect.width)
        for row in paragraph_rows:
            x = rect.x
            for part, bold in row:
                surface = render_text(font, part, color if is_heading or bold else text_color, bold=is_heading or bold)
                screen.blit(surface, (int(x), int(y)))
                x += surface.get_width()
            y += line_height + 2
        y += int(line_height * 0.35)
    screen.set_clip(previous_clip)


def draw_help_modal(screen, rect, font, game, scroll=0):
    close_rect = draw_modal_frame(screen, rect, font, "遊戲說明", accent=BLUE)
    lines = [
        "## 一、遊戲簡介",
        "《Cell Wars》是一款以細胞代謝與生化反應為核心的回合制卡牌遊戲。",
        "玩家操控不同生命類型，收集葡萄糖、氧氣、水、二氧化碳等資源，建立粒線體、葉綠體、核糖體等胞器與結構，並在實驗室中組合卡牌、執行生化反應，以製造 ATP。",
        "核心流程：收集反應物 -> 建立必要結構 -> 組合生化反應 -> 製造 ATP。",
        "",
        "## 二、遊戲目標",
        f"遊戲目標：目前版本中，率先讓自己的 ATP 達到 {game.win_atp} 即可獲勝。簡單模式目標為 30 ATP，普通模式目標為 50 ATP。",
        "遊戲人數：目前版本支援玩家 A、B 本機輪流遊玩；AI 對戰開啟時，玩家 B 由 AI 操作。",
        "",
        "## 三、遊戲難度",
        "簡單模式：包含植物細胞、動物細胞，以及基礎資源、粒線體、葉綠體、細胞呼吸、光合作用、ATP 竊取。",
        "普通模式：加入植物細胞、動物細胞、酵母菌、細菌，以及酒精發酵、病毒、免疫反應、修復、細胞膜、細胞壁、溶體、缺氧、日照與夜晚。",
        "困難模式：目前可選擇，但暫時沿用普通模式內容，保留給後續加入 ADP、無機磷酸、毒素、DNA 損傷與突發狀況。",
        "",
        "## 四、遊戲區域",
        "ATP 區：顯示玩家目前 ATP。ATP 可用於支付卡牌成本、發動攻擊或防禦、執行部分反應與判定勝利。",
        "手牌區：顯示玩家目前持有的卡牌。手牌上限為 8 張；手牌滿時，選 1 張按 Shift 丟棄，再點擊牌堆補抽。",
        "卡牌說明：選中手牌後按 X，可查看該卡牌的詳細功能與相關反應。點擊說明彈窗外空白處可關閉。",
        "資源合成：普通模式中，每位玩家每回合可將 2 張資源牌合成為 1 張基礎資源。合成不消耗 ATP，材料會進入棄牌堆，新資源直接加入手牌。",
        "資源合成屬於遊戲化的細胞調節機制，並非真實生化反應。",
        "胞器與結構區：已建立的胞器與結構會永久留在場上。除非受到病毒封鎖或特殊效果影響，胞器與結構不會因執行反應而消耗。",
        "實驗室 Laboratory：左鍵點擊手牌可加入或移出實驗室。玩家可在確認反應前自由調整實驗室中的卡牌。",
        "反應預覽區：當實驗室中的卡牌符合反應時，系統會顯示反應名稱、使用材料、產物與可獲得 ATP。按 Enter 才會消耗材料並結算效果。",
        "資源牌：不可單獨產生 ATP；必須形成有效反應，才會獲得該反應額定 ATP。",
        "結構牌：可單獨建立，打出後回合結束。重複結構沒有額外效果，可選取後按 Shift 丟棄。",
        "環境區：目前同一時間只能存在一種普通環境。缺氧、日照、夜晚會影響可用反應與 ATP 修正，新環境會取代舊環境。",
    ]
    content_rect = pygame.Rect(rect.x + 32, rect.y + 72, rect.width - 64, rect.height - 94)
    max_scroll = max(0, styled_lines_height(lines, font, content_rect.width) - content_rect.height)
    scroll = min(max(0, scroll), max_scroll)
    draw_styled_paragraphs(
        screen,
        lines,
        content_rect,
        font,
        text_color=MUTED,
        accent=BLUE,
        scroll=scroll,
    )
    if max_scroll:
        track = pygame.Rect(rect.right - 18, content_rect.y, 5, content_rect.height)
        thumb_h = max(34, int(content_rect.height * content_rect.height / (content_rect.height + max_scroll)))
        thumb_y = content_rect.y + int((content_rect.height - thumb_h) * (scroll / max_scroll))
        pygame.draw.rect(screen, (226, 235, 244), track, border_radius=3)
        pygame.draw.rect(screen, LINE, pygame.Rect(track.x, thumb_y, track.width, thumb_h), border_radius=3)
    return close_rect


def catalog_cards_for(tab):
    return [card for card in CATALOG_CARDS if card.type == tab]


def catalog_tab_rects(rect):
    tab_rects = []
    tab_x = rect.x + 36
    for tab_id, label, color in CATALOG_TABS:
        tab_rects.append((tab_id, label, color, pygame.Rect(tab_x, rect.y - 34, 116, 42)))
        tab_x += 126
    return tab_rects


def catalog_card_rects(rect, tab):
    book_rect = pygame.Rect(rect.x + 26, rect.y + 72, rect.width - 52, rect.height - 104)
    card_w = min(210, (book_rect.width / 2 - 78) / 2)
    card_h = min(250, (book_rect.height - 72) / 2)
    left_page_x = book_rect.x + 34
    right_page_x = book_rect.centerx + 34
    top_y = book_rect.y + 28
    x_slots = [left_page_x, left_page_x + card_w + 22, right_page_x, right_page_x + card_w + 22]
    y_slots = [top_y, top_y + card_h + 18]
    rects = []
    for i, card in enumerate(catalog_cards_for(tab)[:8]):
        page = i // 4
        page_index = i % 4
        col = page_index % 2
        row = page_index // 2
        slot_index = page * 2 + col
        rects.append((card, pygame.Rect(x_slots[slot_index], y_slots[row], card_w, card_h)))
    return rects


def card_info_lines(card, reaction_engine):
    if card is None:
        return []

    lines = list(CARD_DETAIL_LINES.get(card.en_name, []))
    if not lines:
        if card.type == "structure":
            lines = ["功能：可單獨建立，之後可支援反應。"]
        else:
            lines = ["功能：資源牌本身不產生 ATP；需透過有效反應使用，完成反應後才獲得該反應額定 ATP。"]

    matched = []
    for reaction in reaction_engine.reactions:
        names = set(reaction.reactants) | set(reaction.required_structures) | set(reaction.products)
        if card.en_name in names:
            matched.append(f"{reaction_name(reaction)}：{reaction_formula(reaction)}，+{reaction.atp_gain} ATP")
    if matched:
        if lines and lines[-1] != "":
            lines.append("")
        lines.append("相關反應：")
        lines.extend(matched)
    elif card.type in {"resource", "structure"}:
        if lines and lines[-1] != "":
            lines.append("")
        lines.append("目前沒有寫入包含此卡牌的反應式。")
    if card.type == "resource":
        if lines and lines[-1] != "":
            lines.append("")
        lines.append("資源合成註記：資源合成屬於遊戲化的細胞調節機制，並非真實生化反應。")
    spaced_lines = []
    for index, line in enumerate(lines):
        spaced_lines.append(line)
        if index >= len(lines) - 1:
            continue
        next_line = lines[index + 1]
        if line == "" or next_line == "":
            continue
        if line.startswith("卡牌名稱") and next_line.startswith("卡牌類型"):
            continue
        if line == "相關反應：":
            continue
        if "：" in line:
            spaced_lines.append("")
    return spaced_lines


def card_detail_content_height(font, content_width, card, game):
    return styled_lines_height(card_info_lines(card, game.reaction_engine), font, content_width) + 28


def draw_catalog_card(screen, rect, card, font, selected=False):
    accent = {"action": WARN, "resource": GREEN, "structure": GOLD}.get(card.type, BLUE)
    pygame.draw.rect(screen, (255, 255, 248), rect, border_radius=7)
    pygame.draw.rect(screen, accent if selected else (205, 217, 231), rect, 3 if selected else 1, border_radius=7)
    draw_wrapped_text_in_rect(screen, card.zh_name, pygame.Rect(rect.x + 12, rect.y + 12, rect.width - 24, 34), font, TEXT, max_lines=1)
    draw_text_in_rect(screen, card.en_name, pygame.Rect(rect.x + 12, rect.y + 50, rect.width - 24, 54), font, MUTED, max_lines=2)
    draw_flask_icon(screen, (rect.centerx, rect.y + rect.height * 0.64), (185, 194, 183), 0.50)
    draw_wrapped_text_in_rect(screen, card_type_label(card), pygame.Rect(rect.x + 12, rect.bottom - 42, rect.width - 24, 30), font, TEXT, max_lines=1, align="center")


def draw_catalog_modal(screen, rect, font, tab, selected_card, game):
    close_rect = draw_modal_frame(screen, rect, font, "卡牌圖鑑", accent=GOLD)
    tab_rects = []
    for tab_id, label, color, tab_rect in catalog_tab_rects(rect):
        pygame.draw.rect(screen, color if tab == tab_id else (255, 255, 252), tab_rect, border_top_left_radius=8, border_top_right_radius=8)
        pygame.draw.rect(screen, color, tab_rect, 2, border_top_left_radius=8, border_top_right_radius=8)
        draw_wrapped_text_in_rect(screen, label, tab_rect.inflate(-12, -8), font, (255, 255, 255) if tab == tab_id else color, max_lines=1, align="center", v_align="center")
        tab_rects.append((tab_id, tab_rect))

    book_rect = pygame.Rect(rect.x + 26, rect.y + 72, rect.width - 52, rect.height - 104)
    pygame.draw.rect(screen, (255, 252, 240), book_rect, border_radius=8)
    pygame.draw.rect(screen, (210, 194, 154), book_rect, 2, border_radius=8)
    pygame.draw.line(screen, (210, 194, 154), (book_rect.centerx, book_rect.y + 12), (book_rect.centerx, book_rect.bottom - 12), 2)

    card_rects = []
    for card, card_rect in catalog_card_rects(rect, tab):
        draw_catalog_card(screen, card_rect, card, font, selected=selected_card and selected_card.en_name == card.en_name)
        card_rects.append((card, card_rect))

    draw_wrapped_text_in_rect(
        screen,
        "點擊卡牌查看功能與相關反應。",
        pygame.Rect(rect.x + 32, book_rect.bottom + 16, rect.width - 64, 34),
        font,
        MUTED,
        max_lines=1,
        align="center",
    )
    return close_rect, tab_rects, card_rects


def draw_card_detail_modal(screen, rect, font, card, game, scroll=0):
    draw_shadowed_panel(screen, rect, fill=(255, 255, 252), border=LINE)
    pygame.draw.rect(screen, PANEL_TINT, pygame.Rect(rect.x, rect.y, rect.width, 54), border_top_left_radius=8, border_top_right_radius=8)
    pygame.draw.line(screen, LINE, (rect.x, rect.y + 54), (rect.right, rect.y + 54), 1)
    accent = {"action": WARN, "resource": GREEN, "structure": GOLD, "defense": BLUE, "environment": MUTED}.get(card.type, BLUE)
    draw_wrapped_text_in_rect(
        screen,
        f"{card.zh_name}（{card.en_name}）",
        pygame.Rect(rect.x + 24, rect.y + 12, rect.width - 48, 34),
        font,
        accent,
        max_lines=1,
        align="center",
    )
    lines = card_info_lines(card, game.reaction_engine)
    info_rect = pygame.Rect(rect.x + 24, rect.y + 74, rect.width - 48, rect.height - 98)
    content_width = info_rect.width - 28
    max_scroll = max(0, card_detail_content_height(font, content_width, card, game) - info_rect.height)
    scroll = min(max(0, scroll), max_scroll)
    draw_styled_paragraphs(
        screen,
        lines,
        pygame.Rect(info_rect.x + 14, info_rect.y + 14, info_rect.width - 28, info_rect.height - 28),
        font,
        text_color=MUTED,
        accent=accent,
        scroll=scroll,
    )
    if max_scroll:
        track = pygame.Rect(rect.right - 16, info_rect.y, 5, info_rect.height)
        thumb_h = max(34, int(info_rect.height * info_rect.height / (info_rect.height + max_scroll)))
        thumb_y = info_rect.y + int((info_rect.height - thumb_h) * (scroll / max_scroll))
        pygame.draw.rect(screen, (226, 235, 244), track, border_radius=3)
        pygame.draw.rect(screen, LINE, pygame.Rect(track.x, thumb_y, track.width, thumb_h), border_radius=3)


def reaction_preview_lines(game):
    if game.waiting_to_discard_for_offer:
        return [
            "手牌已滿",
            "選 1 張按 Shift 丟棄",
            "接著會拿走棄牌",
        ]

    if game.discard_offer_card:
        return [
            f"可拿取棄牌：{game.discard_offer_card.zh_name}",
            "點擊棄牌面板拿取",
            "其他行動會放回牌堆",
        ]

    if game.waiting_for_deck_draw_after_discard:
        return [
            "已丟棄 1 張牌",
            "請點擊牌堆補抽 1 張",
            "補抽後會換下一位出牌",
        ]

    if game.preview:
        preview_atp = game.reaction_atp_gain(game.preview, game.current_player, commit=False)
        return [
            f"可形成：{reaction_name(game.preview)}",
            reaction_formula(game.preview),
            f"按 Enter 執行：+{preview_atp} ATP",
        ]

    if game.reaction_table:
        selected_card = game.selected_single_card()
        if game.can_single_play_card(selected_card):
            if selected_card.type == "structure" and game.has_structure(game.current_player, selected_card.en_name):
                return [
                    f"重複結構：{selected_card.zh_name}",
                    "按 Shift 丟棄此牌",
                    "丟棄後會換下一位",
                ]
            if selected_card.type == "structure":
                reject_reason = game.structure_reject_reason(game.current_player, selected_card)
                if reject_reason:
                    return [
                        reject_reason,
                        "請選擇其他卡牌",
                        "或移出實驗室",
                    ]
            return [
                f"可單獨打出：{selected_card.zh_name}",
                "按 Enter 出牌",
                "出牌後會換下一位",
            ]
        if game.current_player_hand_full() and selected_card:
            return [
                "手牌已滿",
                "按 Shift 丟棄選取卡牌",
                "再點擊牌堆補抽 1 張",
            ]
        return [
            "尚未形成反應",
            "反應桌：" + card_list(game.reaction_table),
            "可繼續加入或移除手牌",
        ]

    return [
        "從手牌選擇卡牌",
        "可形成的反應會顯示在這裡",
        "有效反應可按 Enter 執行",
    ]


def build_sprites(game, width, height):
    sprites = []
    start_x = width * 0.18
    y = height * 0.75
    hand_right = width * 0.69
    available_width = max(0, hand_right - start_x - CARD_WIDTH - 16)
    gap = min(170, max(58, available_width / max(1, len(game.current_player.hand) - 1)))

    for i, card in enumerate(game.current_player.hand):
        sprites.append(
            CardSprite(
                card,
                start_x + i * gap,
                y,
                selected=card in game.selected_cards,
                synthesis_selected=card in game.synthesis_selected_cards,
            )
        )
    return sprites


def build_synthesis_button_rect(deck_rect, height):
    return pygame.Rect(deck_rect.x, min(deck_rect.bottom + 12, height - 58), deck_rect.width, 44)


def synthesis_resource_card(en_name):
    for card in CATALOG_CARDS:
        if card.en_name == en_name:
            return card
    return Card(en_name, en_name, "resource")


def synthesis_panel_rect(width, height):
    return pygame.Rect(width * 0.29, height * 0.585, width * 0.40, height * 0.15)


def synthesis_target_rects(rect):
    gap = 8
    button_w = (rect.width - 32 - gap * 4) / 5
    y = rect.y + 48
    return [
        (resource_name, pygame.Rect(rect.x + 16 + i * (button_w + gap), y, button_w, 36))
        for i, resource_name in enumerate(SYNTHESIS_RESOURCES)
    ]


def synthesis_confirm_rect(rect):
    return pygame.Rect(rect.right - 160, rect.bottom - 42, 132, 34)


def synthesis_cancel_rect(rect):
    return pygame.Rect(rect.x + 18, rect.bottom - 42, 100, 34)


def draw_synthesis_panel(screen, rect, font, game):
    draw_shadowed_panel(screen, rect, fill=(255, 255, 252), border=GOLD)
    pygame.draw.rect(screen, (255, 249, 231), pygame.Rect(rect.x, rect.y, rect.width, 38), border_top_left_radius=8, border_top_right_radius=8)
    pygame.draw.line(screen, LINE, (rect.x, rect.y + 38), (rect.right, rect.y + 38), 1)
    draw_wrapped_text_in_rect(
        screen,
        "資源合成",
        pygame.Rect(rect.x + 16, rect.y + 8, 160, 28),
        font,
        GOLD,
        max_lines=1,
    )
    material_text = card_list(game.synthesis_selected_cards, "請選擇 2 張資源牌")
    if len(game.synthesis_selected_cards) == 2 and game.synthesis_target:
        target_card = synthesis_resource_card(game.synthesis_target)
        material_text = f"{card_list(game.synthesis_selected_cards)} -> {card_name(target_card)}"
    draw_wrapped_text_in_rect(
        screen,
        material_text,
        pygame.Rect(rect.x + 180, rect.y + 8, rect.width - 200, 28),
        font,
        MUTED,
        max_lines=1,
        align="right",
    )

    for resource_name, target_rect in synthesis_target_rects(rect):
        resource_card = synthesis_resource_card(resource_name)
        enabled = len(game.synthesis_selected_cards) == 2
        draw_button(
            screen,
            target_rect,
            resource_card.zh_name,
            font,
            active=game.synthesis_target == resource_name,
            accent=GREEN,
            enabled=enabled,
        )

    draw_button(screen, synthesis_cancel_rect(rect), "取消", font, accent=MUTED)
    can_confirm = len(game.synthesis_selected_cards) == 2 and bool(game.synthesis_target)
    draw_button(screen, synthesis_confirm_rect(rect), "確認合成", font, active=can_confirm, accent=GOLD, enabled=can_confirm)


def build_deck_rect(width, height):
    return pygame.Rect(width * 0.72, height * 0.58, width * 0.26, height * 0.25)


def build_discard_rect(width, height):
    return pygame.Rect(width * 0.36, height * 0.60, width * 0.32, height * 0.08)


def build_restart_button_rect(width, height):
    return pygame.Rect(width * 0.40, height * 0.505, width * 0.20, height * 0.065)


def deck_panel_lines(game):
    if game.discard_offer_card:
        return [
            f"牌堆：{len(game.deck)} 張",
            "可先拿取棄牌",
            "或點牌堆放回",
            "再抽牌",
        ]

    if game.waiting_for_deck_draw_after_discard:
        return [
            f"牌堆：{len(game.deck)} 張",
            "已丟棄卡牌",
            "點擊補抽",
            "並換人",
        ]

    if game.current_player_hand_full():
        return [
            f"牌堆：{len(game.deck)} 張",
            "手牌已滿",
            "先選 1 張按 Shift 丟棄",
        ]

    if game.difficulty == "簡單" and game.can_current_player_form_reaction():
        return [
            f"牌堆：{len(game.deck)} 張",
            "目前可形成反應",
            "請在實驗室出牌",
        ]

    if game.can_current_player_form_reaction():
        return [
            f"牌堆：{len(game.deck)} 張",
            "目前可形成反應",
            "也可抽 1 張跳過",
        ]

    return [
        f"牌堆：{len(game.deck)} 張",
        "目前無有效反應",
        "點擊抽 1 張",
        "並換人",
    ]


async def main():
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE, pygame.RESIZABLE)
    pygame.display.set_caption("細胞戰爭")
    clock = pygame.time.Clock()
    font = load_font(MIN_PAGE_FONT_SIZE)
    big_font = load_font(68)

    game = Game()
    expanded_panels = {"player": False, "opponent": False}
    settings_open = False
    active_modal = None
    catalog_tab = "resource"
    catalog_selected_card = None
    catalog_detail_scroll = 0
    hand_detail_card = None
    hand_detail_scroll = 0
    help_scroll = 0
    running = True

    while running:
        width = screen.get_width()
        height = screen.get_height()
        left_x = width * 0.015
        left_w = width * 0.26
        center_x = width * 0.29
        center_w = width * 0.40
        right_x = width * 0.72
        right_w = width * 0.26
        lab_text = card_list(game.reaction_table, "空")
        opponent_h = player_panel_height(game.opponent, font, left_w, expanded_panels["opponent"])
        player_h = player_panel_height(game.player, font, left_w, expanded_panels["player"], lab_text)
        opponent_rect = pygame.Rect(left_x, height * 0.08, left_w, opponent_h)
        player_rect = pygame.Rect(left_x, opponent_rect.bottom + 12, left_w, player_h)
        hand_y = height * 0.745
        hud_rect = pygame.Rect(center_x, height * 0.59, center_w, height * 0.14)
        hand_rect = pygame.Rect(left_x, hand_y, center_x + center_w - left_x, height - hand_y - 8)
        sprites = build_sprites(game, width, height)
        deck_rect = build_deck_rect(width, height)
        discard_rect = build_discard_rect(width, height)
        synthesis_button_rect = build_synthesis_button_rect(deck_rect, height)
        active_synthesis_panel_rect = synthesis_panel_rect(width, height)
        restart_button_rect = build_restart_button_rect(width, height)
        header_menu_rect = build_header_menu_rect(width)
        settings_rect = build_settings_panel_rect(width, height)
        center_modal_rect = modal_rect(width, height)
        active_modal_rect = catalog_modal_rect(width, height) if active_modal == "catalog" else center_modal_rect

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEWHEEL and hand_detail_card:
                hand_detail_scroll = max(0, hand_detail_scroll - event.y * 48)
                continue

            if event.type == pygame.MOUSEWHEEL and active_modal == "catalog" and catalog_selected_card:
                catalog_detail_scroll = max(0, catalog_detail_scroll - event.y * 48)
                continue

            if event.type == pygame.MOUSEWHEEL and active_modal == "help":
                help_scroll = max(0, help_scroll - event.y * 48)
                continue

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and hand_detail_card:
                detail_rect = card_detail_modal_rect(width, height)
                if not detail_rect.collidepoint(pygame.mouse.get_pos()):
                    hand_detail_card = None
                    hand_detail_scroll = 0
                continue

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and active_modal:
                mouse_pos = pygame.mouse.get_pos()
                if active_modal == "catalog" and catalog_selected_card:
                    detail_rect = card_detail_modal_rect(width, height)
                    if not detail_rect.collidepoint(mouse_pos):
                        catalog_selected_card = None
                        catalog_detail_scroll = 0
                    continue

                close_rect = pygame.Rect(active_modal_rect.right - 54, active_modal_rect.y + 10, 36, 32)
                if close_rect.collidepoint(mouse_pos):
                    active_modal = None
                    catalog_selected_card = None
                    catalog_detail_scroll = 0
                    hand_detail_card = None
                    hand_detail_scroll = 0
                    help_scroll = 0
                    continue
                if active_modal == "catalog":
                    for tab_id, _label, _color, tab_rect in catalog_tab_rects(active_modal_rect):
                        if tab_rect.collidepoint(mouse_pos):
                            catalog_tab = tab_id
                            catalog_selected_card = None
                            catalog_detail_scroll = 0
                            break
                    else:
                        for card, card_rect in catalog_card_rects(active_modal_rect, catalog_tab):
                            if card_rect.collidepoint(mouse_pos):
                                catalog_selected_card = card
                                catalog_detail_scroll = 0
                                break
                    continue
                continue

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and header_menu_rect.collidepoint(pygame.mouse.get_pos()):
                settings_open = not settings_open
                continue

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and settings_open:
                mouse_pos = pygame.mouse.get_pos()
                settings_buttons = {}
                y = settings_rect.y + 62
                settings_buttons["ai"] = pygame.Rect(settings_rect.x + 18, y, settings_rect.width - 36, 44)
                y += 98
                gap = 8
                button_w = (settings_rect.width - 36 - gap * 2) / 3
                difficulty_rects = []
                for i, difficulty in enumerate(DIFFICULTIES):
                    difficulty_rects.append((difficulty, pygame.Rect(settings_rect.x + 18 + i * (button_w + gap), y, button_w, 40)))
                y += 62
                settings_buttons["help"] = pygame.Rect(settings_rect.x + 18, y, settings_rect.width - 36, 44)
                y += 62
                settings_buttons["close_panel"] = pygame.Rect(settings_rect.x + 18, y, settings_rect.width - 36, 44)
                y += 62
                settings_buttons["catalog"] = pygame.Rect(settings_rect.x + 18, y, settings_rect.width - 36, 44)

                if settings_buttons["ai"].collidepoint(mouse_pos):
                    game.ai_enabled = not game.ai_enabled
                    game.add_log(f"AI 對戰已{'開啟' if game.ai_enabled else '關閉'}")
                    continue
                clicked_difficulty = False
                for difficulty, difficulty_rect in difficulty_rects:
                    if difficulty_rect.collidepoint(mouse_pos):
                        ai_enabled = game.ai_enabled
                        game = Game(ai_enabled=ai_enabled, difficulty=difficulty)
                        expanded_panels = {"player": False, "opponent": False}
                        hand_detail_card = None
                        hand_detail_scroll = 0
                        game.add_log(f"難度：{difficulty}")
                        clicked_difficulty = True
                        break
                if clicked_difficulty:
                    continue
                if settings_buttons["help"].collidepoint(mouse_pos):
                    active_modal = "help"
                    settings_open = False
                    help_scroll = 0
                    continue
                if settings_buttons["close_panel"].collidepoint(mouse_pos):
                    settings_open = False
                    continue
                if settings_buttons["catalog"].collidepoint(mouse_pos):
                    active_modal = "catalog"
                    settings_open = False
                    catalog_selected_card = None
                    catalog_detail_scroll = 0
                    continue
                if settings_rect.collidepoint(mouse_pos):
                    continue

            if event.type == pygame.MOUSEBUTTONDOWN and game.game_over:
                if event.button == 1 and restart_button_rect.collidepoint(pygame.mouse.get_pos()):
                    ai_enabled = game.ai_enabled
                    difficulty = game.difficulty
                    game = Game(ai_enabled=ai_enabled, difficulty=difficulty)
                    expanded_panels = {"player": False, "opponent": False}
                    hand_detail_card = None
                    hand_detail_scroll = 0
                    continue

            if event.type == pygame.MOUSEBUTTONDOWN and game.waiting_for_player:
                mouse_pos = pygame.mouse.get_pos()
                if event.button == 1 and game.synthesis_mode:
                    if synthesis_cancel_rect(active_synthesis_panel_rect).collidepoint(mouse_pos):
                        game.cancel_synthesis()
                        continue
                    if synthesis_confirm_rect(active_synthesis_panel_rect).collidepoint(mouse_pos):
                        if game.synthesis_target:
                            game.synthesize_resource(game.current_player, game.synthesis_selected_cards, game.synthesis_target)
                        else:
                            game.add_log("請先選擇要合成的資源")
                        continue
                    clicked_target = False
                    for resource_name, target_rect in synthesis_target_rects(active_synthesis_panel_rect):
                        if target_rect.collidepoint(mouse_pos):
                            if len(game.synthesis_selected_cards) == 2:
                                game.set_synthesis_target(resource_name)
                            else:
                                game.add_log("請先選擇 2 張資源牌")
                            clicked_target = True
                            break
                    if clicked_target:
                        continue
                    for i, sprite in enumerate(sprites):
                        if sprite.is_clicked(mouse_pos):
                            game.select_synthesis_card(i)
                            break
                    continue

                if event.button == 1 and synthesis_button_rect.collidepoint(mouse_pos):
                    if game.current_player.has_synthesized_this_turn:
                        game.add_log("本回合已進行過資源合成")
                    else:
                        game.enter_synthesis_mode()
                    continue

                if event.button == 1 and opponent_rect.collidepoint(mouse_pos):
                    expanded_panels["opponent"] = not expanded_panels["opponent"]
                elif event.button == 1 and player_rect.collidepoint(mouse_pos):
                    expanded_panels["player"] = not expanded_panels["player"]
                elif event.button == 1 and discard_rect.collidepoint(mouse_pos):
                    game.take_discard_offer()
                elif event.button == 1 and deck_rect.collidepoint(mouse_pos):
                    game.draw_from_deck_and_pass()
                else:
                    for i, sprite in enumerate(sprites):
                        if sprite.is_clicked(mouse_pos):
                            if event.button == 1:
                                game.select_card(i)
                            break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if hand_detail_card:
                        hand_detail_card = None
                        hand_detail_scroll = 0
                    elif active_modal:
                        active_modal = None
                        catalog_selected_card = None
                        catalog_detail_scroll = 0
                    elif game.synthesis_mode:
                        game.cancel_synthesis()
                    elif settings_open:
                        settings_open = False
                    else:
                        running = False
                elif hand_detail_card or active_modal:
                    continue
                elif game.synthesis_mode:
                    continue
                elif event.key == pygame.K_r and game.game_over:
                    ai_enabled = game.ai_enabled
                    difficulty = game.difficulty
                    game = Game(ai_enabled=ai_enabled, difficulty=difficulty)
                    expanded_panels = {"player": False, "opponent": False}
                    hand_detail_card = None
                    hand_detail_scroll = 0
                elif event.key == pygame.K_SPACE and game.waiting_for_player:
                    game.draw_from_deck_and_pass()
                elif event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT) and game.waiting_for_player:
                    game.discard_selected_card()
                elif event.key == pygame.K_RETURN and game.waiting_for_player:
                    game.resolve_reaction()
                elif event.key == pygame.K_x and game.waiting_for_player and not active_modal:
                    if game.reaction_table:
                        hand_detail_card = game.reaction_table[-1]
                        hand_detail_scroll = 0
                    else:
                        game.add_log("請先選擇 1 張手牌，再按 X 查看說明")
                elif event.key == pygame.K_p and game.waiting_for_player:
                    game.preview_reaction()

        if game.ai_enabled and game.current_player == game.opponent and not game.game_over:
            game.ai_take_turn()

        screen.fill(BG)
        draw_header(screen, width, font, game)

        draw_player_panel(
            screen,
            opponent_rect,
            game.opponent,
            font,
            active=game.current_player == game.opponent,
            accent=BLUE,
            expanded=expanded_panels["opponent"],
            max_atp=game.win_atp,
        )

        draw_player_panel(
            screen,
            player_rect,
            game.player,
            font,
            active=game.current_player == game.player,
            accent=GREEN,
            expanded=expanded_panels["player"],
            lab_text=lab_text,
            max_atp=game.win_atp,
        )

        draw_panel(
            screen,
            hud_rect,
            "操作提示",
            font,
            [
                f"第 {game.turn} 回合 - {game.current_player.name}",
                "Enter出牌，Shift丟棄，X說明",
            ],
            accent=BLUE,
        )

        lab_rect = pygame.Rect(center_x, height * 0.08, center_w, height * 0.22)
        draw_shadowed_panel(screen, lab_rect)
        pygame.draw.rect(screen, PANEL_TINT, pygame.Rect(lab_rect.x, lab_rect.y, lab_rect.width, 42), border_top_left_radius=8, border_top_right_radius=8)
        pygame.draw.line(screen, LINE, (lab_rect.x, lab_rect.y + 42), (lab_rect.right, lab_rect.y + 42), 1)
        draw_wrapped_text_in_rect(screen, "實驗室（Laboratory）", pygame.Rect(lab_rect.x + 18, lab_rect.y + 10, lab_rect.width - 36, 30), font, GREEN, max_lines=1)
        slot_rect = pygame.Rect(lab_rect.x + 18, lab_rect.y + 60, lab_rect.width - 36, lab_rect.height - 80)
        pygame.draw.rect(screen, (255, 255, 255), slot_rect, border_radius=8)
        pygame.draw.rect(screen, (170, 187, 206), slot_rect, 2, border_radius=8)
        table = card_list(game.reaction_table, "將卡牌加入實驗室\n可形成反應")
        draw_wrapped_text_in_rect(screen, table, slot_rect.inflate(-28, -22), font, MUTED, max_lines=3, align="center", v_align="center")

        preview_rect = pygame.Rect(center_x, height * 0.32, center_w, height * 0.26)
        draw_panel(screen, preview_rect, "反應預覽", font, reaction_preview_lines(game), accent=GREEN)

        log_rect = pygame.Rect(right_x, height * 0.08, right_w, height * 0.48)
        draw_battle_log(screen, log_rect, font, game.messages)

        if game.discard_offer_card:
            draw_shadowed_panel(screen, discard_rect, fill=(255, 255, 250), border=GOLD)
            draw_wrapped_text_in_rect(
                screen,
                "棄牌",
                pygame.Rect(discard_rect.x + 12, discard_rect.y + 8, discard_rect.width * 0.28, discard_rect.height - 16),
                font,
                TEXT,
                max_lines=1,
            )
            draw_wrapped_text_in_rect(
                screen,
                f"點擊拿取：{game.discard_offer_card.zh_name}",
                pygame.Rect(discard_rect.x + discard_rect.width * 0.32, discard_rect.y + 8, discard_rect.width * 0.62, discard_rect.height - 16),
                font,
                MUTED,
                max_lines=2,
            )

        draw_shadowed_panel(screen, deck_rect)
        pygame.draw.rect(screen, PANEL_TINT, pygame.Rect(deck_rect.x, deck_rect.y, deck_rect.width, 42), border_top_left_radius=8, border_top_right_radius=8)
        pygame.draw.line(screen, LINE, (deck_rect.x, deck_rect.y + 42), (deck_rect.right, deck_rect.y + 42), 1)
        deck_border = ACCENT if game.waiting_for_deck_draw_after_discard or game.current_player_hand_full() else MUTED if game.can_current_player_form_reaction() else ACCENT
        pygame.draw.rect(screen, deck_border, deck_rect, 2, border_radius=8)
        draw_wrapped_text_in_rect(
            screen,
            "牌堆",
            pygame.Rect(deck_rect.x + 16, deck_rect.y + 12, deck_rect.width - 32, 28),
            font,
            BLUE,
            max_lines=1,
        )
        card_back = pygame.Rect(deck_rect.x + 26, deck_rect.y + 72, min(58, deck_rect.width * 0.22), min(112, deck_rect.height * 0.58))
        pygame.draw.rect(screen, (220, 231, 243), card_back.move(5, 6), border_radius=7)
        pygame.draw.rect(screen, CARD_BACK, card_back, border_radius=7)
        pygame.draw.rect(screen, (235, 242, 250), card_back, 3, border_radius=7)
        draw_flask_icon(screen, card_back.center, (185, 212, 235), 0.72)
        deck_text_x = card_back.right + 18
        for i, line in enumerate(deck_panel_lines(game)):
            draw_wrapped_text_in_rect(
                screen,
                line,
                pygame.Rect(deck_text_x, deck_rect.y + 74 + i * 28, deck_rect.right - deck_text_x - 16, 32),
                font,
                TEXT if i == 0 else MUTED,
                max_lines=2,
            )

        synthesis_enabled = game.waiting_for_player and game.difficulty != "簡單" and not game.current_player.has_synthesized_this_turn
        draw_button(
            screen,
            synthesis_button_rect,
            "資源合成",
            font,
            active=game.synthesis_mode,
            accent=GOLD,
            enabled=synthesis_enabled,
        )

        draw_shadowed_panel(screen, hand_rect, fill=(252, 255, 252), border=LINE)
        draw_wrapped_text_in_rect(
            screen,
            "手牌",
            pygame.Rect(hand_rect.x + 18, hand_rect.y + 12, 180, 30),
            font,
            BLUE,
            max_lines=1,
        )
        for sprite in sprites:
            if sprite.rect.right < width - 16:
                sprite.draw(screen, font)

        if game.synthesis_mode:
            draw_synthesis_panel(screen, active_synthesis_panel_rect, font, game)

        if not game.waiting_for_player and not game.game_over:
            draw_wrapped_text_in_rect(
                screen,
                f"{game.current_player.name} 回合中...",
                pygame.Rect(width * 0.05, height * 0.64, width * 0.45, 30),
                font,
                ACCENT,
                max_lines=1,
            )

        if settings_open and not active_modal:
            draw_settings_panel(screen, settings_rect, font, game)

        if active_modal == "help":
            draw_help_modal(screen, center_modal_rect, font, game, help_scroll)
        elif active_modal == "catalog":
            draw_catalog_modal(screen, catalog_modal_rect(width, height), font, catalog_tab, catalog_selected_card, game)
            if catalog_selected_card:
                draw_card_detail_modal(screen, card_detail_modal_rect(width, height), font, catalog_selected_card, game, catalog_detail_scroll)

        if hand_detail_card:
            draw_card_detail_modal(screen, card_detail_modal_rect(width, height), font, hand_detail_card, game, hand_detail_scroll)

        if game.game_over:
            overlay = pygame.Surface((width, height))
            overlay.set_alpha(215)
            overlay.fill((248, 251, 255))
            screen.blit(overlay, (0, 0))
            result_rect = pygame.Rect(width * 0.25, height * 0.30, width * 0.50, height * 0.34)
            draw_shadowed_panel(screen, result_rect, fill=(255, 255, 252), border=LINE)
            draw_wrapped_text_in_rect(
                screen,
                f"{game.winner} 勝利！",
                pygame.Rect(result_rect.x + 24, result_rect.y + 36, result_rect.width - 48, 82),
                big_font,
                GOLD,
                max_lines=1,
                align="center",
            )
            pygame.draw.rect(screen, GREEN, restart_button_rect, border_radius=8)
            pygame.draw.rect(screen, (25, 118, 73), restart_button_rect, 2, border_radius=8)
            draw_wrapped_text_in_rect(
                screen,
                "再來一局",
                pygame.Rect(
                    restart_button_rect.x + 16,
                    restart_button_rect.y + 8,
                    restart_button_rect.width - 32,
                    restart_button_rect.height - 16,
                ),
                font,
                (255, 255, 255),
                max_lines=1,
                align="center",
                v_align="center",
            )
            draw_wrapped_text_in_rect(
                screen,
                "按 Esc 離開",
                pygame.Rect(result_rect.x + 24, restart_button_rect.bottom + 18, result_rect.width - 48, 34),
                font,
                MUTED,
                max_lines=1,
                align="center",
            )

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
