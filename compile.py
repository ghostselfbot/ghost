import os
import platform
import subprocess
import plistlib

from utils.config import VERSION


def patch_macos_plist(app_name):
    plist_path = os.path.join("dist", f"{app_name}.app", "Contents", "Info.plist")

    if not os.path.exists(plist_path):
        print("Info.plist not found, skipping version patch")
        return

    with open(plist_path, "rb") as f:
        plist = plistlib.load(f)

    plist["CFBundleShortVersionString"] = VERSION  # About menu
    plist["CFBundleVersion"] = VERSION              # build number

    with open(plist_path, "wb") as f:
        plistlib.dump(plist, f)

    print(f"Patched Info.plist with version {VERSION}")


def build():
    system = platform.system()

    name = "Ghost"
    entry_script = "ghost.py"
    icon = "data/icon-win.png" if system == "Windows" else "data/icon.png"

    args = [
        "pyinstaller",
        f"--name={name}",
        "--onefile",
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
        patch_macos_plist(name)


if __name__ == "__main__":
    build()
