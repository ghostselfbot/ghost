import os
import platform
import subprocess
import plistlib

from utils.config import VERSION

def sign_macos_app(path):
    print(f"🔏 Signing macOS app at {path}...")
    subprocess.run([
        "codesign",
        "--deep",
        "--force",
        "--verbose",
        "--sign",
        "-",
        path
    ], check=True)

def build():
    system = platform.system()

    name = "Ghost"
    entry_script = "ghost.py"
    icon = "data/icon-win.png" if system == "Windows" else "data/icon.png"

    args = [
        "pyinstaller",
        f"--name={name}",
        "--onefile",
        "--clean",
        "--noconfirm",
        "--windowed",
        "--noconsole",
        f"--icon={icon}",
        "--hidden-import=discord",
        "--hidden-import=discord.ext.commands",
        "--hidden-import=PIL.ImageTk",
        "--hidden-import=PIL._tkinter_finder",
        "--collect-submodules=discord",
        entry_script
    ]

    if system == "Windows":
        args += [
            "--paths=.venv\\Lib\\site-packages",
            "--add-data=data\\*;data",
            "--add-data=data\\fonts\\*;data/fonts",
            "--add-data=data\\icons\\*;data/icons"
        ]
    else:
        args += [
            "--paths=.venv/lib/python3.10/site-packages",
            "--add-data=data/*:data",
            "--add-data=data/fonts/*:data/fonts",
            "--add-data=data/icons/*:data/icons",
            "--osx-bundle-identifier=fun.benny.ghost"
        ]

    print(f"🔨 Building Ghost {VERSION} for {system}...")
    subprocess.run(args, check=True)

    if system == "Darwin":
        app_path = os.path.join("dist", "Ghost.app")
        sign_macos_app(app_path)

if __name__ == "__main__":
    build()
