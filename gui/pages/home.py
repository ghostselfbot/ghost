import webbrowser, discord, sys
import ttkbootstrap as ttk
import tkinter.font as tkFont
from ttkbootstrap.scrolled import ScrolledFrame
from gui.components import RoundedFrame, RoundedButton
from gui.helpers import Images
from utils.config import VERSION, CHANGELOG, MOTD, Config

class HomePage:
    def __init__(self, root, bot_controller, _restart_bot, console):
        self.root = root
        self.bot_controller = bot_controller
        self._restart_bot = _restart_bot
        self.console = console
        self.width = root.winfo_width()
        self.height = root.winfo_height()
        self.restart = False
        self.avatar = None
        self.avatars = {}
        self.images = Images()
        self.cfg = Config()
                
        self.details_wrapper = None
        self.friends_label = None
        self.guilds_label = None
        self.uptime_label = None
        self.latency_label = None
        
        self.restart_title = None
        self.restart_title_elipsis = "..."
        self.restart_title_text = "Ghost is restarting"
        
        self.root.bind("<Configure>", self._update_wraplength)
        
    def _clear_everything(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
    def _update_restart_title(self):
        if self.restart:
            if len(self.restart_title_elipsis) == 3:
                self.restart_title_elipsis = "."
            else:
                self.restart_title_elipsis += "."
            self.restart_title.config(text=f"{self.restart_title_text}{self.restart_title_elipsis}")
        self.root.after(750, self._update_restart_title)
        
    def _update_account_details(self):
        try:
            if not self.restart:
                self.friends_label.config(text=f"Friends: {len(self.bot_controller.get_friends())}")
                self.guilds_label.config(text=f"Guilds: {len(self.bot_controller.get_guilds())}")
        except:
            pass
        self.root.after(1000, self._update_account_details)
        
    def _update_bot_details(self):
        try:
            if not self.restart:
                self.uptime_label.config(text=f"Uptime: {self.bot_controller.get_uptime()}")
                self.latency_label.config(text=f"Latency: {self.bot_controller.get_latency()}")
        except:
            pass
        self.root.after(1000, self._update_bot_details)
        
    def _draw_restart_button(self, parent, disabled=False):
        def _hover_enter(_):
            frame.set_background(background="#322bef")
            restart_label.configure(background="#322bef")
            
        def _hover_leave(_):
            frame.set_background(background=self.root.style.colors.get("primary"))
            restart_label.configure(background=self.root.style.colors.get("primary"))
        
        frame = RoundedFrame(parent, radius=(8, 8, 8, 8), bootstyle="primary.TButton" if not disabled else "disabled.TButton")
        
        restart_label = ttk.Label(frame, image=self.images.get("restart"), anchor="center")
        restart_label.configure(background=self.root.style.colors.get("primary") if not disabled else self.root.style.colors.get("disabled"))
        # restart_label.configure(background=self.root.style.colors.get("secondary"))
        restart_label.pack(anchor="center", fill=ttk.BOTH, expand=False, padx=25, pady=10)
        
        if not disabled:
            restart_label.bind("<Button-1>", lambda e: self._restart_bot())
            restart_label.bind("<Enter>", _hover_enter)
            restart_label.bind("<Leave>", _hover_leave)
            frame.bind("<Button-1>", lambda e: self._restart_bot())
            frame.bind("<Enter>", _hover_enter)
            frame.bind("<Leave>", _hover_leave)
        
        return frame
        
    def _draw_header(self, parent):
        wrapper = RoundedFrame(parent, radius=(15, 15, 15, 15), bootstyle="secondary.TFrame")
        wrapper.pack(fill=ttk.BOTH, expand=False, pady=(0, 10))
        
        if self.avatar and not self.restart:
            avatar = ttk.Label(wrapper, image=self.avatar)
            avatar.configure(background=self.root.style.colors.get("secondary"))
            avatar.grid(row=0, column=0, sticky=ttk.W, padx=(15, 10), pady=15, rowspan=2)
            
        if not self.restart:
            display_name = ttk.Label(wrapper, text=self.bot_controller.get_user().display_name, font=("Host Grotesk", 16 if sys.platform != "darwin" else 20, "bold"))
            display_name.configure(background=self.root.style.colors.get("secondary"))
            display_name.grid(row=0, column=1, sticky=ttk.W, pady=(15, 0))

            username = ttk.Label(wrapper, text=self.bot_controller.get_user().name, font=("Host Grotesk", 12 if sys.platform != "darwin" else 14, "italic"))
            username.configure(background=self.root.style.colors.get("secondary"), foreground="lightgrey")
            username.grid(row=1, column=1, sticky=ttk.W, pady=(0, 15))
            
            # restart_btn = self._draw_restart_button(wrapper)
            # restart_btn.grid(row=0, column=3, rowspan=2, sticky=ttk.EW, padx=(10, 16), pady=(10, 10))
            restart_btn = RoundedButton(wrapper, radius=8, bootstyle="primary.TButton", command=lambda _: self._restart_bot(), image=self.images.get("restart"), padx=15, pady=6)
            restart_btn.grid(row=0, column=3, rowspan=2, sticky=ttk.EW, padx=(10, 16), pady=(10, 10))
            
            wrapper.grid_columnconfigure(2, weight=1)
        else:
            self.restart_title = ttk.Label(wrapper, text=f"{self.restart_title_text}...", font=("Host Grotesk", 14 if sys.platform != "darwin" else 20, "bold"), anchor="center")
            self.restart_title.configure(background=self.root.style.colors.get("secondary"))
            self.restart_title.grid(row=0, column=0, sticky=ttk.NSEW, pady=26, padx=15, columnspan=2)
            wrapper.grid_columnconfigure(0, weight=1)
            self.root.after(750, self._update_restart_title)
    
    def _draw_details_wrapper(self, parent):
        wrapper = ttk.Frame(parent, width=self.width)
        wrapper.configure(style="default.TLabel")
        wrapper.pack(fill=ttk.BOTH, expand=False, pady=(10, 0))
        
        wrapper.grid_rowconfigure(0, weight=1)
        wrapper.grid_columnconfigure(0, weight=1)
        wrapper.grid_columnconfigure(1, weight=1)
        
        return wrapper
    
    def _draw_account_details(self, parent):
        wrapper = RoundedFrame(parent, radius=(15, 15, 15, 15), bootstyle="dark.TFrame")
        wrapper.grid(row=0, column=0, sticky=ttk.NSEW, padx=(0, 5), pady=(0, 5))
        
        if self.restart:
            return
        
        title = ttk.Label(wrapper, text="Discord", font=("Host Grotesk", 14 if sys.platform != "darwin" else 18, "bold"))
        title.configure(background=self.root.style.colors.get("dark"))
        title.grid(row=0, column=0, sticky=ttk.W, padx=10, pady=(10, 0))
        
        ttk.Separator(wrapper, orient="horizontal").grid(row=1, column=0, columnspan=2, sticky="we", padx=(10, 10), pady=5)
        wrapper.grid_columnconfigure(1, weight=1)
        
        self.friends_label = ttk.Label(wrapper, text=f"Friends: {len(self.bot_controller.get_friends())}", font=("Host Grotesk", 12 if sys.platform != "darwin" else 14))
        self.friends_label.configure(background=self.root.style.colors.get("dark"), foreground="white" if not self.restart else "lightgrey")
        self.friends_label.grid(row=2, column=0, sticky=ttk.W, padx=10, pady=(5, 0))
        
        self.guilds_label = ttk.Label(wrapper, text=f"Guilds: {len(self.bot_controller.get_guilds())}", font=("Host Grotesk", 12 if sys.platform != "darwin" else 14))
        self.guilds_label.configure(background=self.root.style.colors.get("dark"), foreground="white" if not self.restart else "lightgrey")
        self.guilds_label.grid(row=3, column=0, sticky=ttk.W, padx=10, pady=(0, 10))
        
    def _draw_bot_details(self, parent):
        wrapper = RoundedFrame(parent, radius=(15, 15, 15, 15), bootstyle="dark.TFrame")
        wrapper.grid(row=0, column=1, sticky=ttk.NSEW, padx=(5, 0), pady=(0, 5))
        
        if self.restart:
            return
        
        title = ttk.Label(wrapper, text="Ghost", font=("Host Grotesk", 14 if sys.platform != "darwin" else 18, "bold"))
        title.configure(background=self.root.style.colors.get("dark"))
        title.grid(row=0, column=0, sticky=ttk.W, padx=10, pady=(10, 0))
        
        ttk.Separator(wrapper, orient="horizontal").grid(row=1, column=0, columnspan=2, sticky="we", padx=(10, 10), pady=5)
        wrapper.grid_columnconfigure(1, weight=1)
        
        version = ttk.Label(wrapper, text=f"Version: {VERSION}", font=("Host Grotesk", 12 if sys.platform != "darwin" else 14))
        version.configure(background=self.root.style.colors.get("dark"))
        version.grid(row=2, column=0, sticky=ttk.W, padx=(10, 0), pady=(5, 0))    
        
        self.uptime_label = ttk.Label(wrapper, text=f"Uptime: {self.bot_controller.get_uptime()}", font=("Host Grotesk", 12 if sys.platform != "darwin" else 14))
        self.uptime_label.configure(background=self.root.style.colors.get("dark"), foreground="white" if not self.restart else "lightgrey")
        self.uptime_label.grid(row=3, column=0, sticky=ttk.W, padx=(10, 0))
        
        self.latency_label = ttk.Label(wrapper, text=f"Latency: {self.bot_controller.get_latency()}", font=("Host Grotesk", 12 if sys.platform != "darwin" else 14))
        self.latency_label.configure(background=self.root.style.colors.get("dark"), foreground="white" if not self.restart else "lightgrey")
        self.latency_label.grid(row=4, column=0, sticky=ttk.W, padx=(10, 0), pady=(0, 10))
        
    def _update_wraplength(self, event=None):
        # This method can be used for future wraplength updates if needed
        pass
            
            
    def draw(self, parent, restart=False, start=False):
        self.restart = restart or start
        self.restart_title_text = "Ghost is starting" if start else "Ghost is restarting"
        self.avatar = self.bot_controller.get_avatar()
        self._draw_header(parent)
        
        # self.details_wrapper = self._draw_details_wrapper(parent)
        # self._draw_account_details(self.details_wrapper)
        # self._draw_bot_details(self.details_wrapper)
        
        # self._update_bot_details()
        # self._update_account_details()
        
        self.console.draw(parent)