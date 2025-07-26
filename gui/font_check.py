import os, sys
import ttkbootstrap as ttk

from gui.helpers import layout
from gui.components import RoundedFrame, RoundedButton
from utils.files import resource_path, get_application_support
from utils.fonts import load_fonts, get_fonts
from utils.config import Config
from utils import startup_check, console

class FontCheckGUI:
    def __init__(self):
        self.cfg = Config()
        self.root = ttk.tk.Tk()
        self.root.title("Ghost")
        if os.name == "nt":
            self.root.iconbitmap(resource_path("data/icon.ico"))
        
        self.root.style = ttk.Style()
        # self.root.style.theme_use("darkly")
        self.root.style.load_user_themes(resource_path("data/gui_theme.json"))
        self.root.style.theme_use("ghost")
        self.root.style.configure("TEntry", background=self.root.style.colors.get("dark"), fieldbackground=self.root.style.colors.get("secondary"))
        self.root.style.configure("TCheckbutton", background=self.root.style.colors.get("dark"))
        
        self._draw_font_check()
        
    def _install_fonts(self, _):
        if os.name == "nt":
            if startup_check.is_admin():
                load_fonts()
                os.execl(sys.executable, sys.executable, *sys.argv)
            else:
                install_fonts_path = os.path.join(get_application_support(), "INSTALL_FONTS_NO_GUI")
                console.info("Admin privilages needed, restarting with admin perms. Fonts will be installed without GUI. Restarting...")
                self.cfg.set_skip_fonts(True)
                os.execl(sys.executable, sys.executable, *sys.argv)
        else:
            load_fonts()
            os.execl(sys.executable, sys.executable, *sys.argv)
        
    def _skip(self, _):
        self.cfg.set_skip_fonts()
        os.execl(sys.executable, sys.executable, *sys.argv)
        
    def _draw_font_check(self):
        message = "The required fonts for Ghost have not been found! Would you like Ghost to automatically install them?"
        warning = "If you do not proceed Ghost will use the default system font which may not look as intended!"
        frame = RoundedFrame(self.root, radius=15, bootstyle="dark.TFrame")
        frame.pack(fill=ttk.BOTH, padx=10, pady=10, expand=True)
        
        title = ttk.Label(frame, text="Missing Fonts", font="-weight bold -size 20")
        title.configure(background=self.root.style.colors.get("dark"))
        title.pack(fill=ttk.BOTH, padx=10, pady=(10, 5))
        
        message_label = ttk.Label(frame, text=message, font="-size 12", wraplength=300)
        message_label.configure(background=self.root.style.colors.get("dark"))
        message_label.pack(fill=ttk.BOTH, padx=10)
        
        fonts_list_wrapper = RoundedFrame(frame, radius=10, style="secondary.TFrame")
        fonts_list_wrapper.pack(fill=ttk.BOTH, padx=10, pady=10)

        fonts_list_scrollable = ttk.Text(fonts_list_wrapper, wrap="word", height=8, font="-size 12", width=30)
        fonts_list_scrollable.config(
            border=0,
            background=self.root.style.colors.get("secondary"),
            foreground="lightgrey",
            highlightcolor=self.root.style.colors.get("secondary"),
            highlightbackground=self.root.style.colors.get("secondary"),
        )
        fonts_list_scrollable.pack(fill=ttk.BOTH, padx=5, pady=5)
        
        for font in get_fonts():
            fonts_list_scrollable.insert(ttk.END, f"{font}\n")
        
        fonts_list_scrollable.config(state="disabled")
        
        warning_label = ttk.Label(frame, text=warning, font="-slant italic -size 12", wraplength=300)
        warning_label.configure(background=self.root.style.colors.get("dark"), foreground="#cccccc")
        warning_label.pack(fill=ttk.BOTH, padx=10, pady=(0, 10))
        
        button_wrapper = ttk.Frame(frame, style="dark.TFrame")
        button_wrapper.pack(fill=ttk.BOTH, padx=10, pady=10)
        
        install_button = RoundedButton(button_wrapper, text="Install Fonts", style="primary.TButton", command=self._install_fonts, pady=2)
        install_button.pack(side=ttk.LEFT)
        
        skip_button = RoundedButton(button_wrapper, text="Skip", style="danger.TButton", command=self._skip, pady=2)
        skip_button.pack(side=ttk.LEFT, padx=(5, 0))
        
    def run(self):
        layout.center_window(self.root, 450, 450)
        # self.root.resizable(False, False)
        self.root.mainloop()