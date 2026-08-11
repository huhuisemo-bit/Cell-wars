import re

import pygame

CJK_RE = re.compile(r"[\u3400-\u9fff]")
MIN_READABLE_SCALE = 0.82


def text_tokens(text):
    tokens = []
    word = ""
    for char in str(text):
        if char == "\n":
            if word:
                tokens.append(word)
                word = ""
            tokens.append("\n")
            continue
        if char.isspace():
            if word:
                tokens.append(word)
                word = ""
            continue
        if CJK_RE.match(char):
            if word:
                tokens.append(word)
                word = ""
            tokens.append(char)
            continue
        word += char
    if word:
        tokens.append(word)
    return tokens


def token_join(left, token):
    if not left:
        return token
    if token == "\n":
        return left
    if CJK_RE.match(left[-1]) or CJK_RE.match(token[0]):
        return left + token
    return left + " " + token


def wrap_text(text, font, max_width):
    lines = []
    current = ""

    for token in text_tokens(text):
        if token == "\n":
            lines.append(current)
            current = ""
            continue
        candidate = token_join(current, token)
        if current and font.size(candidate)[0] > max_width:
            lines.append(current)
            current = token
        else:
            current = candidate

    if current:
        lines.append(current)
    return lines or [""]


def ellipsize_line(text, font, max_width):
    if font.size(text)[0] <= max_width:
        return text
    ellipsis = "…"
    if font.size(ellipsis)[0] > max_width:
        return ""
    result = ""
    for token in text_tokens(text):
        candidate = token_join(result, token)
        if font.size(candidate + ellipsis)[0] > max_width:
            break
        result = candidate
    if result:
        return result + ellipsis
    # Very long English words should not be split in normal wrapping, but a
    # final clipped label is better than spilling outside the UI frame.
    for i in range(len(text), 0, -1):
        candidate = text[:i] + ellipsis
        if font.size(candidate)[0] <= max_width:
            return candidate
    return ellipsis


def fit_lines(text, font, rect, max_lines=None):
    lines = wrap_text(text, font, rect.width)
    if max_lines and len(lines) > max_lines:
        kept = lines[:max_lines]
        kept[-1] = kept[-1] + "…"
        lines = kept
    return lines


def draw_text_in_rect(
    screen,
    text,
    rect,
    font,
    color,
    *,
    max_lines=None,
    align="left",
    v_align="top",
    line_gap=2,
):
    rect = pygame.Rect(rect)
    lines = fit_lines(text, font, rect, max_lines=max_lines)
    rendered = [font.render(line, True, color) for line in lines]
    line_height = max(1, font.get_linesize())
    total_height = len(rendered) * line_height + max(0, len(rendered) - 1) * line_gap
    max_line_width = max((surface.get_width() for surface in rendered), default=1)
    width_scale = rect.width / max(1, max_line_width)
    height_scale = rect.height / max(1, total_height)
    scale = min(1, width_scale, height_scale)
    if scale < MIN_READABLE_SCALE and height_scale >= MIN_READABLE_SCALE:
        scale = MIN_READABLE_SCALE
        lines = [ellipsize_line(line, font, int(rect.width / scale)) for line in lines]
        rendered = [font.render(line, True, color) for line in lines]
        total_height = len(rendered) * line_height + max(0, len(rendered) - 1) * line_gap

    scaled_height = total_height * scale
    if v_align == "center" and scaled_height <= rect.height:
        y = rect.y + (rect.height - scaled_height) / 2
    elif v_align == "bottom":
        y = rect.bottom - scaled_height
    else:
        y = rect.y

    previous_clip = screen.get_clip()
    screen.set_clip(rect)
    for surface in rendered:
        width = max(1, int(surface.get_width() * scale))
        height = max(1, int(surface.get_height() * scale))
        if scale < 1:
            surface = pygame.transform.smoothscale(surface, (width, height))

        if align == "center":
            x = rect.x + (rect.width - width) / 2
        elif align == "right":
            x = rect.right - width
        else:
            x = rect.x

        screen.blit(surface, (int(x), int(y)))
        y += (line_height + line_gap) * scale
    screen.set_clip(previous_clip)


def draw_wrapped_text_in_rect(
    screen,
    text,
    rect,
    font,
    color,
    *,
    max_lines=None,
    align="left",
    v_align="top",
    line_gap=2,
):
    rect = pygame.Rect(rect)
    lines = wrap_text(text, font, rect.width)
    available_lines = max(1, (rect.height + line_gap) // (font.get_linesize() + line_gap))
    limit = min(max_lines or available_lines, available_lines)
    lines = lines[:limit]
    if len(lines) == limit and len(wrap_text(text, font, rect.width)) > limit:
        lines[-1] = ellipsize_line(lines[-1], font, rect.width)

    line_height = font.get_linesize()
    total_height = len(lines) * line_height + max(0, len(lines) - 1) * line_gap
    if v_align == "center" and total_height <= rect.height:
        y = rect.y + (rect.height - total_height) / 2
    elif v_align == "bottom" and total_height <= rect.height:
        y = rect.bottom - total_height
    else:
        y = rect.y

    previous_clip = screen.get_clip()
    screen.set_clip(rect)
    for line in lines:
        if y + line_height > rect.bottom:
            break
        line = ellipsize_line(line, font, rect.width)
        surface = font.render(line, True, color)
        if align == "center":
            x = rect.x + (rect.width - surface.get_width()) / 2
        elif align == "right":
            x = rect.right - surface.get_width()
        else:
            x = rect.x
        screen.blit(surface, (int(x), int(y)))
        y += line_height + line_gap
    screen.set_clip(previous_clip)
