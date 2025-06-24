import ttkbootstrap as ttk
import utils.console as console
from gui.components import SettingsPanel, RoundedButton

class RichPresencePanel(SettingsPanel):
    def __init__(self, root, parent, images, config):
        super().__init__(root, parent, "Rich Presence", images.get("rich_presence"))
        self.cfg = config
        self.rpc = self.cfg.get_rich_presence()
        self.rpc_tk_entries = {}
        self.rpc_entries = {
            "enabled": "Enabled",
            "client_id": "Client ID",
            "name": "Name",
            "details": "Details",
            "state": "State",
            "large_image": "Large Image Key",
            "large_text": "Large Text",
            "small_image": "Small Image Key",
            "small_text": "Small Text",
        }
        self.last_saved_state = {
            "enabled": self.rpc.enabled,
            "client_id": self.rpc.client_id,
            "state": self.rpc.state,
            "details": self.rpc.details,
            "large_image": self.rpc.large_image,
            "large_text": self.rpc.large_text,
            "small_image": self.rpc.small_image,
            "small_text": self.rpc.small_text,
            "name": self.rpc.name,
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
        toggle_checkbox = ttk.Checkbutton(self.body, text="Enable Rich Presence", style="success.TCheckbutton")
        toggle_checkbox.grid(row=0, column=0, columnspan=2, sticky=ttk.W, padx=(13, 0), pady=(10, 10))
        toggle_checkbox.configure(command=self._save_rpc)
        
        if self.rpc.enabled:
            toggle_checkbox.state(["!alternate", "selected"])
        else:
            toggle_checkbox.state(["!alternate", "!selected"])
        
        self.rpc_tk_entries["enabled"] = toggle_checkbox
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
            
            label.grid(row=index + 1, column=0, sticky=ttk.W, padx=padding[0], pady=padding[1])
            entry.grid(row=index + 1, column=1, sticky="we", padx=padding[0], pady=padding[1], columnspan=3)
            
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