import json
from enum import Enum

from utils import Config

class Style(Enum):
    WINDOW_BORDER = "#12121c"
    SIDEBAR_SELECTED = "#181722"
    ENTRY_BG = "#1b1b2b"
    ENTRY_FG = "#ffffff"
    SETTINGS_PILL_HOVER = "#252534"
    SETTINGS_PILL_SELECTED = "#2d2d41"
    DROPDOWN_OPTION_HOVER = "#20202f"
    DARK_GREY = "#7f7f92"
    LIGHT_GREY = "#cbcbd2"
    PRIMARY_BTN_HOVER = "#322bef"
    MAC_TITLEBAR_INACTIVE = "#454256"
    TOOL_HOVER = "#1c1c2e"
    
DARK_THEME = {
    "WINDOW_BORDER": "#12121c",
    "SIDEBAR_SELECTED": "#181722",
    "ENTRY_BG": "#1b1b2b",
    "ENTRY_FG": "#ffffff",
    "SETTINGS_PILL_HOVER": "#252534",
    "SETTINGS_PILL_SELECTED": "#2d2d41",
    "DROPDOWN_OPTION_HOVER": "#20202f",
    "DARK_GREY": "#7f7f92",
    "LIGHT_GREY": "#cbcbd2",
    "PRIMARY_BTN_HOVER": "#322bef",
    "MAC_TITLEBAR_INACTIVE": "#454256",
    "TOOL_HOVER": "#1c1c2e",
}

GREEN_THEME = {
    "WINDOW_BORDER": "#0f1512",
    "SIDEBAR_SELECTED": "#141c18",
    "ENTRY_BG": "#17221c",
    "ENTRY_FG": "#ffffff",
    "SETTINGS_PILL_HOVER": "#1c2a22",
    "SETTINGS_PILL_SELECTED": "#213329",
    "DROPDOWN_OPTION_HOVER": "#1a261f",
    "DARK_GREY": "#7f9288",
    "LIGHT_GREY": "#cbd2cd",
    "PRIMARY_BTN_HOVER": "#1ecb5c",
    "MAC_TITLEBAR_INACTIVE": "#2f3d36",
    "TOOL_HOVER": "#162019"
}

RED_THEME = {
    "WINDOW_BORDER": "#150d10",
    "SIDEBAR_SELECTED": "#1c1215",
    "ENTRY_BG": "#22161a",
    "ENTRY_FG": "#ffffff",
    "SETTINGS_PILL_HOVER": "#2a1a1f",
    "SETTINGS_PILL_SELECTED": "#331f26",
    "DROPDOWN_OPTION_HOVER": "#26161b",
    "DARK_GREY": "#927f84",
    "LIGHT_GREY": "#d2cbd0",
    "PRIMARY_BTN_HOVER": "#ff4d4d",
    "MAC_TITLEBAR_INACTIVE": "#3d2f34",
    "TOOL_HOVER": "#201317"
}

YELLOW_THEME = {
    "WINDOW_BORDER": "#151108",
    "SIDEBAR_SELECTED": "#1c160c",
    "ENTRY_BG": "#221c10",
    "ENTRY_FG": "#ffffff",
    "SETTINGS_PILL_HOVER": "#2a2214",
    "SETTINGS_PILL_SELECTED": "#332a18",
    "DROPDOWN_OPTION_HOVER": "#261f12",
    "DARK_GREY": "#928b7f",
    "LIGHT_GREY": "#d2cec3",
    "PRIMARY_BTN_HOVER": "#ffcc33",
    "MAC_TITLEBAR_INACTIVE": "#3d3524",
    "TOOL_HOVER": "#201a0f"
}

PINK_THEME = {
    "WINDOW_BORDER": "#150d12",
    "SIDEBAR_SELECTED": "#1c1218",
    "ENTRY_BG": "#22161e",
    "ENTRY_FG": "#ffffff",
    "SETTINGS_PILL_HOVER": "#2a1a23",
    "SETTINGS_PILL_SELECTED": "#331f2a",
    "DROPDOWN_OPTION_HOVER": "#26161f",
    "DARK_GREY": "#92848f",
    "LIGHT_GREY": "#d2cbd0",
    "PRIMARY_BTN_HOVER": "#ff66b3",
    "MAC_TITLEBAR_INACTIVE": "#3d2f38",
    "TOOL_HOVER": "#20131a"
}

PURPLE_THEME = {
    "WINDOW_BORDER": "#120d18",
    "SIDEBAR_SELECTED": "#171224",
    "ENTRY_BG": "#1d1826",
    "ENTRY_FG": "#ffffff",
    "SETTINGS_PILL_HOVER": "#231c30",
    "SETTINGS_PILL_SELECTED": "#2d2340",
    "DROPDOWN_OPTION_HOVER": "#20192b",
    "DARK_GREY": "#8b7f92",
    "LIGHT_GREY": "#d0cbd2",
    "PRIMARY_BTN_HOVER": "#a07cff",
    "MAC_TITLEBAR_INACTIVE": "#352f3d",
    "TOOL_HOVER": "#1a1422"
}

ORANGE_THEME = {
    "WINDOW_BORDER": "#151008",
    "SIDEBAR_SELECTED": "#1c140c",
    "ENTRY_BG": "#22170f",
    "ENTRY_FG": "#ffffff",
    "SETTINGS_PILL_HOVER": "#2a1d14",
    "SETTINGS_PILL_SELECTED": "#332318",
    "DROPDOWN_OPTION_HOVER": "#261a12",
    "DARK_GREY": "#92877f",
    "LIGHT_GREY": "#d2cdc8",
    "PRIMARY_BTN_HOVER": "#ff8c42",
    "MAC_TITLEBAR_INACTIVE": "#3d3324",
    "TOOL_HOVER": "#20160f"
}

BLUE_THEME = {
    "WINDOW_BORDER": "#0f141c",
    "SIDEBAR_SELECTED": "#141b27",
    "ENTRY_BG": "#18202c",
    "ENTRY_FG": "#ffffff",
    "SETTINGS_PILL_HOVER": "#1c2533",
    "SETTINGS_PILL_SELECTED": "#223049",
    "DROPDOWN_OPTION_HOVER": "#1a2230",
    "DARK_GREY": "#7f8ea3",
    "LIGHT_GREY": "#cbd2da",
    "PRIMARY_BTN_HOVER": "#4da3ff",
    "MAC_TITLEBAR_INACTIVE": "#2f3a4d",
    "TOOL_HOVER": "#16202b"
}

themes = {
    "dark": {
        "style": DARK_THEME,
        "ttk_theme": "ghost"
    },
    "red": {
        "style": RED_THEME,
        "ttk_theme": "red"
    },
    "green": {
        "style": GREEN_THEME,
        "ttk_theme": "green"
    },
    "blue": {
        "style": BLUE_THEME,
        "ttk_theme": "blue_vibrant"
    },
    "yellow": {
        "style": YELLOW_THEME,
        "ttk_theme": "yellow"
    },
    "orange": {
        "style": ORANGE_THEME,
        "ttk_theme": "orange"
    },
    "pink": {
        "style": PINK_THEME,
        "ttk_theme": "pink"
    },
    "purple": {
        "style": PURPLE_THEME,
        "ttk_theme": "purple"
    },
}
