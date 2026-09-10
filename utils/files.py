import os
import sys
import subprocess

def resource_path(relative_path):
    """ Get the absolute path to a resource, handling PyInstaller builds. """
    if getattr(sys, 'frozen', False):  # Detect if running as a PyInstaller bundle
        base_path = sys._MEIPASS  # Extracted temp folder
    else:
        base_path = os.path.abspath(".")  # Normal script execution

    return os.path.join(base_path, relative_path)

APPLICATION_SUPPORT = None

def get_application_support():
    global APPLICATION_SUPPORT

    if APPLICATION_SUPPORT is not None:
        return APPLICATION_SUPPORT

    if sys.platform == "darwin":
        APPLICATION_SUPPORT = os.path.expanduser("~/Library/Application Support/Ghost")
    elif sys.platform == "win32":
        APPLICATION_SUPPORT = os.path.join(os.getenv("APPDATA"), "Ghost")
    else:
        APPLICATION_SUPPORT = os.path.expanduser("~/.config/ghost")

    if not os.path.exists(APPLICATION_SUPPORT):
        os.makedirs(APPLICATION_SUPPORT)

    return APPLICATION_SUPPORT

def get_data_path():
    return os.path.join(get_application_support(), "data")

def get_cache_path():
    return os.path.join(get_application_support(), "data/cache")

def get_themes_path():
    return os.path.join(get_application_support(), "themes")

def get_scripts_path():
    return os.path.join(get_application_support(), "scripts")

def get_config_path():
    return os.path.join(get_application_support(), "config.json")

def get_theme_path(theme_name):
    return os.path.join(get_themes_path(), f"{theme_name}.json")

def open_path_in_explorer(path):
    path += "/"
    
    if sys.platform == "darwin":
        subprocess.run(["open", path])
    elif sys.platform == "win32":
        os.startfile(path)
    else:
        subprocess.run(["xdg-open", path], creationflags=subprocess.CREATE_NO_WINDOW)

def open_file_in_editor(file_path):
    if sys.platform == "darwin":
        subprocess.run(["open", "-a", "TextEdit", file_path])
    elif sys.platform == "win32":
        subprocess.run(["notepad", file_path], creationflags=subprocess.CREATE_NO_WINDOW)
    else:
        subprocess.run(["gedit", file_path])
        
def set_launch_on_startup(enabled):
    """Register or remove Ghost from OS startup. Returns (success, error_message)."""
    import traceback
    try:
        if sys.platform == "win32":
            return _set_startup_windows(enabled)
        elif sys.platform == "darwin":
            return _set_startup_macos(enabled)
        else:
            return _set_startup_linux(enabled)
    except Exception as e:
        return False, str(e)

def _set_startup_windows(enabled):
    try:
        import winreg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)

        if getattr(sys, 'frozen', False):
            exe_path = sys.executable
        else:
            script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            ghost_path = os.path.join(script_dir, "ghost.py")
            exe_path = f'cmd.exe /c "cd /d "{script_dir}" && python "{ghost_path}"'

        app_name = "GhostSelfbot"

        if enabled:
            winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, exe_path)
        else:
            try:
                winreg.DeleteValue(key, app_name)
            except FileNotFoundError:
                pass

        winreg.CloseKey(key)
        return True, None
    except Exception as e:
        return False, str(e)

def _set_startup_macos(enabled):
    try:
        plist_dir = os.path.expanduser("~/Library/LaunchAgents")
        plist_path = os.path.join(plist_dir, "com.ghost.selfbot.plist")

        if not enabled:
            if os.path.exists(plist_path):
                os.remove(plist_path)
            return True, None

        if getattr(sys, 'frozen', False):
            exe_path = sys.executable
        else:
            exe_path = sys.executable

        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.ghost.selfbot</string>
    <key>ProgramArguments</key>
    <array>
        <string>{exe_path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>WorkingDirectory</key>
    <string>{os.path.dirname(exe_path)}</string>
</dict>
</plist>"""

        os.makedirs(plist_dir, exist_ok=True)
        with open(plist_path, "w") as f:
            f.write(plist_content)
        return True, None
    except Exception as e:
        return False, str(e)

def _set_startup_linux(enabled):
    try:
        autostart_dir = os.path.expanduser("~/.config/autostart")
        desktop_path = os.path.join(autostart_dir, "ghost-selfbot.desktop")

        if not enabled:
            if os.path.exists(desktop_path):
                os.remove(desktop_path)
            return True, None

        if getattr(sys, 'frozen', False):
            exec_path = sys.executable
        else:
            exec_path = f'{sys.executable} {os.path.abspath("ghost.py")}'

        desktop_content = f"""[Desktop Entry]
Type=Application
Name=Ghost Selfbot
Exec={exec_path}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
"""

        os.makedirs(autostart_dir, exist_ok=True)
        with open(desktop_path, "w") as f:
            f.write(desktop_content)
        return True, None
    except Exception as e:
        return False, str(e)