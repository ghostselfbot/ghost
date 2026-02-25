import ttkbootstrap as ttk
from gui.components import RoundedFrame
from gui.helpers.style import Style

class DropdownMenu:
    def __init__(self, parent, options, command=None):
        self.parent = parent
        self.options = options
        self.selected_option = ttk.StringVar(value=options[0] if options else "")
        self.command = command
        self.style = None
        
        # see if parent has root attribute, if so use it to get the style, otherwise get the style from the parent itself
        if hasattr(parent, "root") and parent.root and hasattr(parent.root, "style"):
            self.style = parent.root.style
        elif hasattr(parent, "style"):
            self.style = parent.style
        else:
            raise ValueError("Parent must have a style attribute or a root attribute with a style")
        
    def _hover_enter(self, wrapper, label):
        wrapper.set_background(Style.DROPDOWN_OPTION_HOVER.value)
        label.configure(background=Style.DROPDOWN_OPTION_HOVER.value)
        
    def _hover_leave(self, wrapper, label):
        wrapper.set_background(self.parent.style.colors.get("secondary"))
        label.configure(background=self.parent.style.colors.get("secondary"))
        
    def _rearrange_options(self):
        selected = self.selected_option.get()
        self.options.remove(selected)
        self.options.insert(0, selected)
        
    def _open_menu(self, event):
        if not self._alive():
            return
        
        for widget in self.frame.winfo_children():
            widget.destroy()
        
        self._rearrange_options()
        index = 0
        for option in self.options:
            index += 1
            
            wrapper = RoundedFrame(self.frame, radius=8, background=self.parent.style.colors.get("secondary"))
            wrapper.pack(fill=ttk.X, padx=5, pady=(4, 5 if index == len(self.options) else 0))
            wrapper.bind("<Button-1>", lambda e, opt=option: self._on_option_selected(opt))
            
            label = ttk.Label(wrapper, text=option, background=self.parent.style.colors.get("secondary"), anchor="w")
            label.pack(fill=ttk.X, padx=5, pady=2)
            label.bind("<Button-1>", lambda e, opt=option: self._on_option_selected(opt))
            
            label.bind("<Enter>", lambda e, w=wrapper, l=label: self._hover_enter(w, l))
            label.bind("<Leave>", lambda e, w=wrapper, l=label: self._hover_leave(w, l))
            wrapper.bind("<Enter>", lambda e, w=wrapper, l=label: self._hover_enter(w, l))
            wrapper.bind("<Leave>", lambda e, w=wrapper, l=label: self._hover_leave(w, l))
        
    def _close_menu(self):
        if not self._alive():
            return
        
        for widget in self.frame.winfo_children():
            widget.destroy()
            
        label = ttk.Label(self.frame, textvariable=self.selected_option, anchor="w", background=self.parent.style.colors.get("secondary"))
        label.pack(fill=ttk.X, padx=10, pady=5)
        label.bind("<Button-1>", self._open_menu)
        self.frame.bind("<Button-1>", self._open_menu)
        
        self.down_arrow = ttk.Label(self.frame, text="▼", background=self.parent.style.colors.get("secondary"), font=("Host Grotesk", 10))
        self.down_arrow.place(relx=1.0, rely=0.5, x=-10, y=0, anchor="e")
        self.down_arrow.bind("<Button-1>", self._open_menu)
        
    def _on_option_selected(self, option):
        if not self._alive():
            return

        self.selected_option.set(option)
        if self.command:
            self.command(option)

        if self._alive():
            self._close_menu()
        
    def _outside_click(self, event):
        if not self._alive():
            return
        if not self.frame.winfo_containing(event.x_root, event.y_root):
            self._close_menu()
        
    def draw(self):
        self.parent.bind("<Button-1>", self._outside_click, add="+")
        self.frame = RoundedFrame(self.parent, radius=5, bootstyle="secondary.TFrame")

        label = ttk.Label(self.frame, textvariable=self.selected_option, anchor="w", background=self.style.colors.get("secondary"))
        label.pack(fill=ttk.X, padx=10, pady=5)
        label.bind("<Button-1>", self._open_menu)
        self.frame.bind("<Button-1>", self._open_menu)
        
        self.down_arrow = ttk.Label(self.frame, text="▼", background=self.style.colors.get("secondary"), font=("Host Grotesk", 10))
        self.down_arrow.place(relx=1.0, rely=0.5, x=-10, y=0, anchor="e")
        self.down_arrow.bind("<Button-1>", self._open_menu)

        return self.frame
    
    def value(self):
        return self.selected_option.get()
    
    def set_selected(self, option):
        if option in self.options:
            self.selected_option.set(option)
            if self._alive():
                self._close_menu()
    
    def destroy(self):
        if self._alive():
            self.frame.destroy()
        
    def _alive(self):
        return hasattr(self, "frame") and self.frame.winfo_exists()
