import webbrowser, discord, sys, time
import ttkbootstrap as ttk
import tkinter.font as tkFont
from ttkbootstrap.scrolled import ScrolledFrame
from gui.components import RoundedFrame, ToolPage
from gui.components.tools.message_log_entry import MessageLogEntry
from gui.helpers import Images
from gui.helpers.style import Style
from utils.config import VERSION, CHANGELOG, MOTD, Config

class MessageLoggerPage(ToolPage):
    def __init__(self, toolspage, root, bot_controller, images, layout):
        super().__init__(toolspage, root, bot_controller, images, layout, title="Message Logger")
        
        self.discord_logs_wrapper = None
        self.discord_logs_inner_wrapper = None
        self.discord_logs_frame = None
        self.discord_logs = []
        self.discord_logs_canvas = None
        self.logs = []
        self.canvas_window = None
        self.avatars = {}

    def draw_navigation(self, parent):
        wrapper = ttk.Frame(parent)

        tools_label = ttk.Label(wrapper, text="Tools", font=("Host Grotesk", 24, "bold"), foreground=Style.LIGHT_GREY.value)
        tools_label.grid(row=0, column=0, sticky=ttk.W)
        tools_label.bind("<Button-1>", lambda e: self.go_back())

        back_button = ttk.Label(wrapper, image=self.images.get("right-chevron-small"))
        back_button.bind("<Button-1>", lambda e: self.go_back())
        back_button.grid(row=0, column=1, sticky=ttk.W, padx=(10, 10))

        page_name = ttk.Label(wrapper, text=self.title, font=("Host Grotesk", 24, "bold"))
        page_name.grid(row=0, column=2, sticky=ttk.W)
        page_name.bind("<Button-1>", lambda e: self.go_back())

        clear_btn = ttk.Label(wrapper, image=self.images.get("trash"))
        clear_btn.configure(foreground="white")
        clear_btn.bind("<Button-1>", lambda e: self._clear_discord_logs())
        clear_btn.bind("<Enter>", lambda e: clear_btn.configure(foreground="lightgrey"))
        clear_btn.bind("<Leave>", lambda e: clear_btn.configure(foreground="white"))
        clear_btn.grid(row=0, column=3, sticky=ttk.E, padx=(20, 0))

        wrapper.grid_columnconfigure(2, weight=1)

        return wrapper

    def add_discord_log(self, author, message, delete_time):
        log_entry = (author, message, delete_time)
        self.discord_logs.append(log_entry)
        
        if self.discord_logs_frame and self.discord_logs_canvas:
            self._display_log(log_entry)
            self.root.after_idle(lambda: self._update_canvas_after_add())
    
    def _on_mousewheel(self, event):
        if sys.platform == 'darwin':
            self.discord_logs_canvas.yview_scroll(-1 * int(event.delta), "units")
        else:
            self.discord_logs_canvas.yview_scroll(-1 * int(event.delta / 120), "units")
    
    def _update_canvas_after_add(self):
        try:
            if self.discord_logs_canvas and self.discord_logs_frame:
                self.discord_logs_canvas.configure(scrollregion=self.discord_logs_canvas.bbox("all"))
                
                if self.discord_logs_wrapper:
                    self._update_canvas_width(self.discord_logs_canvas, self.discord_logs_wrapper)
                    
                self.discord_logs_canvas.yview_moveto(1)
        except:
            pass
        
    def _load_discord_logs(self):
        for log_entry in self.discord_logs:
            self._display_log(log_entry)
            
        try:
            self._update_canvas_width(self.discord_logs_canvas, self.discord_logs_wrapper)
            self.discord_logs_canvas.yview_moveto(1)
        except:
            pass
            
    def _clear_discord_logs(self):
        if not self.discord_logs_frame:
            return
            
        for widget in self.discord_logs_frame.winfo_children():
            widget.destroy()
        
        self.discord_logs = []
        self.avatars = {}
        
        if self.discord_logs_canvas:
            self.discord_logs_canvas.configure(scrollregion="0 0 0 0")
            
            if self.discord_logs_wrapper:
                self._update_canvas_width(self.discord_logs_canvas, self.discord_logs_wrapper)
        
        if hasattr(self.bot_controller, 'gui') and hasattr(self.bot_controller.gui, 'tools_page'):
            try:
                if hasattr(self.bot_controller.gui.tools_page, 'message_logger_page'):
                    pass
            except:
                pass
        
    def _update_canvas_width(self, canvas, logs_wrapper):
        try:
            available_width = logs_wrapper.winfo_width() - 35
            canvas.itemconfig(self.canvas_window, width=available_width)
        except:
            pass
            
    def _update_wraplength(self, event=None):
        if self.discord_logs_frame:
            try:
                new_width = self.discord_logs_frame.winfo_width() - 60
                for widget in self.discord_logs_frame.winfo_children():
                    if hasattr(widget, 'winfo_children'):
                        for child in widget.winfo_children():
                            if isinstance(child, ttk.Label) and hasattr(child, 'configure'):
                                if hasattr(child, 'cget') and child.cget('wraplength') > 0:
                                    child.configure(wraplength=max(300, new_width - 80))
            except:
                pass
                
    def _display_log(self, log_entry):
        if not self.discord_logs_frame:
            return

        entry = MessageLogEntry(
            parent=self.discord_logs_frame,
            root=self.root,
            bot_controller=self.bot_controller,
            avatars=self.avatars,
            log_entry=log_entry
        )
        self.logs.append(entry)  # keep track of all logs

    def draw_content(self, wrapper):
        self.root.bind("<Configure>", self._update_wraplength)
        
        self.discord_logs_inner_wrapper = ttk.Frame(wrapper)
        self.discord_logs_inner_wrapper.pack(fill=ttk.BOTH, expand=True, padx=10, pady=(10, 10))

        canvas = ttk.Canvas(self.discord_logs_inner_wrapper)
        scrollbar = ttk.Scrollbar(self.discord_logs_inner_wrapper, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas, style="dark.TFrame")

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        self.canvas_window = canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

        def resize_canvas(event):
            # Match the inner frame to the canvas width
            canvas.itemconfig(self.canvas_window, width=event.width)

        canvas.bind("<Configure>", resize_canvas)

        canvas.configure(yscrollcommand=scrollbar.set, background=self.root.style.colors.get("dark"))

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        

        self.discord_logs_frame = scroll_frame
        self.discord_logs_canvas = canvas
        self.discord_logs_wrapper = wrapper

        canvas.after(100, lambda: self._update_canvas_width(canvas, wrapper))

        self.discord_logs_canvas.bind("<Enter>", lambda e: self.discord_logs_canvas.bind_all("<MouseWheel>", self._on_mousewheel))
        self.discord_logs_canvas.bind("<Leave>", lambda e: self.discord_logs_canvas.unbind_all("<MouseWheel>"))
        self.discord_logs_canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.discord_logs_canvas.bind("<Button-4>", self._on_mousewheel)
        self.discord_logs_canvas.bind("<Button-5>", self._on_mousewheel)
    

        self._load_discord_logs()