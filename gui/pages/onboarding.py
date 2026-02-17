import os
import sys
import ttkbootstrap as ttk
import threading

from utils.config import Config
from utils import files
from gui.components import RoundedFrame, RoundedButton
from gui.helpers import Images

class OnboardingPage:
    def __init__(self, root, run, bot_controller):
        self.root = root
        self.run = run
        self.bot_controller = bot_controller
        self.width = 450
        self.height = 115
        self.images = Images()
        self.cfg = Config()
        self.entry = None
        self.root.bind("<Button-1>", self._remove_focus)
        self.token_entry_placeholder = "Paste your token here..."
        self.prefix_entry_placeholder = "Enter your desired prefix..."
       
    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()
       
    def _remove_focus(self, event):
        widget = event.widget
        if isinstance(widget, ttk.Entry):  # Ignore if clicking an entry field
            return
        self.root.focus_set()  # Set focus to the main window
        
    def _start(self, setup_webhooks):
        token = self.token_entry.get()
        prefix = self.prefix_entry.get()
        
        token = token.strip()
        prefix = prefix.strip()
        
        if token == self.token_entry_placeholder or token == "":
            print("Please enter a valid token.")
            return

        if prefix == self.prefix_entry_placeholder or prefix == "":
            print("Please enter a valid prefix.")
            return
        
        self.cfg.set("token", token, save=False)
        self.cfg.set("prefix", prefix, save=False)
        
        if setup_webhooks:
            with open(files.get_application_support() + "/data/cache/CREATE_WEBHOOKS", "w") as f:
                f.write("True")
                
        self.cfg.save()
        # os.execl(sys.executable, sys.executable, *sys.argv)
        self.clear()
        # threading.Thread(target=self.bot_controller.start, daemon=True).start()
        self.root.after(100, lambda: self.run())
        
    def _draw_token_entry(self, parent):
        entry_wrapper = RoundedFrame(parent, radius=(15, 15, 15, 15), bootstyle="dark.TFrame")
        # entry_wrapper.pack(fill=ttk.BOTH, padx=30, pady=30)
        
        def _focus_in(_):
            if self.token_entry.get() == self.token_entry_placeholder:
                self.token_entry.delete(0, "end")
                self.token_entry.configure(foreground="#cdcdcd", background="#1a1c1c", show="*")

        def _focus_out(_):
            if self.token_entry.get() == "":
                self.token_entry.insert(0, self.token_entry_placeholder)
                self.token_entry.configure(foreground="grey", background="#1a1c1c", show="")
        
        label = ttk.Label(entry_wrapper, text="Token", font=("Host Grotesk", 12))
        label.configure(background=self.root.style.colors.get("dark"))
        label.grid(row=0, column=0, sticky=ttk.W, padx=(12, 0), pady=(10, 8))
        
        self.token_entry = ttk.Entry(entry_wrapper, bootstyle="dark.TFrame", font=("Host Grotesk", 12))
        self.token_entry.insert(0, self.token_entry_placeholder)
        self.token_entry.configure(foreground="grey", background="#1a1c1c")
        self.token_entry.bind("<FocusIn>", _focus_in)
        self.token_entry.bind("<FocusOut>", _focus_out)
        self.token_entry.grid(row=0, column=1, sticky=ttk.EW, padx=(8, 10), pady=(10, 8), ipady=10, ipadx=10)
        entry_wrapper.grid_columnconfigure(1, weight=1)
            
        return entry_wrapper
    
    def _draw_prefix_entry(self, parent):
        entry_wrapper = RoundedFrame(parent, radius=(15, 15, 15, 15), bootstyle="dark.TFrame")
        # entry_wrapper.pack(fill=ttk.BOTH, padx=30, pady=30)
        
        def _focus_in(_):
            if self.prefix_entry.get() == self.prefix_entry_placeholder:
                self.prefix_entry.delete(0, "end")
                self.prefix_entry.configure(foreground="#cdcdcd", background="#1a1c1c")

        def _focus_out(_):
            if self.prefix_entry.get() == "":
                self.prefix_entry.insert(0, self.prefix_entry_placeholder)
                self.prefix_entry.configure(foreground="grey", background="#1a1c1c")
        
        label = ttk.Label(entry_wrapper, text="Prefix", font=("Host Grotesk", 12))
        label.configure(background=self.root.style.colors.get("dark"))
        label.grid(row=0, column=0, sticky=ttk.W, padx=(12, 0), pady=(10, 8))
        
        self.prefix_entry = ttk.Entry(entry_wrapper, bootstyle="dark.TFrame", font=("Host Grotesk", 12))
        self.prefix_entry.insert(0, self.prefix_entry_placeholder)
        self.prefix_entry.configure(foreground="grey", background="#1a1c1c")
        self.prefix_entry.bind("<FocusIn>", _focus_in)
        self.prefix_entry.bind("<FocusOut>", _focus_out)
        self.prefix_entry.grid(row=0, column=1, sticky=ttk.EW, padx=(8, 10), pady=(10, 8), ipady=10, ipadx=10)
        entry_wrapper.grid_columnconfigure(1, weight=1)
        
        prefix = self.cfg.get("prefix")
        if prefix != "":
            self.prefix_entry.delete(0, "end")
            self.prefix_entry.insert(0, prefix)
            self.prefix_entry.configure(foreground="#cdcdcd", background="#1a1c1c")
            
        return entry_wrapper
    
    def _draw_webhook_setup(self, parent):
        wrapper = RoundedFrame(parent, radius=(15, 15, 15, 15), bootstyle="dark.TFrame")
        inner_wrapper = ttk.Frame(wrapper, style="dark.TFrame")
        inner_wrapper.pack(fill=ttk.BOTH, padx=10, pady=10)

        # Configure grid columns to have equal weight
        inner_wrapper.grid_columnconfigure(0, weight=1, minsize=150)
        inner_wrapper.grid_columnconfigure(1, weight=1, minsize=180)
        inner_wrapper.grid_rowconfigure(0, weight=1)

        # Left Side - Text
        text_wrapper = ttk.Frame(inner_wrapper, style="dark.TFrame")
        # text_wrapper.pack(fill=ttk.BOTH, side=ttk.LEFT, expand=True)
        text_wrapper.grid(row=0, column=0, sticky=ttk.NSEW, pady=(0, 4), padx=(2, 0))

        title = ttk.Label(text_wrapper, text="Webhook Setup", font=("Host Grotesk", 14 if sys.platform != "darwin" else 20, "bold"))
        title.configure(background=self.root.style.colors.get("dark"))
        title.grid(row=0, column=0, sticky=ttk.W)

        description = ttk.Label(text_wrapper, text="Do you want Ghost to create a fresh server for sniper webhooks and rich embeds?", wraplength=180)
        description.configure(background=self.root.style.colors.get("dark"))
        description.grid(row=1, column=0, sticky=ttk.W)

        button_wrapper = ttk.Frame(text_wrapper, style="dark.TFrame")
        button_wrapper.grid(row=2, column=0, sticky="SEW", pady=(10, 0))
        text_wrapper.grid_rowconfigure(2, weight=1)

        continue_button = RoundedButton(button_wrapper, text="Continue", style="primary.TButton", command=lambda _: self._start(True))
        continue_button.grid(row=0, column=0, sticky=ttk.EW, padx=(0, 5))

        skip_button = RoundedButton(button_wrapper, text="Skip", style="danger.TButton", command=lambda _: self._start(False))
        skip_button.grid(row=0, column=1, sticky=ttk.EW)
        
        button_wrapper.grid_columnconfigure(0, weight=1, uniform="buttons")
        button_wrapper.grid_columnconfigure(1, weight=1, uniform="buttons")
        
        # Right Side - Image
        
        ghost_webhook_image = self.images.images["ghost_webhooks"]
        if ghost_webhook_image is None:
            print("Failed to load image.")
        
        webhooks_preview = ttk.Label(inner_wrapper, image=ghost_webhook_image)
        webhooks_preview.configure(background=self.root.style.colors.get("dark"))
        # webhooks_preview.pack(fill=ttk.BOTH, side=ttk.RIGHT)
        webhooks_preview.grid(row=0, column=1, sticky=ttk.NE, padx=(10, 0))

        return wrapper
        
    def draw(self):
        wrapper = RoundedFrame(self.root, radius=(25, 25, 25, 25), background=self.root.style.colors.get("bg"))
        wrapper.place(relx=0.5, rely=0.5, anchor="center")
        
        token_entry = self._draw_token_entry(wrapper)
        token_entry.pack(fill=ttk.BOTH, padx=30, pady=(30, 0))
        
        prefix_entry = self._draw_prefix_entry(wrapper)
        prefix_entry.pack(fill=ttk.BOTH, padx=30, pady=10)
        
        webhooks_setup = self._draw_webhook_setup(wrapper)
        webhooks_setup.pack(fill=ttk.BOTH, padx=30, pady=(0, 30))