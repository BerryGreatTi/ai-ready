"""Theme constants for AIReady GUI."""

import sys

# Window
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 520
PADDING = 28
PADDING_SM = 14
BUTTON_HEIGHT = 42
CARD_HEIGHT = 90

# Platform-aware font families
if sys.platform == "darwin":
    _FONT_FAMILY = "Helvetica Neue"
    _FONT_CODE_FAMILY = "Menlo"
else:
    _FONT_FAMILY = "Segoe UI"
    _FONT_CODE_FAMILY = "Consolas"

# Fonts
FONT_HERO = (_FONT_FAMILY, 36, "bold")
FONT_TITLE = (_FONT_FAMILY, 20, "bold")
FONT_SUBTITLE = (_FONT_FAMILY, 14)
FONT_BODY = (_FONT_FAMILY, 13)
FONT_SMALL = (_FONT_FAMILY, 11)
FONT_CARD_TITLE = (_FONT_FAMILY, 15, "bold")
FONT_CODE = (_FONT_CODE_FAMILY, 14, "bold")

# Colors - accent
COLOR_PRIMARY = "#6366f1"
COLOR_PRIMARY_HOVER = "#4f46e5"
COLOR_PRIMARY_LIGHT = "#818cf8"

# Colors - status
COLOR_SUCCESS = "#22c55e"
COLOR_ERROR = "#ef4444"
COLOR_WARNING = "#f59e0b"
COLOR_RUNNING = "#6366f1"

# Colors - neutral
COLOR_MUTED = "#9ca3af"
COLOR_CARD_BG = ("gray92", "gray17")
COLOR_CARD_BORDER = ("gray80", "gray30")
COLOR_CARD_SELECTED = "#6366f1"
