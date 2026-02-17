import sys
import ttkbootstrap as ttk
import utils.console as console
from gui.components import SettingsPanel

class APIsPanel(SettingsPanel):
    def __init__(self, root, parent, images, config, width=None):
        super().__init__(root, parent, "APIs", images.get("apis"), width=width, collapsed=False)
        self.cfg = config
        self.api_keys_tk_entries = {}
        self.api_keys_entries = {
            "serpapi": "SerpAPI Key"
        }
        
    def _save_api_keys(self):
        for index, (key, value) in enumerate(self.api_keys_entries.items()):
            tkinter_entry = self.api_keys_tk_entries[key]
            self.cfg.set(f"apis.{key}", tkinter_entry.get(), save=False)
            
        self.cfg.save(notify=False)
        
    def draw(self):
        wrapper = ttk.Frame(self.body, style="dark.TFrame")
        wrapper.pack(fill=ttk.BOTH, expand=True, padx=10, pady=10)
        wrapper.grid_columnconfigure(1, weight=1)
        
        for index, (key, value) in enumerate(self.api_keys_entries.items()):
            cfg_value = self.cfg.get(f"apis.{key}")
            entry = ttk.Entry(wrapper, show="*", font=("Host Grotesk", 12 if sys.platform != "darwin" else 13))
            entry.insert(0, cfg_value)
            entry.bind("<Return>", lambda event: self._save_api_keys())
            entry.bind("<FocusOut>", lambda event: self._save_api_keys())

            label = ttk.Label(wrapper, text=value)
            label.configure(background=self.root.style.colors.get("dark"))

            label.grid(row=index + 1, column=0, sticky=ttk.W, padx=(0, 10), pady=(0, 2))
            entry.grid(row=index + 1, column=1, sticky="we", pady=(0, 2))

            self.api_keys_tk_entries[key] = entry

        # save_api_keys_button = ttk.Button(self.body, text="Save", style="success.TButton", command=self._save_api_keys)
        # save_api_keys_button.grid(row=len(self.api_keys_entries) + 1, column=2, sticky=ttk.E, padx=(0, 11), pady=10)
        
        return self.wrapper