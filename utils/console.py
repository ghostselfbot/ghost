import os
import sys
import logging
import datetime
import colorama
import pystyle

from . import config

# handler = logging.FileHandler(filename='ghost.log', encoding='utf-8', mode='w')
gui = None
banner = f"""  ▄████  ██░ ██  ▒█████    ██████ ▄▄▄█████▓
 ██▒ ▀█▒▓██░ ██▒▒██▒  ██▒▒██    ▒ ▓  ██▒ ▓▒
▒██░▄▄▄░▒██▀▀██░▒██░  ██▒░ ▓██▄   ▒ ▓██░ ▒░
░▓█  ██▓░▓█ ░██ ▒██   ██░  ▒   ██▒░ ▓██▓ ░ 
░▒▓███▀▒░▓█▒░██▓░ ████▓▒░▒██████▒▒  ▒██▒ ░ 
 ░▒   ▒  ▒ ░░▒░▒░ ▒░▒░▒░ ▒ ▒▓▒ ▒ ░  ▒ ░░   
  ░   ░  ▒ ░▒░ ░  ░ ▒ ▒░ ░ ░▒  ░ ░    ░    
░ ░   ░  ░  ░░ ░░ ░ ░ ▒  ░  ░  ░    ░      
      ░  ░  ░  ░    ░ ░        ░           
                                           
"""

def set_gui(ghost_gui):
    global gui
    gui = ghost_gui

def log_to_gui(prefix, text):
    if gui and gui.console:
        gui.run_on_main_thread(gui.console.add_log, prefix, text)

def log_sniper_to_gui(sniper_obj):
    if gui and gui.console:
        gui.run_on_main_thread(gui.console.add_sniper, sniper_obj)

def clear_gui():
    if gui and gui.console:
        gui.run_on_main_thread(gui.console.clear)

def clear():
    clear_gui()
    try:
        os.system("cls" if sys.platform == "win32" else "clear")
    except:
        pass

def resize(columns, rows):
    try:
        command = f"mode con cols={columns} lines={rows}" if sys.platform == "win32" else f"echo '\033[8;{rows};{columns}t'"
        os.system(command)
    except:
        pass

def print_banner():
    copyright_ = f"( Ghost v{config.VERSION} )"
    total_width = os.get_terminal_size()[0]
    copyright_length = len(copyright_)
    dashes_length = (total_width - copyright_length) // 2
    dashes = "—" * dashes_length
    banner_line = f"{dashes}{copyright_}{dashes}"

    if len(banner_line) < total_width:
        banner_line += "—"

    print(colorama.Fore.LIGHTBLUE_EX + colorama.Style.BRIGHT)
    print(pystyle.Center.XCenter(banner))
    print(f"{colorama.Style.NORMAL}{colorama.Fore.WHITE}")
    print(pystyle.Center.XCenter(config.MOTD))
    print()
    print(f"{colorama.Fore.BLUE}{banner_line}")
    print(f"{colorama.Style.RESET_ALL}")

get_formatted_time = lambda: datetime.datetime.now().strftime("%H:%M:%S")
print_colour       = lambda colour, text: print(colour + text + colorama.Style.RESET_ALL)

def _log_and_print(prefix, colour, text, gui_log=True):
    # print(f"[{prefix}] {text}")
    print(f"{colorama.Style.NORMAL}{colorama.Fore.WHITE}[{get_formatted_time()}] {colour}{colorama.Style.BRIGHT}[{prefix}]{colorama.Style.RESET_ALL} {text}")
    if gui_log:
        try:
            log_to_gui(prefix, text)
        except:
            pass

print_cmd     = lambda text: _log_and_print("COMMAND", colorama.Fore.LIGHTBLUE_EX, text)
print_info    = lambda text: _log_and_print("INFO", colorama.Fore.LIGHTCYAN_EX, text)
print_success = lambda text: _log_and_print("SUCCESS", colorama.Fore.LIGHTGREEN_EX, text)
print_error   = lambda text: _log_and_print("ERROR", colorama.Fore.LIGHTRED_EX, text)
print_warning = lambda text: _log_and_print("WARNING", colorama.Fore.LIGHTYELLOW_EX, text)
print_cli     = lambda text: _log_and_print("CLI", colorama.Fore.LIGHTMAGENTA_EX, text)
print_rpc     = lambda text: _log_and_print("RPC", colorama.Fore.LIGHTMAGENTA_EX, text)
print_captcha = lambda text: _log_and_print("CAPTCHA", colorama.Fore.LIGHTYELLOW_EX, text)
print_nitro   = lambda text: _log_and_print("NITRO", colorama.Fore.LIGHTBLUE_EX, text)

cmd     = lambda text: print_cmd(text)
info    = lambda text: print_info(text)
success = lambda text: print_success(text)
error   = lambda text: print_error(text)
warning = lambda text: print_warning(text)
cli     = lambda text: print_cli(text)
rpc     = lambda text: print_rpc(text)

def print_sniper(sniper, title, description, success=True):
    log_sniper_to_gui({"type": sniper, "title": title, "description": description})
    colour = colorama.Fore.LIGHTGREEN_EX if success else colorama.Fore.LIGHTRED_EX
    _log_and_print(sniper.upper(), colour, title, gui_log=False)
    for key, value in description.items():
        print(f"{' '*10} {colorama.Fore.LIGHTYELLOW_EX}{colorama.Style.NORMAL}{key}: {colorama.Style.RESET_ALL}{value}")
