import os
import sys
import certifi
import multiprocessing

os.environ["SSL_CERT_FILE"] = certifi.where()

HEADLESS = "DISPLAY" not in os.environ and sys.platform == "linux"

if sys.platform == "darwin":
    multiprocessing.set_start_method("fork", force=True)

if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))

from utils.files import get_application_support
from utils.config import Config
from utils import startup_check, check_fonts, console, load_fonts
from bot.controller import BotController

if not HEADLESS:
    from gui.main import GhostGUI
    from gui.font_check import FontCheckGUI

def install_fonts_no_gui():
    load_fonts()
    os.execl(sys.executable, sys.executable, *sys.argv)

def run_gui():
    controller = BotController()
    GhostGUI(controller).run()

def run_cli():
    startup_check.check()
    cfg = Config()

    token = cfg.get("token")
    if not token:
        console.error("No token found. Please enter one below.")
        token = input("> ")
        cfg.set("token", token)
        cfg.save()

    console.info("Starting bot.")
    controller = BotController()
    controller.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        console.info("Exiting.")

def main():
    get_application_support()
    startup_check.check()
    cfg = Config()
    cfg.check()

    if HEADLESS:
        console.info("Running in headless (CLI) mode.")
        run_cli()
        return

    console.info("Running in GUI mode.")

    if cfg.get_skip_fonts():
        if os.path.exists(os.path.join(get_application_support(), "INSTALL_FONTS_NO_GUI")):
            console.info("Installing fonts without GUI.")
            install_fonts_no_gui()
        else:
            console.info("Skipping font installation as per user preference.")
            
        cfg.set_skip_fonts(False)
        run_gui()
    elif check_fonts():
        run_gui()
    else:
        FontCheckGUI().run()
        run_gui()

if __name__ == "__main__":
    main()
