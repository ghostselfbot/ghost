import json
import os
import threading

from .rich_presence import RichPresence
from .sniper import Sniper
from .theme import Theme
from .token import Token
from utils.defaults import DEFAULT_THEME, DEFAULT_CONFIG
from utils import console
from utils import files

class Config:
    _instance = None
    _lock = threading.Lock()
    _temp_state = {}

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._init()
        return cls._instance

    def get_temp(self, key, default=None):
        """Retrieve a temporary in-memory value (not saved to file)."""
        return self._temp_state.get(key, default)

    def set_temp(self, key, value):
        """Set a temporary in-memory value (not saved to file)."""
        self._temp_state[key] = value

    def set_skip_fonts(self, value=True):
        self.config["skip_font_check"] = value
        self.save()
        
    def get_skip_fonts(self):
        if "skip_font_check" not in self.config:
            self.config["skip_font_check"] = False
            self.save()
        return self.config["skip_font_check"]

    def _init(self):
        self.base_path = files.get_application_support() + "/"
        self.config_file = files.get_config_path()
        self.config = None
        self._load_config()
        self.theme = self.get_theme(self.config["theme"])
        self.subscribers = []
        
        self.tokens_file = files.get_data_path() + "/sensitive/tokens.json"
        self._load_tokens()

    def _load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as f:
                try:
                    self.config = json.load(f)
                except json.JSONDecodeError:
                    self.config = DEFAULT_CONFIG
        else:
            self.config = DEFAULT_CONFIG
            
        if isinstance(self.config["message_settings"]["auto_delete_delay"], str):
            self.config["message_settings"]["auto_delete_delay"] = int(self.config["message_settings"]["auto_delete_delay"])

    def check(self):
        # check if the config file is missing any keys
        for key, value in DEFAULT_CONFIG.items():
            if key not in self.config:
                self.config[key] = value
                
        # check if the theme is missing any keys
        theme = self.get_theme(self.config["theme"])
        
        for key, value in DEFAULT_THEME.items():
            if key not in theme.to_dict():
                theme[key] = value
                
        self.save()

    def save(self, notify=True):
        token = self.get("token")
        self.config["token"] = token.strip()
        
        if isinstance(self.config["theme"], dict):
            self.save_theme_file(self.config["theme_name"], self.config["theme"])
            self.config["theme"] = self.config["theme_name"]
            self.config.pop("theme_name")

        if isinstance(self.config["message_settings"]["auto_delete_delay"], str):
            self.config["message_settings"]["auto_delete_delay"] = int(self.config["message_settings"]["auto_delete_delay"])

        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=4)
        
        self.save_tokens()
        if notify: self.notify_subscribers()

    def get(self, key):
        subkey = None
        if "." in key:
            key, subkey = key.split(".")
            
        value = self.config[key][subkey] if subkey else self.config[key]
        return value.strip() if "token" in key and isinstance(value, str) else value

    def set(self, key, value, save=True):
        subkey = None
        if "." in key:
            key, subkey = key.split(".")

        if subkey:
            self.config[key][subkey] = value
        else:
            self.config[key] = value

        if save:
            self.save()

    def subscribe(self, obj):
        if obj not in self.subscribers:
            print(f"Subscribed {obj}")
            self.subscribers.append(obj)
        print(f"Current Subscribers: {self.subscribers}")

    def unsubscribe(self, obj):
        if obj in self.subscribers:
            print(f"Unsubscribed {obj}")
            self.subscribers.remove(obj)

    def notify_subscribers(self):
        print("Notifying subscribers")
        for obj in self.subscribers:
            print(f"Checking subscriber: {type(obj)} - {obj}")
            if hasattr(obj, "refresh_config"):
                print(f"Refreshing {obj}")
                obj.refresh_config()

    def get_theme_file(self, theme):
        return json.load(open(self.base_path + f"themes/{theme}.json")) if os.path.exists(self.base_path + f"themes/{theme}.json") else None

    def save_theme_file(self, theme_name, new_obj):
        json.dump(new_obj, open(self.base_path + f"themes/{theme_name}.json", "w"), indent=4)

    def get_theme(self, theme_name):
        if not os.path.exists(self.base_path + f"themes/{theme_name}.json"):
            return Theme(self, **DEFAULT_THEME)

        theme_obj = self.get_theme_file(theme_name)
        theme_obj["name"] = theme_name
        return Theme(self, **theme_obj)

    def set_theme(self, theme_name, save=True):
        self.config["theme"] = theme_name
        if save: self.save()
        self.theme = self.get_theme(theme_name)

    def delete_theme(self, theme_name):
        if self.theme.name == theme_name:
            self.set_theme("ghost")

        os.remove(self.base_path + f"themes/{theme_name}.json")
        self.save()

    def get_themes(self):
        return [
            Theme(self, name=theme.replace(".json", ""), **self.get_theme_file(theme.replace(".json", "")))
            for theme in os.listdir(files.get_themes_path()) if theme.endswith(".json")
        ]

    def get_sniper(self, sniper):
        if sniper not in self.config["snipers"]:
            return None

        obj = self.config["snipers"].get(sniper)
        obj["name"] = sniper
        return Sniper(config=self, **obj)

    def get_snipers(self):
        return [
            Sniper(config=self, **{**self.config["snipers"][sniper], "name": sniper})
            for sniper in self.config["snipers"]
        ]

    def get_session_spoofing(self):
        return self.config["session_spoofing"]["enabled"], self.config["session_spoofing"]["device"]

    def set_session_spoofing(self, enabled, device):
        self.config["session_spoofing"]["enabled"] = enabled
        self.config["session_spoofing"]["device"] = device
        self.save()

    def get_rich_presence(self):
        return RichPresence(config=self, **self.config["rich_presence"])

    def create_theme(self, theme_name):
        if os.path.exists(self.base_path + f"themes/{theme_name}.json"):
            return False

        theme_name = theme_name.replace(" ", "_")

        with open(self.base_path + f"themes/{theme_name}.json", "w") as f:
            json.dump(DEFAULT_THEME, f, indent=4)

        return Theme(self, name=theme_name, **DEFAULT_THEME)

    def add_command_history(self, command_string):
        os.makedirs(self.base_path + "data/cache", exist_ok=True)
        
        with open(self.base_path + "data/cache/command_history.txt", "a") as f:
            f.write(f"{console.get_formatted_time()}|{command_string}\n")

    def get_command_history(self):
        os.makedirs(self.base_path + "data/cache", exist_ok=True)
        
        if not os.path.exists(self.base_path + "data/cache/command_history.txt"):
            open(self.base_path + "data/cache/command_history.txt", "w").close()

        with open(self.base_path + "data/cache/command_history.txt", "r") as f:
            return [tuple(line.strip().split("|", 1)) for line in f.readlines()]

    def _load_tokens(self):
        if os.path.exists(self.tokens_file):
            with open(self.tokens_file, "r") as f:
                self.tokens = [Token(**token) for token in json.load(f)]
        else:
            self.tokens = []
    
    def get_token(self, id):
        for token in self.tokens:
            if token.id == id:
                return token
    
    def get_tokens(self):
        return self.tokens
    
    def save_tokens(self):
        with open(self.tokens_file, "w") as f:
            json.dump([token.to_dict() for token in self.tokens], f, indent=4)
    
    def add_token(self, token, username, id):
        for t in self.tokens:
            if t.token == token:
                if t.username != username:
                    t.username = username
                if t.id != id:
                    t.id = id
                self.save_tokens()
                return False
        
        self.tokens.append(Token(token, username, id))
        self.save_tokens()
        return True

    def get_scripts(self):
        script_files = os.listdir(files.get_scripts_path())
        return [script for script in script_files if script.endswith(".py")]

    @staticmethod
    def get_python_path():
        return os.path.dirname(os.path.realpath(__file__))

    @staticmethod
    def quit():
        exit()
