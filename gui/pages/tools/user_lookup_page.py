import sys
import ttkbootstrap as ttk
from gui.components import RoundedFrame, ToolPage

class UserLookupPage(ToolPage):
    def __init__(self, toolspage, root, bot_controller, images, layout):
        super().__init__(toolspage, root, bot_controller, images, layout, title="User Lookup", frame=None)
        self.search_entry = None  # Initialize search entry to None
        self.user = None
        self.user_avatar = None
        self.search_results_widget = None
        self.wrapper = None  # Initialize wrapper to None
        
    def _search_user(self, user_id):
        if not user_id.isdigit():
            return  # Invalid user ID
        user = self.bot_controller.get_user_from_id(user_id)
        self.user = user
        
        avatar_url = self.user.avatar.url if self.user and self.user.avatar else "https://ia600305.us.archive.org/31/items/discordprofilepictures/discordblue.png"
        self.user_avatar = self.bot_controller.get_avatar_from_url(avatar_url, size=100, radius=10)
        
        if self.search_results_widget:
            self.search_results_widget.destroy()
        self.search_results_widget = self._draw_search_results(self.wrapper)
        self.search_results_widget.pack(side=ttk.TOP, fill=ttk.BOTH, expand=True)

    def _draw_search_bar(self, parent):
        entry_wrapper = RoundedFrame(parent, radius=(15, 15, 15, 15), bootstyle="dark.TFrame")
        # entry_wrapper.pack(fill=ttk.BOTH)
        
        placeholder_text = "Search a Discord user ID..."
        
        def on_focus_in(event):
            if self.search_entry.get() == placeholder_text:
                self.search_entry.delete(0, ttk.END)
                self.search_entry.configure(foreground="white")
                
        def on_focus_out(event):
            if self.search_entry.get() == "":
                self.search_entry.insert(0, placeholder_text)
                self.search_entry.configure(foreground="grey")
        
        self.search_entry = ttk.Entry(entry_wrapper, bootstyle="dark.TFrame", font=("Host Grotesk",))
        self.search_entry.grid(row=0, column=0, sticky=ttk.EW, padx=(18, 0), pady=10, columnspan=2, ipady=10)
        self.search_entry.configure(foreground="grey")
        self.search_entry.insert(0, placeholder_text)
        self.search_entry.bind("<FocusIn>", on_focus_in)
        self.search_entry.bind("<FocusOut>", on_focus_out)
        self.search_entry.bind("<Return>", lambda e: self._search_user(self.search_entry.get()))
        
        search_button = ttk.Label(entry_wrapper, image=self.images.get("search"), style="dark.TButton")
        search_button.grid(row=0, column=2, sticky=ttk.E, padx=(0, 10), pady=10)
        search_button.bind("<Button-1>", lambda e: self._search_user(self.search_entry.get()))
        
        entry_wrapper.columnconfigure(1, weight=1)
        
        return entry_wrapper

    def _draw_search_results(self, parent):
        wrapper = RoundedFrame(parent, radius=(15, 15, 15, 15), bootstyle="dark.TFrame")
        
        if self.user_avatar:
            avatar_label = ttk.Label(wrapper, image=self.user_avatar)
            avatar_label.configure(background=self.root.style.colors.get("dark"))
            avatar_label.grid(row=0, column=1, sticky=ttk.E, padx=15, pady=15)
            wrapper.grid_columnconfigure(1, weight=1)
            
        if self.user:
            user_info_wrapper = ttk.Frame(wrapper, style="dark.TFrame")
            user_info_wrapper.grid(row=0, column=0, sticky=ttk.NSEW, padx=(15, 0), pady=15)
            
            display_name = ttk.Label(user_info_wrapper, text=self.user.display_name, font=("Host Grotesk", 16 if sys.platform != "darwin" else 20, "bold"))
            display_name.configure(background=self.root.style.colors.get("dark"))
            display_name.grid(row=0, column=1, sticky=ttk.W)
            
            if self.user.bot:
                bot_tag = ttk.Label(user_info_wrapper, text="Bot", font=("Host Grotesk", 12 if sys.platform != "darwin" else 14), foreground="red")
                bot_tag.configure(background=self.root.style.colors.get("dark"))
                bot_tag.grid(row=0, column=2, sticky=ttk.W)

            username = ttk.Label(user_info_wrapper, text=f"@{self.user.name}", font=("Host Grotesk", 12 if sys.platform != "darwin" else 14))
            username.configure(background=self.root.style.colors.get("dark"), foreground="lightgrey")
            username.grid(row=1, column=1, sticky=ttk.W)
            
            user_id = ttk.Label(user_info_wrapper, text=f"ID: {self.user.id}", font=("Host Grotesk", 12 if sys.platform != "darwin" else 14))
            user_id.configure(background=self.root.style.colors.get("dark"))
            user_id.grid(row=2, column=1, sticky=ttk.W, pady=(5, 0))
        
        return wrapper

    def draw_content(self, wrapper):
        self.wrapper = wrapper
        search_bar = self._draw_search_bar(self.wrapper)
        search_bar.pack(side=ttk.TOP, fill=ttk.X, pady=(0, 10))

        self.search_results_widget = self._draw_search_results(self.wrapper)
        self.search_results_widget.pack(side=ttk.TOP, fill=ttk.BOTH, expand=True)