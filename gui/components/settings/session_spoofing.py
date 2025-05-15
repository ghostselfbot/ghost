import ttkbootstrap as ttk
import utils.console as console
from gui.components import SettingsPanel

class SessionSpoofingPanel(SettingsPanel):
    def __init__(self, root, parent, images, config):
        super().__init__(root, parent, "Session Spoofing", images.get("session_spoofing"))
        self.cfg = config
        self.selected_device = ttk.StringVar(value=self.cfg.get("session_spoofing.device"))
        self.last_saved_state = {
            "enabled": self.cfg.get("session_spoofing.enabled"),
            "device": self.selected_device.get(),
        }
        
    def _save_session_spoofing(self):
        enabled = self.checkbox.instate(["selected"])
        device = self.selected_device.get()

        if (enabled, device) != (self.last_saved_state["enabled"], self.last_saved_state["device"]):
            self.cfg.set("session_spoofing.enabled", enabled, save=False)
            self.cfg.set("session_spoofing.device", device, save=False)
            self.cfg.save(notify=False)

            self.last_saved_state["enabled"] = enabled
            self.last_saved_state["device"] = device

    def _select_and_save_device(self, device):
        if self.selected_device.get() != device:
            self.selected_device.set(device)
            self._save_session_spoofing()
        
    def draw(self):
        self.checkbox = ttk.Checkbutton(self.body, text="Enable session spoofing", style="success.TCheckbutton")
        self.checkbox.grid(row=0, column=0, columnspan=2, sticky=ttk.W, padx=(13, 0), pady=(10, 0))
        self.checkbox.configure(command=self._save_session_spoofing)
        
        if self.cfg.get("session_spoofing.enabled"):
            self.checkbox.state(["!alternate", "selected"])
        else:
            self.checkbox.state(["!alternate", "!selected"])
                
        device_label = ttk.Label(self.body, text="Session spoofing device")
        device_label.configure(background=self.root.style.colors.get("dark"))
        device_label.grid(row=1, column=0, sticky=ttk.W, padx=(10, 0), pady=(5, 0))
        
        device_select_menu = ttk.Menubutton(self.body, textvariable=self.selected_device, bootstyle="secondary")
        device_select_menu.menu = ttk.Menu(device_select_menu, tearoff=0)
        device_select_menu["menu"] = device_select_menu.menu
        
        for device in ["mobile", "desktop", "web", "embedded"]:
            device_select_menu.menu.add_command(label=device, command=lambda device=device: self._select_and_save_device(device))
            
        device_select_menu.grid(row=1, column=1, sticky="we", padx=(10, 10), pady=(5, 0))
        
        # save_button = ttk.Button(self.body, text="Save", style="success.TButton", command=self._save_session_spoofing)
        # save_button.grid(row=2, column=1, sticky=ttk.E, padx=(0, 11), pady=10)
        
        restart_required_label = ttk.Label(self.body, text="A restart is required to apply changes!", font=("Host Grotesk", 12, "italic"))
        restart_required_label.configure(background=self.root.style.colors.get("dark"), foreground="#cccccc")
        restart_required_label.grid(row=2, column=0, sticky=ttk.W, padx=(10, 0), pady=10)

        self.body.grid_columnconfigure(1, weight=1)
        
        return self.wrapper