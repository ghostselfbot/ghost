import os
import sys
import ttkbootstrap as ttk
import threading

from utils.config import Config
from utils import files
from gui.components import RoundedFrame, RoundedButton
from gui.helpers import Images, Style

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
        
        self.entered_token = ""
        self.entered_prefix = ""
       
    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()
       
    def _remove_focus(self, event):
        widget = event.widget
        if isinstance(widget, ttk.Entry):  # Ignore if clicking an entry field
            return
        self.root.focus_set()  # Set focus to the main window
        
    def _start(self, setup_webhooks):
        token = self.entered_token if self.entered_token else self.token_entry.get()
        prefix = self.entered_prefix if self.entered_prefix else self.prefix_entry.get()
        
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
        # self.clear()
        # threading.Thread(target=self.bot_controller.start, daemon=True).start()
        self.root.after(100, lambda: self.run(preserve_position=True))
        
    def _draw_token_entry(self, parent):
        entry_wrapper = RoundedFrame(parent, radius=(15, 15, 15, 15), bootstyle="secondary.TFrame")
        # entry_wrapper.pack(fill=ttk.BOTH, padx=30, pady=30)
        
        def _focus_in(_):
            if self.token_entry.get() == self.token_entry_placeholder:
                self.token_entry.delete(0, "end")
                self.token_entry.configure(foreground="#cdcdcd", background="#1a1c1c", show="*")

        def _focus_out(_):
            if self.token_entry.get() == "":
                self.token_entry.insert(0, self.token_entry_placeholder)
                self.token_entry.configure(foreground="grey", background="#1a1c1c", show="")
        
        # label = ttk.Label(entry_wrapper, text="Token", font=("Host Grotesk", 12 if sys.platform != "darwin" else 13))
        # label.configure(background=self.root.style.colors.get("secondary"))
        # label.grid(row=0, column=0, sticky=ttk.W, padx=(12, 0), pady=(10, 8))
        
        self.token_entry = ttk.Entry(entry_wrapper, bootstyle="secondary.TFrame", font=("Host Grotesk", 12 if sys.platform != "darwin" else 13))
        self.token_entry.insert(0, self.token_entry_placeholder)
        self.token_entry.configure(foreground="grey", background="#1a1c1c")
        self.token_entry.bind("<FocusIn>", _focus_in)
        self.token_entry.bind("<FocusOut>", _focus_out)
        self.token_entry.grid(row=0, column=0, sticky=ttk.EW, padx=12, pady=(10, 8), ipady=10, ipadx=10)
        entry_wrapper.grid_columnconfigure(0, weight=1)
            
        return entry_wrapper
    
    def _draw_prefix_entry(self, parent):
        entry_wrapper = RoundedFrame(parent, radius=(15, 15, 15, 15), bootstyle="secondary.TFrame")
        # entry_wrapper.pack(fill=ttk.BOTH, padx=30, pady=30)
        
        def _focus_in(_):
            if self.prefix_entry.get() == self.prefix_entry_placeholder:
                self.prefix_entry.delete(0, "end")
                self.prefix_entry.configure(foreground="#cdcdcd", background="#1a1c1c")

        def _focus_out(_):
            if self.prefix_entry.get() == "":
                self.prefix_entry.insert(0, self.prefix_entry_placeholder)
                self.prefix_entry.configure(foreground="grey", background="#1a1c1c")
        
        # label = ttk.Label(entry_wrapper, text="Prefix", font=("Host Grotesk", 12 if sys.platform != "darwin" else 13))
        # label.configure(background=self.root.style.colors.get("secondary"))
        # label.grid(row=0, column=0, sticky=ttk.W, padx=(12, 0), pady=(10, 8))
        
        self.prefix_entry = ttk.Entry(entry_wrapper, bootstyle="secondary.TFrame", font=("Host Grotesk", 12 if sys.platform != "darwin" else 13))
        self.prefix_entry.insert(0, self.prefix_entry_placeholder)
        self.prefix_entry.configure(foreground="grey", background="#1a1c1c")
        self.prefix_entry.bind("<FocusIn>", _focus_in)
        self.prefix_entry.bind("<FocusOut>", _focus_out)
        self.prefix_entry.grid(row=0, column=1, sticky=ttk.EW, padx=12, pady=(10, 8), ipady=10, ipadx=10)
        entry_wrapper.grid_columnconfigure(1, weight=1)
        
        prefix = self.cfg.get("prefix")
        if prefix != "":
            self.prefix_entry.delete(0, "end")
            self.prefix_entry.insert(0, prefix)
            self.prefix_entry.configure(foreground="#cdcdcd", background="#1a1c1c")
            
        return entry_wrapper
        
    def draw_webhook_setup(self, wrapper):
        self.clear_token_input()
        self.clear_prefix_input()
        inner_wrapper = RoundedFrame(wrapper, radius=(25, 25, 25, 25), background=self.root.style.colors.get("dark"), parent_background=self.root.style.colors.get("bg"))
        inner_wrapper.place(relx=0.5, rely=0.5, anchor="center")

        inner_wrapper.grid_columnconfigure(0, weight=1)
        inner_wrapper.grid_columnconfigure(1, weight=0)

        content_wrapper = ttk.Frame(inner_wrapper, style="dark.TFrame")
        content_wrapper.grid(row=0, column=0, sticky=ttk.NSEW, padx=30, pady=30)

        title = ttk.Label(content_wrapper, text="Setup webhooks?", font=("Host Grotesk", 20, "bold"))
        title.configure(background=self.root.style.colors.get("dark"))
        title.pack(fill=ttk.BOTH)
        
        subtitle = ttk.Label(content_wrapper, wraplength=220, text="Do you want Ghost to create a fresh Discord server for sniper webhooks and rich embeds?", font=("Host Grotesk", 14))
        subtitle.configure(background=self.root.style.colors.get("dark"))
        subtitle.pack(fill=ttk.BOTH, pady=(0, 10))

        button_wrapper = ttk.Frame(content_wrapper, style="dark.TFrame")
        button_wrapper.pack(fill=ttk.BOTH, pady=(20, 0))
        
        continue_btn = RoundedButton(button_wrapper, text="Yes", style="success.TButton", command=lambda _: self._start(True), pady=5, padx=15, radius=15)
        continue_btn.grid(row=0, column=0, sticky=ttk.EW, padx=(0, 2))

        skip_btn = RoundedButton(button_wrapper, text="Skip", style="danger.TButton", command=lambda _: self._start(False), pady=5, padx=15, radius=15)
        skip_btn.grid(row=0, column=1, sticky=ttk.EW, padx=(2, 0))

        button_wrapper.grid_columnconfigure(0, weight=1, uniform="buttons")
        button_wrapper.grid_columnconfigure(1, weight=1, uniform="buttons")

        ghost_webhook_image = self.images.images["ghost_webhooks"]
        if ghost_webhook_image is None:
            print("Failed to load image.")

        webhooks_preview = ttk.Label(inner_wrapper, image=ghost_webhook_image)
        webhooks_preview.configure(background=self.root.style.colors.get("dark"))
        webhooks_preview.grid(row=0, column=1, sticky=ttk.NE, padx=(10, 30), pady=30)

    def draw_prefix_input(self, wrapper):
        self.prefix_input_inner_wrapper = RoundedFrame(wrapper, radius=(25, 25, 25, 25), background=self.root.style.colors.get("dark"), parent_background=self.root.style.colors.get("bg"))
        self.prefix_input_inner_wrapper.place(relx=0.5, rely=0.5, anchor="center")
        
        title = ttk.Label(self.prefix_input_inner_wrapper, text="Now choose a prefix.", font=("Host Grotesk", 20, "bold"))
        title.configure(background=self.root.style.colors.get("dark"))
        title.pack(fill=ttk.BOTH, padx=30, pady=(30, 0))
        
        subtitle = ttk.Label(self.prefix_input_inner_wrapper, wraplength=350, text="Ghost uses old school bot command prefixes. Set a prefix to execute commands.", font=("Host Grotesk", 14))
        subtitle.configure(background=self.root.style.colors.get("dark"))
        subtitle.pack(fill=ttk.BOTH, padx=30, pady=(0, 10))
        
        prefix_entry = self._draw_prefix_entry(self.prefix_input_inner_wrapper)
        prefix_entry.pack(fill=ttk.BOTH, padx=30, pady=(20, 10))
        
        def continue_to_webhook_setup(_=None):
            prefix = self.prefix_entry.get().strip()
            if prefix == "" or prefix == self.prefix_entry_placeholder:
                print("Please enter a valid prefix.")
                return

            self.entered_prefix = prefix
            self.cfg.set("prefix", prefix, save=False)
            self.cfg.save()
            self.clear_prefix_input()
            self.draw_webhook_setup(wrapper)
        
        next_btn = RoundedButton(self.prefix_input_inner_wrapper, text="Next", style="primary.TButton", command=continue_to_webhook_setup, pady=5, padx=15, radius=15)
        next_btn.pack(pady=(0, 30), fill=ttk.BOTH, padx=30)
        
    def clear_token_input(self):
        if hasattr(self, "token_input_inner_wrapper"):
            self.token_input_inner_wrapper.destroy()
        
    def clear_prefix_input(self):
        if hasattr(self, "prefix_input_inner_wrapper"):
            self.prefix_input_inner_wrapper.destroy()

    def draw_token_input(self, wrapper):
        self.clear_welcome()
        self.token_input_inner_wrapper = RoundedFrame(wrapper, radius=(25, 25, 25, 25), background=self.root.style.colors.get("dark"), parent_background=self.root.style.colors.get("bg"))
        self.token_input_inner_wrapper.place(relx=0.5, rely=0.5, anchor="center")
        
        title = ttk.Label(self.token_input_inner_wrapper, text="Let's get started!", font=("Host Grotesk", 20, "bold"))
        title.configure(background=self.root.style.colors.get("dark"))
        title.pack(fill=ttk.BOTH, padx=30, pady=(30, 0))
        
        subtitle = ttk.Label(self.token_input_inner_wrapper, wraplength=350, text="Ghost runs on your own account. Please enter your Discord token to continue.", font=("Host Grotesk", 14))
        subtitle.configure(background=self.root.style.colors.get("dark"))
        subtitle.pack(fill=ttk.BOTH, padx=30, pady=(0, 10))
        
        token_entry = self._draw_token_entry(self.token_input_inner_wrapper)
        token_entry.pack(fill=ttk.BOTH, padx=30, pady=(20, 10))
        
        def continue_to_prefix(_=None):
            token = self.token_entry.get().strip()
            if token == "" or token == self.token_entry_placeholder:
                print("Please enter a valid token.")
                return

            self.entered_token = token
            self.cfg.set("token", token, save=False)
            self.cfg.save()
            self.clear_token_input()
            self.draw_prefix_input(wrapper)

        next_btn = RoundedButton(self.token_input_inner_wrapper, text="Next", style="primary.TButton", command=continue_to_prefix, pady=5, padx=15, radius=15)
        next_btn.pack(pady=(0, 30), fill=ttk.BOTH, padx=30)
        
    def clear_welcome(self):
        self.welcome_subtitle.destroy()
        self.welcome_title.destroy()
        self.start_btn.destroy()
        
    def draw(self, wrapper):
        self.welcome_subtitle = ttk.Label(wrapper, text="Welcome to", font=("Host Grotesk", 16, "bold"))
        self.welcome_subtitle.configure(background=self.root.style.colors.get("bg"), foreground=Style.LIGHT_GREY.value)
        
        self.welcome_title = ttk.Label(wrapper, text="Ghost", font=("Climate Crisis", 64))
        self.welcome_title.configure(background=self.root.style.colors.get("bg"))
        
        # center both labels vertically and horizontally in the middle of the wrapper
        self.welcome_subtitle.place(relx=0.5, rely=0.2, anchor="center")
        self.welcome_title.place(relx=0.5, rely=0.35, anchor="center")
        
        self.start_btn = RoundedButton(wrapper, text="Get Started", style="primary.TButton", command=lambda _: self.draw_token_input(wrapper), radius=(20, 20, 20, 20), font=("Host Grotesk", 14 if sys.platform != "darwin" else 16, "bold"), pady=5, padx=15)
        self.start_btn.place(relx=0.5, rely=0.75, anchor="center")