from logging import root
import sys
import ttkbootstrap as ttk
from gui.components import RoundedFrame
from gui.helpers.style import Style

class Titlebar:
    def __init__(self, root, images):
        self.root = root
        self.images = images
        self._offset_x = 0
        self._offset_y = 0
        self._dragging = False

    def _on_press(self, event):
        self._dragging = True
        self._offset_x = event.x_root - self.root.winfo_x()
        self._offset_y = event.y_root - self.root.winfo_y()

    def _on_motion(self, event):
        if not self._dragging:
            return

        x = event.x_root - self._offset_x
        y = event.y_root - self._offset_y
        self.root.geometry(f"+{x}+{y}")

    def _on_release(self, event):
        self._dragging = False

    def _reset_hover_state(self):
        x, y = self.root.winfo_pointerxy()
        self.root.event_generate("<Motion>", warp=True, x=x+1, y=y)
        self.root.event_generate("<Motion>", warp=True, x=x, y=y)

    def _minimize(self):
        self.root.overrideredirect(False)
        self.root.withdraw()
        # if sys.platform == "darwin":
        #     self.root.withdraw()
        #     self.root.bind("<FocusIn>", self._restore_once, add="+")
        # else:
        #     self.root.overrideredirect(False)
        #     self.root.deiconify()
        #     self.root.overrideredirect(True)
        #     self.root.update_idletasks()

    def _restore_once(self, event=None):
        self.root.unbind("<FocusIn>")
        self.root.deiconify()

        self.root.after(10, lambda: self.root.overrideredirect(True))
        self.root.after(20, self._reset_hover_state)

    def _maximize(self):
        screen_height = self.root.winfo_screenheight()
        screen_width = self.root.winfo_screenwidth()
        
        window_geometry = self.root.winfo_geometry()
        window_size = window_geometry.split("+")[0]
        window_width = int(window_size.split("x")[0])
        window_height = int(window_size.split("x")[1])
        
        if window_width > self.root.size[0] or window_height > self.root.size[1]:
            self.root.geometry(f"{self.root.size[0]}x{self.root.size[1]}")
            self.root.update_idletasks()
            self.root.after(10, lambda: self.root.overrideredirect(True))
            self.root.after(20, lambda: self.root.geometry(f"+{(screen_width - self.root.size[0]) // 2}+{(screen_height - self.root.size[1]) // 2}"))
        else:
            self.root.geometry(f"{screen_width}x{screen_height - 40}+0+0")
            self.root.update_idletasks()
            self.root.after(10, lambda: self.root.overrideredirect(True))

    def draw(self):
        titlebar = RoundedFrame(
            self.root,
            radius=(25, 25, 0, 0),
            background=Style.WINDOW_BORDER.value
        )

        inner_wrapper = RoundedFrame(titlebar, background=Style.WINDOW_BORDER.value, radius=0)
        padx = 8
        pady = 8

        # Bind to all titlebar surfaces
        for widget in (titlebar, inner_wrapper):
            widget.bind("<ButtonPress-1>", self._on_press)
            widget.bind("<B1-Motion>", self._on_motion)
            widget.bind("<ButtonRelease-1>", self._on_release)

        if sys.platform == "darwin":
            pady = 0

            close_btn = ttk.Label(inner_wrapper, text="●", foreground="#FF5F57", font=("Arial", 25))
            close_btn.configure(background=Style.WINDOW_BORDER.value)
            close_btn.pack(side=ttk.LEFT, padx=(0, 0))
            close_btn.bind("<Button-1>", lambda e: self.root.quit())
            close_btn.bind("<Enter>", lambda e: close_btn.configure(foreground="#CC4940"))
            close_btn.bind("<Leave>", lambda e: close_btn.configure(foreground="#FF5F57"))
            
            minimize_btn = ttk.Label(inner_wrapper, text="●", foreground="#FFBD2E", font=("Arial", 25))
            minimize_btn.configure(background=Style.WINDOW_BORDER.value)
            minimize_btn.pack(side=ttk.LEFT, padx=(0, 0))
            minimize_btn.bind("<Button-1>", lambda e: self._minimize())
            minimize_btn.bind("<Enter>", lambda e: minimize_btn.configure(foreground="#CC9A26"))
            minimize_btn.bind("<Leave>", lambda e: minimize_btn.configure(foreground="#FFBD2E"))
            
            maximize_btn = ttk.Label(inner_wrapper, text="●", foreground="#4f4c4c", font=("Arial", 25))
            maximize_btn.configure(background=Style.WINDOW_BORDER.value)
            maximize_btn.pack(side=ttk.LEFT, padx=(0, 5))
            # maximize_btn.bind("<Enter>", lambda e: maximize_btn.configure(foreground="#20A833"))
            # maximize_btn.bind("<Leave>", lambda e: maximize_btn.configure(foreground="#28C940"))
            # maximize_btn.bind("<Button-1>", lambda e: self._maximize())
            
        else:
            ico = ttk.Label(inner_wrapper, image=self.images.images["titlebar-ico"])
            ico.configure(background=Style.WINDOW_BORDER.value)
            ico.pack(side=ttk.LEFT, padx=(5, 0))

            title = ttk.Label(inner_wrapper, text="Ghost", font=("Host Grotesk", 10))
            title.configure(background=Style.WINDOW_BORDER.value)
            title.pack(side=ttk.LEFT, padx=(5, 0))
            
            close_btn = ttk.Label(inner_wrapper, text="✕", font=("Host Grotesk", 10))
            close_btn.configure(background=Style.WINDOW_BORDER.value)
            close_btn.pack(side=ttk.RIGHT, padx=(0, 5))
            close_btn.bind("<Button-1>", lambda e: self.root.quit())
            
            minimize_btn = ttk.Label(inner_wrapper, text="—", font=("Host Grotesk", 10))
            minimize_btn.configure(background=Style.WINDOW_BORDER.value)
            minimize_btn.pack(side=ttk.RIGHT, padx=(0, 7))
            minimize_btn.bind("<Button-1>", lambda e: self._minimize())


        inner_wrapper.pack(fill=ttk.BOTH, expand=True, pady=pady, padx=padx)
        return titlebar