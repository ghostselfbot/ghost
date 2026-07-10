import os
import sys
import certifi
import multiprocessing
import argparse

sys.setrecursionlimit(10000)
os.environ["SSL_CERT_FILE"] = certifi.where()

if sys.platform == "darwin":
    multiprocessing.set_start_method("fork", force=True)

if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))

from utils.files import get_application_support
from utils.config import Config
from utils import startup_check, check_fonts, console, load_fonts
from bot.controller import BotController


def parse_args():
    parser = argparse.ArgumentParser(description="Ghost selfbot launcher")
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Force CLI mode instead of the GUI",
    )
    return parser.parse_args()

def run_gui():
    from gui.main import GhostGUI

    cfg = Config()
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
        controller.join()
    except KeyboardInterrupt:
        console.info("Exiting.")
        controller.stop()
        controller.join()

def main():
    args = parse_args()
    headless = args.headless

    get_application_support()
    startup_check.check()
    cfg = Config()
    cfg.check()
    load_fonts()

    if headless:
        console.info("Running in headless (CLI) mode.")
        run_cli()
        return

    console.info("Running in GUI mode.")

    if cfg.get_skip_fonts():
        cfg.set_skip_fonts(False)
        run_gui()
    elif check_fonts():
        run_gui()
    else:
        # FontCheckGUI().run()
        load_fonts()
        run_gui()

if __name__ == "__main__":
    main()
