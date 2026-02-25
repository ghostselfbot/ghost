import sys
import ttkbootstrap as ttk
from gui.components.settings import GeneralPanel, ThemingPanel, APIsPanel, SessionSpoofingPanel, RichPresencePanel, SnipersPanel
from gui.components import RoundedFrame, DropdownMenu
from gui.helpers import Images, Style
from utils.config import Config

class SettingsPage:
    def __init__(self, root, bot_controller, draw_settings):
        self.root = root
        self.bot_controller = bot_controller
        self.width = root.winfo_width()
        self.height = root.winfo_height()
        self.parent = None
        self.draw_settings = draw_settings
        self.images = Images()
        self.cfg = Config()
        self.cfg.subscribe(self)

        self.current_page = "general"
        self.pages = {
            "general": None,
            "theming": None,
            # "apis": None,
            # "session_spoofing": None,
            "rich_presence": None,
            "snipers": None,
        }
        self.pills = {}
        
    def refresh_config(self):
        if not self.parent:
            return
        
        try:
            for widget in self.parent.winfo_children():
                widget.destroy()
                
            if self.parent: self.parent.update_idletasks()
            self.draw(self.parent)
            if self.parent:
                self.root.after_idle(lambda: self.root.focus_force())
        except Exception as e:
            print(f"Error refreshing config: {e}")
    
    def _create_sections(self, wrapper):
        general_wrapper = ttk.Frame(wrapper)
        
        self.general = GeneralPanel(self.root, general_wrapper, self.bot_controller, self.images, self.cfg, self.draw_settings).draw()
        self.session_spoofing = SessionSpoofingPanel(self.root, general_wrapper, self.images, self.cfg).draw()
        self.snipers = SnipersPanel(self.root, wrapper, self.images, self.cfg).draw()
        self.rpc = RichPresencePanel(self.root, wrapper, self.images, self.cfg, bot_controller=self.bot_controller).draw()
        self.apis = APIsPanel(self.root, general_wrapper, self.images, self.cfg).draw()
        self.theming = ThemingPanel(self.root, wrapper, self.images, self.cfg, bot_controller=self.bot_controller).draw()
        
        self.general.pack(fill=ttk.BOTH, expand=True, pady=(0, 10))
        self.session_spoofing.pack(fill=ttk.BOTH, expand=True, pady=(0, 10))
        self.apis.pack(fill=ttk.BOTH, expand=True, pady=(0, 10))
        
        self.pages["general"] = general_wrapper
        self.pages["theming"] = self.theming
        # self.pages["apis"] = self.apis
        # self.pages["session_spoofing"] = self.session_spoofing
        self.pages["rich_presence"] = self.rpc
        self.pages["snipers"] = self.snipers
    
    def _create_pill(self, parent, text, row, command):
        def _hover_enter(_, pill, label):
            if pill == self.pills[self.current_page]["pill"]:
                return
            pill.set_background(Style.SETTINGS_PILL_HOVER.value)
            label.configure(background=Style.SETTINGS_PILL_HOVER.value)
        def _hover_leave(_, pill, label):
            if pill == self.pills[self.current_page]["pill"]:
                return
            pill.set_background(self.root.style.colors.get("secondary"))
            label.configure(background=self.root.style.colors.get("secondary"))
        
        pill = RoundedFrame(parent, radius=10, bootstyle="secondary.TFrame")
        pill.grid(row=0, column=row, sticky=ttk.W, padx=(5, 0 if text != "Snipers" else 5), pady=5)
        label = ttk.Label(pill, text=text, font=("Host Grotesk", 14))
        label.configure(background=self.root.style.colors.get("secondary"))
        label.grid(row=0, column=0, sticky=ttk.W, padx=5, pady=5)
        label.bind("<Button-1>", lambda e: command())
        pill.bind("<Button-1>", lambda e: command())
        pill.bind("<Enter>", lambda e: _hover_enter(e, pill, label))
        pill.bind("<Leave>", lambda e: _hover_leave(e, pill, label))
        label.bind("<Enter>", lambda e: _hover_enter(e, pill, label))
        label.bind("<Leave>", lambda e: _hover_leave(e, pill, label))
        self.pills[text.lower().replace(" ", "_")] = {"pill": pill, "label": label}
        
    def toggle(self, key):
        if key != self.current_page:
            for page in self.pages.values():
                page.pack_forget()
            self.pages[key].pack(fill=ttk.BOTH, expand=True, pady=(0, 10))
            self.current_page = key
        
        for pill_key, pill_components in self.pills.items():
            is_selected = pill_key == key
            bg_color = Style.SETTINGS_PILL_SELECTED.value if is_selected else self.root.style.colors.get("secondary")
            pill_components["pill"].set_background(bg_color)
            pill_components["label"].configure(background=bg_color, font=("Host Grotesk", 14, "bold" if is_selected else "normal"))
    
    def draw(self, parent):
        self.parent = parent
        
        self.settings_wrapper = ttk.Frame(parent)
        self._create_sections(self.settings_wrapper)

        self.title = ttk.Label(parent, text="Settings", font=("Host Grotesk", 24, "bold"))
        self.title.configure(background=self.root.style.colors.get("bg"))
        self.title.pack(pady=(0, 10), anchor=ttk.W)

        self.pages_wrapper = RoundedFrame(parent, radius=15, bootstyle="dark.TFrame")
        self.pages_wrapper.pack(anchor=ttk.W)
        
        self._create_pill(self.pages_wrapper, "General", 0, lambda: self.toggle("general"))
        self._create_pill(self.pages_wrapper, "Theming", 1, lambda: self.toggle("theming"))
        # self._create_pill(self.pages_wrapper, "APIs", 2, lambda: self.toggle("apis"))
        # self._create_pill(self.pages_wrapper, "Session Spoofing", 3, lambda: self.toggle("session_spoofing"))
        self._create_pill(self.pages_wrapper, "Rich Presence", 4, lambda: self.toggle("rich_presence"))
        self._create_pill(self.pages_wrapper, "Snipers", 5, lambda: self.toggle("snipers"))
        
        # -------
        
        self.settings_wrapper.pack(fill=ttk.BOTH, expand=True, pady=(10, 0))
        self.pages[self.current_page].pack(fill=ttk.BOTH, expand=True, pady=(0, 10))
        self.toggle(self.current_page)