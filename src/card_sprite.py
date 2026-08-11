import pygame

from text_fit import draw_text_in_rect
from ui_text import card_type_label

CARD_WIDTH = 140
CARD_HEIGHT = 180

TYPE_COLORS = {
    "resource": (138, 184, 92),
    "structure": (77, 144, 211),
    "action": (231, 101, 74),
    "defense": (56, 111, 208),
    "environment": (91, 108, 132),
}


class CardSprite:
    def __init__(self, card, x, y, selected=False, synthesis_selected=False):
        self.card = card
        self.selected = selected
        self.synthesis_selected = synthesis_selected
        self.rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

    def draw(self, screen, font):
        accent = TYPE_COLORS.get(self.card.type, (96, 126, 160))
        fill = (255, 255, 248)
        border = (245, 184, 58) if self.synthesis_selected else accent if self.selected else (205, 217, 231)
        border_width = 5 if self.synthesis_selected else 4 if self.selected else 1

        shadow = pygame.Surface((CARD_WIDTH + 8, CARD_HEIGHT + 8), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (46, 76, 116, 32), pygame.Rect(4, 5, CARD_WIDTH, CARD_HEIGHT), border_radius=8)
        screen.blit(shadow, (self.rect.x, self.rect.y))
        pygame.draw.rect(screen, fill, self.rect, border_radius=8)
        pygame.draw.rect(screen, border, self.rect, border_width, border_radius=8)

        draw_text_in_rect(
            screen,
            self.card.zh_name,
            pygame.Rect(self.rect.x + 10, self.rect.y + 14, CARD_WIDTH - 20, 34),
            font,
            (0, 0, 0),
            max_lines=2,
        )
        draw_text_in_rect(
            screen,
            self.card.en_name,
            pygame.Rect(self.rect.x + 10, self.rect.y + 54, CARD_WIDTH - 20, 44),
            font,
            (45, 58, 78),
            max_lines=2,
        )
        pygame.draw.circle(screen, (185, 194, 183), (self.rect.centerx, self.rect.y + 92), 4)
        pygame.draw.line(screen, (185, 194, 183), (self.rect.centerx, self.rect.y + 96), (self.rect.centerx, self.rect.y + 128), 2)
        pygame.draw.circle(screen, (185, 194, 183), (self.rect.centerx - 14, self.rect.y + 108), 4)
        pygame.draw.circle(screen, (185, 194, 183), (self.rect.centerx + 14, self.rect.y + 116), 4)
        pygame.draw.line(screen, (185, 194, 183), (self.rect.centerx, self.rect.y + 104), (self.rect.centerx - 14, self.rect.y + 108), 2)
        pygame.draw.line(screen, (185, 194, 183), (self.rect.centerx, self.rect.y + 116), (self.rect.centerx + 14, self.rect.y + 116), 2)
        draw_text_in_rect(
            screen,
            card_type_label(self.card),
            pygame.Rect(self.rect.x + 10, self.rect.y + 136, CARD_WIDTH - 20, 28),
            font,
            (65, 78, 96),
            max_lines=1,
        )
