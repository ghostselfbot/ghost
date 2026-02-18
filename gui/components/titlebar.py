from logging import root
import sys

if sys.platform == "win32":
    import hPyT

if sys.platform == "darwin":
    from Cocoa import NSApp

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
        if sys.platform == "win32":
            self._dragging = True
            self._offset_x = event.x_root - self.root.winfo_x()
            self._offset_y = event.y_root - self.root.winfo_y()
        elif sys.platform == "darwin":
            ns_window = NSApp().windows()[0]
            ns_event = NSApp().currentEvent()
            ns_window.performWindowDragWithEvent_(ns_event)

    def _on_motion(self, event):
        if not self._dragging:
            return

        if sys.platform == "darwin":
            x = event.x_root - self._offset_x
            y = event.y_root - self._offset_y
            self.root.geometry(f"+{x}+{y}")
        elif sys.platform == "win32":
            hPyT.window_frame.move(self.root, event.x_root - self._offset_x, event.y_root - self._offset_y)

    def _on_release(self, event):
        self._dragging = False

    def _reset_hover_state(self):
        x, y = self.root.winfo_pointerxy()
        self.root.event_generate("<Motion>", warp=True, x=x+1, y=y)
        self.root.event_generate("<Motion>", warp=True, x=x, y=y)

    def _close(self):
        if sys.platform == "darwin":
            self.root.update_idletasks()
            self.root.overrideredirect(False)
            self.root.withdraw()
        else:
            self.root.quit()

    def _minimize(self):
        self.root.update_idletasks()
        self.root.overrideredirect(False)
        
        if sys.platform == "darwin":
            self.root.iconify()
        elif sys.platform == "win32":
            hPyT.window_frame.minimize(self.root)
            
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
            if sys.platform != "darwin":
                widget.bind("<B1-Motion>", self._on_motion)
                widget.bind("<ButtonRelease-1>", self._on_release)

        if sys.platform == "darwin":
            pady = 10
            
            ttk.Label(inner_wrapper, text="asd", foreground=Style.WINDOW_BORDER.value, background=Style.WINDOW_BORDER.value, font=("Arial", 1)).pack(side=ttk.LEFT, padx=(0, 0))

            # close_btn = ttk.Label(inner_wrapper, text="●", foreground="#FF5F57", font=("Arial", 25))
            # close_btn.configure(background=Style.WINDOW_BORDER.value)
            # close_btn.pack(side=ttk.LEFT, padx=(0, 0))
            # close_btn.bind("<Button-1>", lambda e: self._close())
            # close_btn.bind("<Enter>", lambda e: close_btn.configure(foreground="#CC4940"))
            # close_btn.bind("<Leave>", lambda e: close_btn.configure(foreground="#FF5F57"))
            
            # minimize_btn = ttk.Label(inner_wrapper, text="●", foreground=Style.MAC_TITLEBAR_INACTIVE.value, font=("Arial", 28))
            # minimize_btn.configure(background=Style.WINDOW_BORDER.value)
            # minimize_btn.pack(side=ttk.LEFT, padx=(0, 0))
            # # minimize_btn.bind("<Button-1>", lambda e: self._minimize())
            # # minimize_btn.bind("<Enter>", lambda e: minimize_btn.configure(foreground="#CC9A26"))
            # # minimize_btn.bind("<Leave>", lambda e: minimize_btn.configure(foreground="#FFBD2E"))
            
            # maximize_btn = ttk.Label(inner_wrapper, text="●", foreground=Style.MAC_TITLEBAR_INACTIVE.value, font=("Arial", 28))
            # maximize_btn.configure(background=Style.WINDOW_BORDER.value)
            # maximize_btn.pack(side=ttk.LEFT, padx=(0, 5))
            # # maximize_btn.bind("<Enter>", lambda e: maximize_btn.configure(foreground="#20A833"))
            # # maximize_btn.bind("<Leave>", lambda e: maximize_btn.configure(foreground="#28C940"))
            # # maximize_btn.bind("<Button-1>", lambda e: self._maximize())
            
        else:
            ico = ttk.Label(inner_wrapper, image=self.images.images["titlebar-ico"])
            ico.configure(background=Style.WINDOW_BORDER.value)
            ico.pack(side=ttk.LEFT, padx=(5, 0))

            title = ttk.Label(inner_wrapper, text="Ghost", font=("Host Grotesk", 12))
            title.configure(background=Style.WINDOW_BORDER.value)
            title.pack(side=ttk.LEFT, padx=(5, 0))
            
            def close_btn_enter(e):
                close_btn.configure(background=Style.SETTINGS_PILL_HOVER.value, foreground="#ffffff")
                close_btn_wrapper.set_background(Style.SETTINGS_PILL_HOVER.value)

            def close_btn_leave(e):
                close_btn.configure(background=Style.WINDOW_BORDER.value, foreground="#ffffff")
                close_btn_wrapper.set_background(Style.WINDOW_BORDER.value)

            close_btn_wrapper = RoundedFrame(inner_wrapper, radius=10, background=Style.WINDOW_BORDER.value)
            close_btn_wrapper.pack(side=ttk.RIGHT)
            close_btn_wrapper.bind("<Button-1>", lambda e: self._close())
            close_btn_wrapper.bind("<Enter>", close_btn_enter)
            close_btn_wrapper.bind("<Leave>", close_btn_leave)

            close_btn = ttk.Label(close_btn_wrapper, text="⨉", font=("Arial", 13))
            close_btn.configure(background=Style.WINDOW_BORDER.value, foreground="#ffffff")
            close_btn.pack(fill=ttk.BOTH, expand=True, padx=8, pady=4)
            close_btn.bind("<Button-1>", lambda e: self.root.quit())
            close_btn.bind("<Enter>", close_btn_enter)
            close_btn.bind("<Leave>", close_btn_leave)

            def minimize_btn_enter(e):
                minimize_btn.configure(background=Style.SETTINGS_PILL_HOVER.value, foreground="#ffffff")
                minimize_btn_wrapper.set_background(Style.SETTINGS_PILL_HOVER.value)

            def minimize_btn_leave(e):
                minimize_btn.configure(background=Style.WINDOW_BORDER.value, foreground="#ffffff")
                minimize_btn_wrapper.set_background(Style.WINDOW_BORDER.value)

            minimize_btn_wrapper = RoundedFrame(inner_wrapper, radius=10, background=Style.WINDOW_BORDER.value)
            minimize_btn_wrapper.pack(side=ttk.RIGHT)
            minimize_btn_wrapper.bind("<Button-1>", lambda e: self._minimize())
            minimize_btn_wrapper.bind("<Enter>", minimize_btn_enter)
            minimize_btn_wrapper.bind("<Leave>", minimize_btn_leave)

            minimize_btn = ttk.Label(minimize_btn_wrapper, text="—", font=("Arial", 10))
            minimize_btn.configure(background=Style.WINDOW_BORDER.value, foreground="#ffffff")
            minimize_btn.pack(fill=ttk.BOTH, expand=True, padx=8, pady=5)
            minimize_btn.bind("<Button-1>", lambda e: self._minimize())
            minimize_btn.bind("<Enter>", minimize_btn_enter)
            minimize_btn.bind("<Leave>", minimize_btn_leave)

        inner_wrapper.pack(fill=ttk.BOTH, expand=True, pady=pady, padx=padx)
        return titlebar