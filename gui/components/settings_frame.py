import sys
import ttkbootstrap as ttk
from gui.components import RoundedFrame
from utils.config import Config

class SettingsFrame:
    def __init__(self, parent, header_text, header_icon, collapsed=False, collapsible=False, width=None):
        self.parent = parent
        self.root = parent.winfo_toplevel()
        self.hover_colour = "#282a2a"
        self.header_text = header_text
        self.header_icon = header_icon
        self.width = width
        self.config = Config()
        
        self.collapsible = collapsible
        self.is_collapsed = self.config.get_temp(f"settings.{self.header_text.lower().replace(' ', '-')}.collapsed", collapsed)
        
    def _toggle_collapsed(self):
        if not self.collapsible:
            return
    
        self.is_collapsed = not self.is_collapsed
        self.config.set_temp(f"settings.{self.header_text.lower().replace(' ', '-')}.collapsed", self.is_collapsed)

        if self.is_collapsed:
            self.header.set_corner_radius((15, 15, 15, 15))
            self.body.pack_forget()
        else:
            self.header.set_corner_radius((15, 15, 0, 0))
            self.body.pack(fill=ttk.BOTH, expand=False)
        
    def _hover_enter(self, _):
        self.header.set_background(background=self.hover_colour)
        self.title.configure(background=self.hover_colour)
        self.icon.configure(background=self.hover_colour)
        
    def _hover_leave(self, _):
        self.header.set_background(background=self.root.style.colors.get("secondary"))
        self.title.configure(background=self.root.style.colors.get("secondary"))
        self.icon.configure(background=self.root.style.colors.get("secondary"))
        
    def _draw_header(self, parent):
        self.header = RoundedFrame(parent, radius=(15, 15, 0, 0), bootstyle="secondary.TFrame")
        self.header.pack(fill=ttk.BOTH, expand=False)
        
        self.title = ttk.Label(self.header, text=self.header_text, font=("Host Grotesk", 14 if sys.platform != "darwin" else 18, "bold"))
        self.title.configure(background=self.root.style.colors.get("secondary"))
        self.title.grid(row=0, column=0, sticky=ttk.NSEW, padx=15, pady=10)
        
        self.icon = ttk.Label(self.header, image=self.header_icon)
        self.icon.configure(background=self.root.style.colors.get("secondary"))
        self.icon.grid(row=0, column=2, sticky=ttk.E, padx=(0, 15), pady=10)
        
        self.header.grid_columnconfigure(1, weight=1)
        
        if self.collapsible:
            for component in [self.title, self.icon, self.header]:
                component.bind("<Enter>", self._hover_enter)
                component.bind("<Leave>", self._hover_leave)
                component.bind("<Button-1>", lambda e: self._toggle_collapsed())
        
    def _draw_body(self, parent):
        frame = RoundedFrame(parent, radius=15, bootstyle="dark.TFrame")
        # frame.pack(fill=ttk.BOTH, expand=False)
        frame.grid(column=0, row=5, sticky="nsew")
        parent.grid_columnconfigure(0, weight=1)
        
        return frame
        
    def draw(self):
        if self.width:
            wrapper = ttk.Frame(self.parent, takefocus=True, width=self.width)
        else:
            wrapper = ttk.Frame(self.parent, takefocus=True)
        wrapper.configure(style="default.TLabel")
        # wrapper.pack(fill=ttk.BOTH, expand=True)
        # wrapper.grid(column=0, row=0, sticky="nsew")
        
        # self._draw_header(wrapper)
        self.body = self._draw_body(wrapper)
        
        if self.is_collapsed:
            # self.header.set_corner_radius((15, 15, 15, 15))
            self.body.pack_forget()
        
        return self.body, wrapper