import certifi
import os, sys

if sys.platform == "win32":
    import hPyT

os.environ["SSL_CERT_FILE"] = certifi.where()
import ttkbootstrap as ttk

from utils.notifier import Notifier
from utils.config import Config
import utils.console as logging
from utils.files import resource_path

from gui.pages import HomePage, LoadingPage, SettingsPage, OnboardingPage, ScriptsPage, ToolsPage
from gui.components import Sidebar, Console, Titlebar, RoundedFrame
from gui.helpers import Images, Layout, Style

class GhostGUI:
    def __init__(self, bot_controller):
        self.resize_grip_size = 5
        self.size = (700, 530)
        self.bot_controller = bot_controller
        self.resize_grips = {}
        
        self.root = ttk.tk.Tk()
        self.root.size = self.size
        self.root.title("Ghost")

        if sys.platform != "darwin":
            self.root.tk.call('tk', 'scaling', 1)
        
        if sys.platform == "darwin":
            self.root.overrideredirect(False)
            self.root.withdraw()
        
        if sys.platform == "win32":
            self.root.iconbitmap(resource_path("data/icon.ico"))
            hPyT.title_bar.hide(self.root, no_span=True)
            hPyT.corner_radius.set(self.root, style="round")
            hPyT.window_dwm.toggle_dwm_transitions(self.root, enabled=True)
            hPyT.window_frame.minimize(self.root)
        
        self.root.minsize(self.size[0], self.size[1])
        self.root.protocol("WM_DELETE_WINDOW", self.quit)
        
        self.root.style = ttk.Style()
        # self.root.style.theme_use("darkly")
        self.root.style.load_user_themes(resource_path("data/gui_theme.json"))
        self.root.style.theme_use("ghost")
        self.root.style.configure("TEntry",       background=self.root.style.colors.get("dark"), fieldbackground=Style.ENTRY_BG.value, font=("Host Grotesk", 12 if sys.platform != "darwin" else 13), bordercolor=Style.ENTRY_BG.value, foreground="#ffffff", borderstyle="flat", borderwidth=0)
        self.root.style.configure("TCheckbutton", background=self.root.style.colors.get("dark"), font=("Host Grotesk", 12 if sys.platform != "darwin" else 13))
        self.root.style.configure("TMenubutton",  font=("Host Grotesk", 12 if sys.platform != "darwin" else 13))
        self.root.style.configure("TLabel",       font=("Host Grotesk", 12 if sys.platform != "darwin" else 13))
        self.root.style.configure("TButton",      font=("Host Grotesk", 12 if sys.platform != "darwin" else 13))
        
        if sys.platform == "darwin":
            self.root.attributes("-transparent", True)
            self.root.configure(bg="systemTransparent")
        # elif sys.platform == "win32":
        #     self.root.configure(bg="#ff00ff")
        #     self.root.attributes("-transparentcolor", "#ff00ff")
        # else:
        #     self.root.attributes("-alpha", 1)
        
        self.cfg      = Config()
        self.notifier = Notifier()
        self.images   = Images()
        self.sidebar  = Sidebar(self.root)
        
        self.sidebar.add_button("home",     self.draw_home)
        # self.sidebar.add_button("console", self.draw_console)
        self.sidebar.add_button("settings", self.draw_settings)
        self.sidebar.add_button("scripts",  self.draw_scripts)
        self.sidebar.add_button("tools",    self.draw_tools)
        self.sidebar.add_button("logout",   self.quit)
        
        if self.cfg.get("token") != "":
            self._create_resize_grips()
        
        self.titlebar        = Titlebar(self.root, self.images)
        self.layout          = Layout(self.root, self.sidebar, self.titlebar, self.resize_grips)
        self.loading_page    = LoadingPage(self.root)
        self.onboarding_page = OnboardingPage(self.root, self.run, self.bot_controller)
        self.console         = Console(self.root, self.bot_controller)
        self.home_page       = HomePage(self.root, self.bot_controller, self._restart_bot, self.console)
        self.settings_page   = SettingsPage(self.root, self.bot_controller)
        self.scripts_page    = ScriptsPage(self, self.bot_controller, self.images)
        self.tools_page      = ToolsPage(self.root, self.bot_controller, self.images, self.layout, self._position_resize_grips)
        
        logging.set_gui(self)
        
        if bot_controller:
            self.bot_controller.set_gui(self)
            
        if sys.platform == "darwin":
            self.layout.center_window(self.size[0], self.size[1])
            self.root.update_idletasks()
            
            self.root.update_idletasks()
            self.root.createcommand('::tk::mac::ReopenApplication', self._show_window)
            self.root.bind("<Map>", lambda _: self._window_mapped())
            
            self.root.after(450, self._show_window)
            self.root.after(500, self._window_mapped)

    def _pre_load_images(self, user):
        print("Pre-loading images...")
        avatar_url = user.avatar.url if user and user.avatar else "https://ia600305.us.archive.org/31/items/discordprofilepictures/discordblue.png"
        self.bot_controller.get_avatar_from_url(avatar_url, size=65, radius=65//2)
        self.images.get_majority_color_from_url(avatar_url)

        rpc = self.cfg.get_rich_presence()
        if rpc and rpc.large_image:
            self.images.load_image_from_url(rpc.large_image if rpc.large_image else "https://www.ghostt.cc/assets/ghost.png", (64, 64), 5)
        
        print("Finished pre-loading images.")

    def _window_mapped(self):
        self.root.update_idletasks()
        self.root.overrideredirect(True)
        self.root.state("normal")
        
    def _show_window(self):
        self.root.update_idletasks()
        self.root.deiconify()
        self.root.overrideredirect(True)
        
    def _create_resize_grips(self):
        if sys.platform != "darwin":
            return
        
        self.resize_grips = {}

        # Bottom grip
        bottom = RoundedFrame(
            self.root,
            radius=(0, 0, 25, 25),
            background=Style.WINDOW_BORDER.value
        )
        bottom.bind("<B1-Motion>", self._resize_window)
        bottom.bind("<Enter>", lambda e: self.root.config(cursor="sb_v_double_arrow"))
        bottom.bind("<Leave>", lambda e: self.root.config(cursor=""))
        self.resize_grips["bottom"] = bottom

        # Right grip
        right = RoundedFrame(
            self.root,
            radius=(0, 25, 25, 0),
            background=Style.WINDOW_BORDER.value
        )
        right.bind("<B1-Motion>", self._resize_window)
        right.bind("<Enter>", lambda e: self.root.config(cursor="sb_h_double_arrow"))
        right.bind("<Leave>", lambda e: self.root.config(cursor=""))
        self.resize_grips["right"] = right

        self._position_resize_grips()
        
    def _position_resize_grips(self):
        if sys.platform != "darwin":
            return
        
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        s = self.resize_grip_size

        self.resize_grips["bottom"].place(
            x=0, y=h - s, width=w, height=s
        )

        self.resize_grips["right"].place(
            x=w - s, y=0, width=s, height=h
        )

        for grip in self.resize_grips.values():
            ttk.tk.Misc.lift(grip)
            
    def _resize_window(self, event):
        # resize the window based on mouse position, save the new positions so resizing continues smoothly
        x = self.root.winfo_pointerx()
        y = self.root.winfo_pointery()
        self.root.geometry(f"{x - self.root.winfo_x()}x{y - self.root.winfo_y()}")
        self.root.update_idletasks()
        
        self.size = (self.root.winfo_width(), self.root.winfo_height())
        self._position_resize_grips()
        
    def draw_home(self, restart=False, start=False):
        self.sidebar.set_current_page("home")
        self.layout.clear()
        main = self.layout.main()
        self.home_page.draw(main, restart=restart, start=start)
        self._position_resize_grips()
    
    # def draw_console(self):
    #     self.sidebar.set_current_page("console")
    #     self.layout.clear()
    #     main = self.layout.main()
    #     self.console.draw(main)
        
    def draw_settings(self):
        self.sidebar.set_current_page("settings")
        self.layout.clear()
        main = self.layout.main(scrollable=True)
        self.settings_page.draw(main)
        self._position_resize_grips()
        
    def draw_scripts(self):
        self.sidebar.set_current_page("scripts")
        self.layout.clear()
        main = self.layout.main()
        self.scripts_page.draw(main)
        self._position_resize_grips()
        
    def draw_tools(self):
        self.sidebar.set_current_page("tools")
        self.layout.clear()
        main = self.layout.main(scrollable=False)
        self.tools_page.draw(main)
        self._position_resize_grips()
        
    # def draw_loading(self):
    #     self.layout.hide_titlebar()
    #     self.layout.stick_window()
    #     self.layout.resize(400, 90)
    #     self.layout.center_window(400, 90)
    #     self.loading_page.draw()
    #     self.root.after(100, self._check_bot_restarted)
        
    def _check_bot_restarted(self):
        if self.bot_controller.running:
            self.root.after(0, self._on_bot_ready)
        else:
            self.root.after(1500, self._check_bot_restarted)
        
    def _restart_bot(self):
        self.cfg.save()
        self.layout.clear()
        main = self.layout.main()
        self.sidebar.set_current_page("home")
        self.root.after(50, self.sidebar.disable)
        self.root.after(50, self.home_page.draw(main, restart=True))
        
        self.root.after(100, self.bot_controller.restart)
        self.root.after(500, self._check_bot_started)
        
    def _on_bot_ready(self):
        # self.layout.show_titlebar()
        # self.layout.unstick_window()
        # self.loading_page.clear()
        
        if not self.root.winfo_ismapped():
            self.layout.resize(600, 530)
            self.layout.center_window(600, 530)
        else:
            # check if the window size is too small
            width, height = self.root.winfo_width(), self.root.winfo_height()
            if width < 600 or height < 530:
                self.layout.resize(600, 530)
                self.layout.center_window(600, 530)

        user = self.bot_controller.get_user()
        self._pre_load_images(user)
        self.root.after(50, lambda: self.notifier.send("Ghost", "Ghost has successfully started!"))
        self.root.after(50, lambda: self.draw_home())

    def _check_bot_started(self):
        if self.bot_controller.bot_running:
            self.root.after(50, self._on_bot_ready)
        else:
            self.root.after(500, self._check_bot_started)

    def run(self):
        if self.cfg.get("token") == "":
            if sys.platform == "win32":
                self.root.after(50, lambda: hPyT.window_frame.restore(self.root))
                self.root.after(75, lambda: hPyT.window_frame.center(self.root))
            else:
                self.layout.center_window(self.size[0], self.size[1])
            # self.layout.resize(450, 372)
            # self.layout.center_window(450, 372)
            self.onboarding_page.draw()
            self.root.mainloop()
            return
        
        if not self.bot_controller.running:
            self.bot_controller.start()
        
        self.layout.center_window(self.size[0], self.size[1])
        # self.layout.hide_titlebar()
        # self.layout.stick_window()
        # self.layout.resize(400, 90)
        # self.layout.center_window(400, 90)
        # self.loading_page.draw()
        self.root.after(25, self.sidebar.disable)
        self.draw_home(start=True)
        
        if sys.platform == "win32":
            self.root.after(50, lambda: hPyT.window_frame.restore(self.root))
            self.root.after(75, lambda: hPyT.window_frame.center(self.root))

        self.root.after(100, self._check_bot_started)
        self.root.mainloop()
        
    def quit(self):
        # if str(Messagebox.yesno("Are you sure you want to quit?", title="Ghost")).lower() == "yes":
        #     # uninstall_fonts()
        #     # if os.name == "nt":
        #     #     os.kill(os.getpid(), 9)
        #     # else:
        #     #     os._exit(0)
        #     self.root.destroy()
        #     sys.exit(0)
        self.root.destroy()
        sys.exit(0)
                
    def run_on_main_thread(self, func, *args, **kwargs):
        self.root.after(0, lambda: func(*args, **kwargs))

if __name__ == "__main__":
    gui = GhostGUI()
    gui.run()