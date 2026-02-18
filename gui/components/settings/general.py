import sys
import ttkbootstrap as ttk
import utils.console as console
from gui.components import SettingsPanel, DropdownMenu, RoundedButton
from gui.helpers import apply_theme, get_themes

class GeneralPanel(SettingsPanel):
    def __init__(self, root, parent, bot_controller, images, config, draw_settings, width=None):
        super().__init__(root, parent, "General", images.get("settings"), collapsed=False, width=width)
        self.bot_controller = bot_controller
        self.cfg = config
        self.draw_settings = draw_settings
        self.config_tk_entries = {}
        self.config_entries = {
            "token": "Token",
            "prefix": "Prefix",
            "message_settings.auto_delete_delay": "Auto delete delay"
        }
        self.message_style_entry = None
        
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

        try:
            self.cfg.set("message_settings.style", self.message_style_entry.value(), save=False)
        except Exception as e:
            console.error(f"Failed to set message style: {e}")

        self.cfg.save(notify=False)
        
    def _only_numeric(self, event):
        if not event.char.isnumeric() and event.char != "" and event.keysym != "BackSpace":
            return "break"
        
    def _set_message_style(self, style):
        # self.message_style_entry.configure(text=style)
        self._save_cfg()
        
    def _set_gui_theme(self):
        selected_theme = self.gui_theme_entry.value()
        apply_theme(self.root, selected_theme)
        self.cfg.set("gui_theme", selected_theme)

        # Redraw settings page
        self.root.after(100, lambda: self.draw_settings())

    def draw(self):
        for index, (key, value) in enumerate(self.config_entries.items()):
            padding = (10, 2)
            cfg_value = self.cfg.get(key)
            entry = ttk.Entry(self.body, font=("Host Grotesk", 12 if sys.platform != "darwin" else 13)) if key != "token" else ttk.Entry(self.body, show="*", font=("Host Grotesk", 12 if sys.platform != "darwin" else 13))
            entry.insert(0, cfg_value)
            entry.bind("<Return>", lambda event: self._save_cfg())
            entry.bind("<FocusOut>", lambda event: self._save_cfg())
            
            if "message_settings" in key:
                entry.bind("<Key>", self._only_numeric)

            if index == 0:
                padding = (padding[0], (10, 2))

            label = ttk.Label(self.body, text=value)
            label.configure(background=self.root.style.colors.get("dark"))

            label.grid(row=index + 1, column=0, sticky=ttk.W, padx=padding[0], pady=padding[1])
            entry.grid(row=index + 1, column=1, sticky="we", padx=padding[0], pady=padding[1], columnspan=3)

            self.body.grid_columnconfigure(1, weight=1)
            self.config_tk_entries[key] = entry
        
        message_style_label = ttk.Label(self.body, text="Message style")
        message_style_label.configure(background=self.root.style.colors.get("dark"))
        message_style_label.grid(row=len(self.config_entries) + 1, column=0, sticky=ttk.NW, padx=(10, 0), pady=(5, 10))
        
        self.message_style_entry = DropdownMenu(self.body, options=["codeblock", "image", "embed", "edited"], command=self._set_message_style)
        self.message_style_entry.set_selected(self.cfg.get("message_settings.style"))
        self.message_style_entry.draw().grid(row=len(self.config_entries) + 1, column=1, sticky="we", padx=(10, 10), pady=(2, 0), columnspan=3)
        
        gui_theme_label = ttk.Label(self.body, text="GUI Theme")
        gui_theme_label.configure(background=self.root.style.colors.get("dark"))
        gui_theme_label.grid(row=len(self.config_entries) + 2, column=0, sticky=ttk.NW, padx=(10, 0), pady=(5, 10))
        
        self.gui_theme_entry = DropdownMenu(self.body, options=get_themes(), command=lambda _: self._set_gui_theme())
        self.gui_theme_entry.set_selected(self.cfg.get("gui_theme"))
        self.gui_theme_entry.draw().grid(row=len(self.config_entries) + 2, column=1, sticky="we", padx=(10, 10), pady=(2, 10), columnspan=3)
        
        return self.wrapper
    
    def save(self):
        pass