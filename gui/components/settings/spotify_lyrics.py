import json
import os

import ttkbootstrap as ttk

from gui.components import RoundedButton, RoundedSwitch, SettingsPanel
from utils.files import get_application_support
from utils.spotify_lyrics import SpotifyLyricsService


class SpotifyLyricsPanel(SettingsPanel):
    def __init__(self, root, parent, images, config, width=None):
        super().__init__(root, parent, "Spotify Lyrics", images.get("rich_presence"), width=width, collapsed=False)
        self.cfg = config
        self.service = None
        self.entries = {}
        self.auth_button = None
        self.settings_path = os.path.join(get_application_support(), "lyrics", "settings.json")
        self.lyrics_settings = self._load_settings()

    def _load_settings(self):
        try:
            with open(self.settings_path, "r") as settings_file:
                return json.load(settings_file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "credentials": {},
                "view": {"timestamp": True, "label": True},
                "timings": {"sendTimeOffset": 500, "enableAutooffset": True, "autooffset": 3},
                "update": {"enableAutoupdate": True},
            }

    def _credential(self, key, default=""):
        return self.lyrics_settings.get("credentials", {}).get(key, default)

    def _save_settings(self):
        credentials = self.lyrics_settings.setdefault("credentials", {})
        for key, entry in self.entries.items():
            credentials[key] = entry.get()

        view = self.lyrics_settings.setdefault("view", {})
        view["timestamp"] = self.timestamp_entry.instate(["selected"])
        view["label"] = self.label_entry.instate(["selected"])

        os.makedirs(os.path.dirname(self.settings_path), exist_ok=True)
        with open(self.settings_path, "w") as settings_file:
            json.dump(self.lyrics_settings, settings_file, indent=4)
        self.status_label.configure(text="Lyrics settings saved.")

    def _start(self):
        self._save_settings()
        if self.service and self.service.thread and self.service.thread.is_alive():
            self.status_label.configure(text="Spotify Lyrics is already running.")
            return

        self.service = SpotifyLyricsService(
            self.lyrics_settings.get("credentials", {}),
            show_timestamp=self.lyrics_settings.get("view", {}).get("timestamp", True),
            show_label=self.lyrics_settings.get("view", {}).get("label", True),
            status_callback=lambda message: self.root.after(0, lambda: self.status_label.configure(text=message)),
        )
        self.service.start()

    def _authenticate(self):
        self._save_settings()
        credentials = self.lyrics_settings.setdefault("credentials", {})
        self.service = SpotifyLyricsService(credentials, status_callback=self._set_status)
        self._set_status("Opening Spotify authentication ...")
        self.service.authenticate(self._authentication_finished)

    def _set_status(self, message):
        self.root.after(0, lambda: self.status_label.configure(text=message))

    def _authentication_finished(self, success, message):
        if success:
            self.root.after(0, self._save_settings)
        self._set_status(message)

    def stop(self):
        if not self.service:
            return
        self.service.stop()
        self.service = None

    def _stop(self):
        self.stop()
        self.status_label.configure(text="Spotify Lyrics stopped.")

    def draw(self):
        fields = [
            ("token", "Discord Token", self.cfg.get("token") or self._credential("token"), True),
            ("clientID", "Spotify Client ID", self._credential("clientID"), False),
            ("clientSecret", "Spotify Client Secret", self._credential("clientSecret"), True),
        ]

        for row, (key, label_text, value, secret) in enumerate(fields):
            label = ttk.Label(self.body, text=label_text)
            label.configure(background=self.root.style.colors.get("dark"))
            label.grid(row=row + 1, column=0, sticky=ttk.W, padx=(10, 10), pady=(2, 5))

            entry = ttk.Entry(self.body, show="*" if secret else None)
            entry.configure(foreground=self.root.style.colors.get("fg"))
            entry.insert(0, value)
            entry.grid(row=row + 1, column=1, sticky=ttk.EW, padx=(0, 10), pady=(2, 5))
            self.entries[key] = entry

        view = ttk.Frame(self.body, style="dark.TFrame")
        view.grid(row=len(fields) + 1, column=0, columnspan=2, sticky=ttk.EW, padx=10, pady=(5, 5))
        view.grid_columnconfigure(0, weight=1)

        self.timestamp_entry = RoundedSwitch(
            view,
            variable=ttk.BooleanVar(value=self.lyrics_settings.get("view", {}).get("timestamp", True)),
            parent_background=self.root.style.colors.get("dark"),
        )
        self.timestamp_entry.grid(row=0, column=1, sticky=ttk.E, padx=10, pady=5)
        ttk.Label(view, text="Show timestamps").grid(row=0, column=0, sticky=ttk.W, pady=5)

        self.label_entry = RoundedSwitch(
            view,
            variable=ttk.BooleanVar(value=self.lyrics_settings.get("view", {}).get("label", True)),
            parent_background=self.root.style.colors.get("dark"),
        )
        self.label_entry.grid(row=1, column=1, sticky=ttk.E, padx=10, pady=5)
        ttk.Label(view, text="Show lyrics label").grid(row=1, column=0, sticky=ttk.W, pady=5)

        actions = ttk.Frame(self.body, style="dark.TFrame")
        actions.grid(row=len(fields) + 2, column=0, columnspan=2, sticky=ttk.EW, padx=10, pady=(10, 5))
        RoundedButton(actions, text="Save", command=self._save_settings).pack(side=ttk.LEFT, padx=(0, 5))
        self.auth_button = RoundedButton(actions, text="Authenticate with Spotify", command=self._authenticate)
        self.auth_button.pack(side=ttk.LEFT, padx=5)
        RoundedButton(actions, text="Start", command=self._start).pack(side=ttk.LEFT, padx=5)
        RoundedButton(actions, text="Stop", command=self._stop).pack(side=ttk.LEFT, padx=5)

        self.status_label = ttk.Label(self.body, text="Ready")
        self.status_label.configure(background=self.root.style.colors.get("dark"))
        self.status_label.grid(row=len(fields) + 3, column=0, columnspan=2, sticky=ttk.W, padx=10, pady=(5, 10))

        self.body.grid_columnconfigure(1, weight=1)
        return self.wrapper