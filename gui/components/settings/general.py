import ttkbootstrap as ttk
import utils.console as console
from gui.components import SettingsPanel

class GeneralPanel(SettingsPanel):
    def __init__(self, root, parent, bot_controller, images, config):
        super().__init__(root, parent, "General", images.get("settings"), collapsed=False)
        self.bot_controller = bot_controller
        self.cfg = config
        self.config_tk_entries = {}
        self.config_entries = {
            "token": "Token",
            "prefix": "Prefix",
            "message_settings.auto_delete_delay": "Auto delete delay",
            "rich_embed_webhook": "Rich embed webhook",
        }
        
    def _save_cfg(self):
        for index, (key, value) in enumerate(self.config_entries.items()):
            tkinter_entry = self.config_tk_entries[key]

            if key == "prefix":
                self.bot_controller.set_prefix(tkinter_entry.get())

            if "message_settings" in key:
                entry_value = tkinter_entry.get()
                if entry_value.isnumeric():
                    self.cfg.set(key, int(entry_value), save=False)
                else:
                    console.error(f"Auto delete delay must be a number! Got: {entry_value}")
                    continue

            self.cfg.set(key, tkinter_entry.get(), save=False)

        self.cfg.save(notify=False)
        
    def _only_numeric(self, event):
        if not event.char.isnumeric() and event.char != "" and event.keysym != "BackSpace":
            return "break"
        
    def draw(self):
        for index, (key, value) in enumerate(self.config_entries.items()):
            padding = (10, 2)
            cfg_value = self.cfg.get(key)
            entry = ttk.Entry(self.body, bootstyle="secondary", font=("Host Grotesk",)) if key != "token" else ttk.Entry(self.body, bootstyle="secondary", show="*", font=("Host Grotesk",))
            entry.insert(0, cfg_value)
            entry.bind("<Return>", lambda event: self._save_cfg())
            entry.bind("<FocusOut>", lambda event: self._save_cfg())
            
            if "message_settings" in key:
                entry.bind("<Key>", self._only_numeric)

            if index == 0:
                padding = (padding[0], (10, 2))
            elif index == len(self.config_entries) - 1:
                padding = (padding[0], (2, 10))

            label = ttk.Label(self.body, text=value)
            label.configure(background=self.root.style.colors.get("dark"))

            label.grid(row=index + 1, column=0, sticky=ttk.W, padx=padding[0], pady=padding[1])
            entry.grid(row=index + 1, column=1, sticky="we", padx=padding[0], pady=padding[1], columnspan=3)

            self.body.grid_columnconfigure(1, weight=1)
            self.config_tk_entries[key] = entry
        
        return self.wrapper
    
    def save(self):
        pass