import sys
import ttkbootstrap as ttk
import utils.console as console
from gui.components import SettingsPanel, RoundedButton, RoundedFrame

class RichPresencePanel(SettingsPanel):
    def __init__(self, root, parent, images, config, width=None):
        super().__init__(root, parent, "Rich Presence", images.get("rich_presence"), width=width, collapsed=False)
        self.cfg = config
        self.rpc = self.cfg.get_rich_presence()
        self.rpc_tk_entries = {}
        self.rpc_entries = {
            "enabled": "Enabled",
            "name": "Name",
            "details": "Details",
            "details_url": "Details URL",
            "state": "State",
            "state_url": "State URL",
            "large_image": "Large Image Key",
            "large_text": "Large Text",
            "large_url": "Large Image URL",
            "small_image": "Small Image Key",
            "small_text": "Small Text",
            "small_url": "Small Image URL",
        }
        self.last_saved_state = {
            "enabled": self.rpc.enabled,
            "state": self.rpc.state,
            "details": self.rpc.details,
            "large_image": self.rpc.large_image,
            "large_text": self.rpc.large_text,
            "small_image": self.rpc.small_image,
            "small_text": self.rpc.small_text,
            "name": self.rpc.name,
            "state_url": self.rpc.state_url,
            "details_url": self.rpc.details_url,
            "large_url": self.rpc.large_url,
            "small_url": self.rpc.small_url
        }
        
    def _save_rpc(self):
        for index, (key, value) in enumerate(self.rpc_entries.items()):
            tkinter_entry = self.rpc_tk_entries[key]
            if key == "enabled":
                self.rpc.enabled = tkinter_entry.instate(["selected"])
            else:
                self.rpc.set(key, tkinter_entry.get())
            
        self.rpc.save(notify=False)
        
    def _reset_rpc(self):
        self.rpc.reset_defaults()
        
    def draw(self):
        toggle_wrapper = RoundedFrame(self.wrapper, radius=(10, 10, 10, 10), bootstyle="dark.TFrame")
        toggle_wrapper.grid(row=0, column=0, columnspan=4, sticky="we", pady=(0, 10))
        toggle_wrapper.bind("<Button-1>", lambda e: self.toggle_checkbox.invoke())
        
        toggle_label = ttk.Label(toggle_wrapper, text="Enable Rich Presence")
        toggle_label.configure(background=self.root.style.colors.get("dark"))
        toggle_label.grid(row=0, column=0, sticky=ttk.W, padx=(10, 0), pady=10)
        toggle_label.bind("<Button-1>", lambda e: self.toggle_checkbox.invoke())
        
        self.toggle_checkbox = ttk.Checkbutton(toggle_wrapper, text="", style="success-round-toggle")
        self.toggle_checkbox.grid(row=0, column=1, sticky=ttk.E, padx=(0, 10), pady=10)
        self.toggle_checkbox.configure(command=self._save_rpc)
        
        toggle_wrapper.grid_columnconfigure(0, weight=1)
        
        if self.rpc.enabled:
            self.toggle_checkbox.state(["!alternate", "selected"])
        else:
            self.toggle_checkbox.state(["!alternate", "!selected"])
        
        self.rpc_tk_entries["enabled"] = self.toggle_checkbox
        padding = (10, 2)

        for index, (key, value) in enumerate(self.rpc_entries.items()):
            if key == "enabled":
                continue
            
            rpc_value = self.rpc.get(key)
            entry = ttk.Entry(self.body, bootstyle="secondary", font=("Host Grotesk",))
            entry.insert(0, rpc_value)
            entry.bind("<Return>", lambda event: self._save_rpc())
            entry.bind("<FocusOut>", lambda event: self._save_rpc())
                
            label = ttk.Label(self.body, text=value)
            label.configure(background=self.root.style.colors.get("dark"))
            
            label.grid(row=index + 1, column=0, sticky=ttk.W, padx=padding[0], pady=(padding[1] + 8 if index == 1 else padding[1], padding[1]))
            entry.grid(row=index + 1, column=1, sticky="we", padx=padding[0], pady=(padding[1] + 8 if index == 1 else padding[1], padding[1]), columnspan=3)
            
            self.body.grid_columnconfigure(1, weight=1)
            self.rpc_tk_entries[key] = entry
            
        save_label = ttk.Label(self.body, text="A restart is required to apply changes!", font=("Host Grotesk", 12, "italic"))
        save_label.configure(background=self.root.style.colors.get("dark"), foreground="#cccccc")
        save_label.grid(row=len(self.rpc_entries) + 1, column=0, columnspan=2, sticky=ttk.W, padx=(10, 0), pady=10)
        
        # save_rpc_button = ttk.Button(self.body, text="Save", style="success.TButton", command=self._save_rpc)
        # save_rpc_button.grid(row=len(self.rpc_entries) + 1, column=2, sticky=ttk.E, pady=10)
        
        # reset_rpc_button = ttk.Button(self.body, text="Reset", style="danger.TButton", command=self._reset_rpc)
        reset_rpc_button = RoundedButton(self.body, text="Reset", style="danger.TButton", command=self._reset_rpc)
        reset_rpc_button.grid(row=len(self.rpc_entries) + 1, column=3, sticky=ttk.E, padx=(5, 11), pady=10)
        
        return self.wrapper