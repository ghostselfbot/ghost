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
        subprocess.run(["open", path], creationflags=subprocess.CREATE_NO_WINDOW)
    elif sys.platform == "win32":
        os.startfile(path)
    else:
        subprocess.run(["xdg-open", path], creationflags=subprocess.CREATE_NO_WINDOW)

def open_file_in_editor(file_path):
    if sys.platform == "darwin":
        subprocess.run(["open", "-a", "TextEdit", file_path], creationflags=subprocess.CREATE_NO_WINDOW)
    elif sys.platform == "win32":
        subprocess.run(["notepad", file_path], creationflags=subprocess.CREATE_NO_WINDOW)
    else:
        subprocess.run(["gedit", file_path], creationflags=subprocess.CREATE_NO_WINDOW)