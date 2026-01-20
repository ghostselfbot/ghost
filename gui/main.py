import certifi
import os, sys

os.environ["SSL_CERT_FILE"] = certifi.where()
import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.utility import enable_high_dpi_awareness

from utils.notifier import Notifier
from utils.config import Config
import utils.console as logging
from utils.files import resource_path
from utils import uninstall_fonts

from gui.pages import HomePage, LoadingPage, SettingsPage, OnboardingPage, ScriptsPage, ToolsPage
from gui.components import Sidebar, Console, Titlebar
from gui.helpers import Images, Layout

class GhostGUI:
    def __init__(self, bot_controller):
        self.size = (650, 530)
        self.bot_controller = bot_controller
            
        enable_high_dpi_awareness()
        
        self.root = ttk.tk.Tk()
        self.root.size = self.size
        self.root.title("Ghost")
        # self.root.resizable(False, False)
        if os.name == "nt":
            self.root.iconbitmap(resource_path("data/icon.ico"))
        self.root.geometry(f"{self.size[0]}x{self.size[1]}")
        self.root.minsize(self.size[0], self.size[1])
        self.root.protocol("WM_DELETE_WINDOW", self.quit)
        self.root.createcommand('::tk::mac::ReopenApplication', self._show_window)
        
        self.root.style = ttk.Style()
        # self.root.style.theme_use("darkly")
        self.root.style.load_user_themes(resource_path("data/gui_theme.json"))
        self.root.style.theme_use("ghost")
        self.root.style.configure("TEntry", background=self.root.style.colors.get("dark"), fieldbackground=self.root.style.colors.get("secondary"))
        self.root.style.configure("TCheckbutton", background=self.root.style.colors.get("dark"))
        self.root.style.configure("TMenubutton", font=("Host Grotesk",))
        self.root.style.configure("TCheckbutton", font=("Host Grotesk",))
        self.root.style.configure("TEntry", font=("Host Grotesk",))
        self.root.style.configure("TLabel", font=("Host Grotesk",))
        self.root.style.configure("TButton", font=("Host Grotesk",))
        
        self.root.overrideredirect(True)
        self.root.attributes("-transparent", True)
        self.root.configure(bg="systemTransparent")
        
        self.root.focus()
        
        self.cfg      = Config()
        self.notifier = Notifier()
        self.images   = Images()
        self.sidebar  = Sidebar(self.root)
        
        self.sidebar.add_button("home", self.draw_home)
        # self.sidebar.add_button("console", self.draw_console)
        self.sidebar.add_button("settings", self.draw_settings)
        self.sidebar.add_button("scripts", self.draw_scripts)
        self.sidebar.add_button("tools", self.draw_tools)
        self.sidebar.add_button("logout", self.quit)
        
        self.titlebar        = Titlebar(self.root)
        self.layout          = Layout(self.root, self.sidebar, self.titlebar)
        self.loading_page    = LoadingPage(self.root)
        self.onboarding_page = OnboardingPage(self.root, self.run, self.bot_controller)
        self.console         = Console(self.root, self.bot_controller)
        self.home_page       = HomePage(self.root, self.bot_controller, self._restart_bot, self.console)
        self.settings_page   = SettingsPage(self.root, self.bot_controller)
        self.scripts_page    = ScriptsPage(self, self.bot_controller, self.images)
        self.tools_page      = ToolsPage(self.root, self.bot_controller, self.images, self.layout)
        
        logging.set_gui(self)
        
        if bot_controller:
            self.bot_controller.set_gui(self)
            
        self.root.overrideredirect(False)
        self.layout.center_window(self.size[0], self.size[1])
        self.root.update_idletasks()

        # When restored, remove decorations again
        self.root.after(10, lambda: self.root.overrideredirect(True))

    def _show_window(self):
        self.root.deiconify()
        
    def draw_home(self, restart=False, start=False):
        self.sidebar.set_current_page("home")
        self.layout.clear()
        main = self.layout.main()
        self.home_page.draw(main, restart=restart, start=start)
    
    def draw_console(self):
        self.sidebar.set_current_page("console")
        self.layout.clear()
        main = self.layout.main()
        self.console.draw(main)
        
    def draw_settings(self):
        self.sidebar.set_current_page("settings")
        self.layout.clear()
        main = self.layout.main(scrollable=True)
        self.settings_page.draw(main)
        
    def draw_scripts(self):
        self.sidebar.set_current_page("scripts")
        self.layout.clear()
        main = self.layout.main(padx=(23, 24))
        self.scripts_page.draw(main)
        
    def draw_tools(self):
        self.sidebar.set_current_page("tools")
        self.layout.clear()
        main = self.layout.main(scrollable=True)
        self.tools_page.draw(main)
        
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

        self.root.after(50, lambda: self.notifier.send("Ghost", "Ghost has successfully started!"))
        self.root.after(50, lambda: self.draw_home())

    def _check_bot_started(self):
        if self.bot_controller.bot_running:
            self.root.after(50, self._on_bot_ready)
        else:
            self.root.after(500, self._check_bot_started)

    def run(self):
        if self.cfg.get("token") == "":
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