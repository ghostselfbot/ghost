import os, sys
import ttkbootstrap as ttk

from ttkbootstrap.scrolled import ScrolledFrame
from ttkbootstrap.dialogs import Messagebox
from gui.components import RoundedFrame
from gui.helpers.style import Style

# Uncomment the below to enable the dedicated script page.
# Please be aware this is a work in progress and the current state of the page is laggy and sometimes unresponsive.

# from gui.pages.script import ScriptPage

from utils.config import Config
from utils.files import open_path_in_explorer, get_application_support
from utils.defaults import DEFAULT_SCRIPT

class ScriptsPage:
    def __init__(self, root, bot_controller, images):
        self.gui = root
        self.root = root.root
        self.bot_controller = bot_controller
        self.images = images
        self.cfg = Config()
        self.script_frames = []
    
    def _open_editor(self, script):
        # Uncomment the below to enable the dedicated script page.
        # Please be aware this is a work in progress and the current state of the page is laggy and sometimes unresponsive.
        
        # self.gui.sidebar.set_current_page("scripts")
        # self.gui.layout.clear()
        # main = self.gui.layout.main()
        # script_page = ScriptPage(self.gui, script)
        # script_page.draw(main)
        
        
        # Please comment out the below to enable the dedicated script page!
        # Please be aware this is a work in progress and the current state of the page is laggy and sometimes unresponsive.
        
        if sys.platform == "darwin":
            try:
                os.system(f"code '{get_application_support()}/scripts/{script}'")
            except:
                os.system(f"open -a TextEdit '{get_application_support()}/scripts/{script}'")
        elif sys.platform == "win32":
            try:
                os.system(f"code '{get_application_support()}\\scripts\\{script}'")
            except:
                os.system(f"notepad '{get_application_support()}\\scripts\\{script}'")
        else:
            try:
                os.system(f"subl '{get_application_support()}/scripts/{script}'")
            except:
                os.system(f"gedit '{get_application_support()}/scripts/{script}'")
                
    def _new_scripts_listener(self):
        current_scripts = set(self.cfg.get_scripts())
        previous_scripts = set(self.bot_controller.startup_scripts)

        if current_scripts != previous_scripts:
            try:
                if not self.restart_warning.winfo_ismapped():
                    self.restart_warning.pack(fill=ttk.X, side=ttk.TOP, pady=(10, 0))
            except:
                pass
        else:
            try:
                if self.restart_warning.winfo_ismapped():
                    self.restart_warning.pack_forget()
            except:
                pass

        self.root.after(1000, self._new_scripts_listener)
                
    def _listen_to_directory(self):
        current_scripts = [script["name"] for script in self.script_frames]
        files = self.cfg.get_scripts()

        for script in files:
            if script not in current_scripts:
                script_frame = self._draw_script_frame(self.scripts_wrapper, script)
                script_frame.pack(fill=ttk.X, pady=5)
                self.script_frames.append({
                    "name": script,
                    "frame": script_frame
                })
                
        for script in current_scripts:
            if script not in files:
                for frame in self.script_frames:
                    if frame["name"] == script:
                        tk_frame = frame["frame"]
                        tk_frame.pack_forget()
                        self.script_frames.remove(frame)
                        break
                
        self.root.after(500, self._listen_to_directory)
                
    def _delete_script(self, script):
        if str(Messagebox.yesno("Are you sure you want to delete this script?", title="Ghost")).lower() == "yes":
            os.remove(get_application_support() + f"/scripts/{script}")
            self.gui.draw_scripts()
                
    def _create_script(self):
        # create a new script file, the name is example.py, if there is already a file with the same name, start a sequence and call it example1.py, example2.py, etc.
        num = 0
        name = f"example.py"
        
        if not os.path.exists(get_application_support() + "/scripts"):
            os.makedirs(get_application_support() + "/scripts")
            
        while os.path.exists(get_application_support() + f"/scripts/{name}"):
            num += 1
            name = f"example{num}.py"
            
        with open(get_application_support() + f"/scripts/{name}", "w") as file:
            file.write(DEFAULT_SCRIPT)
            
        self.gui.draw_scripts()
        
    def _search_scripts(self, event):
        search_query = self.search_entry.get()
        
        if search_query == "Search local scripts...":
            return
        
        for frame in self.script_frames:
            frame["frame"].pack_forget()
       
        if search_query == "":
            for frame in self.script_frames:
                frame["frame"].pack(fill=ttk.X, pady=5)
            return
            
        for frame in self.script_frames:
            if search_query.lower() in frame["name"].lower():
                frame["frame"].pack(fill=ttk.X, pady=5)
        
    def _draw_search_bar(self, parent):
        entry_wrapper = RoundedFrame(parent, radius=(15, 15, 15, 15), bootstyle="secondary.TFrame")
        # entry_wrapper.pack(fill=ttk.BOTH)
        
        placeholder_text = "Search local scripts..."
        
        def on_focus_in(event):
            if self.search_entry.get() == placeholder_text:
                self.search_entry.delete(0, ttk.END)
                self.search_entry.configure(foreground="white")
                
        def on_focus_out(event):
            if self.search_entry.get() == "":
                self.search_entry.insert(0, placeholder_text)
                self.search_entry.configure(foreground="grey")
        
        self.search_entry = ttk.Entry(entry_wrapper, bootstyle="secondary.TFrame", font=("Host Grotesk",))
        self.search_entry.grid(row=0, column=0, sticky=ttk.EW, padx=(18, 0), pady=10, columnspan=2, ipady=10)
        self.search_entry.configure(foreground="grey")
        self.search_entry.insert(0, placeholder_text)
        self.search_entry.bind("<FocusIn>", on_focus_in)
        self.search_entry.bind("<FocusOut>", on_focus_out)
        self.search_entry.bind("<Return>", self._search_scripts)
        # self.search_entry.bind("<Key>", self._search_scripts)
        
        search_button = ttk.Label(entry_wrapper, image=self.images.get("search"), style="secondary.TButton")
        search_button.grid(row=0, column=2, sticky=ttk.E, padx=(0, 10), pady=10)
        search_button.bind("<Button-1>", self._search_scripts)
        
        entry_wrapper.columnconfigure(1, weight=1)
        
        return entry_wrapper
    
    def _draw_open_folder_button(self, parent):
        def _hover_enter(_):
            wrapper.set_background(background=Style.SETTINGS_PILL_HOVER.value)
            open_folder_button.configure(background=Style.SETTINGS_PILL_HOVER.value)
            
        def _hover_leave(_):
            wrapper.set_background(background=self.root.style.colors.get("secondary"))
            open_folder_button.configure(background=self.root.style.colors.get("secondary"))
        
        wrapper = RoundedFrame(parent, radius=(10, 10, 10, 10), bootstyle="secondary")
        wrapper.bind("<Button-1>", lambda e: open_path_in_explorer(get_application_support() + "/scripts"))
        wrapper.bind("<Enter>", _hover_enter)
        wrapper.bind("<Leave>", _hover_leave)
        
        open_folder_button = ttk.Label(wrapper, image=self.images.get("folder-open"), style="secondary")
        open_folder_button.configure(background=self.root.style.colors.get("secondary"))
        open_folder_button.pack(side=ttk.LEFT, padx=15, pady=14)
        open_folder_button.bind("<Button-1>", lambda e: open_path_in_explorer(get_application_support() + "/scripts"))
        open_folder_button.bind("<Enter>", _hover_enter)
        open_folder_button.bind("<Leave>", _hover_leave)
        
        return wrapper
    
    def _draw_plus_button(self, parent):
        def _hover_enter(_):
            wrapper.set_background(background=Style.PRIMARY_BTN_HOVER.value)
            plus_button.configure(background=Style.PRIMARY_BTN_HOVER.value)
            
        def _hover_leave(_):
            wrapper.set_background(background=self.root.style.colors.get("primary"))
            plus_button.configure(background=self.root.style.colors.get("primary"))
        
        wrapper = RoundedFrame(parent, radius=(10, 10, 10, 10), bootstyle="primary")
        wrapper.bind("<Button-1>", lambda e: self._create_script())
        wrapper.bind("<Enter>", _hover_enter)
        wrapper.bind("<Leave>", _hover_leave)
        
        plus_button = ttk.Label(wrapper, image=self.images.get("plus"), style="primary")
        plus_button.configure(background=self.root.style.colors.get("primary"))
        plus_button.pack(side=ttk.LEFT, padx=15, pady=14)
        plus_button.bind("<Button-1>", lambda e: self._create_script())
        plus_button.bind("<Enter>", _hover_enter)
        plus_button.bind("<Leave>", _hover_leave)
        
        return wrapper

    def _draw_header(self, parent):
        header = ttk.Frame(parent)
        
        search_bar = self._draw_search_bar(header)
        search_bar.grid(row=0, column=0, sticky=ttk.EW, padx=(0, 5))
        
        open_folder_button = self._draw_open_folder_button(header)
        open_folder_button.grid(row=0, column=1, sticky=ttk.E)
        
        plus_button = self._draw_plus_button(header)
        plus_button.grid(row=0, column=2, sticky=ttk.E, padx=(5, 0))
        
        header.grid_columnconfigure(0, weight=1)
        
        return header
    
    def _draw_script_frame(self, parent, script):
        script = script.split(".")[0] + ".py"

        frame = RoundedFrame(parent, radius=(15, 15, 15, 15), bootstyle="dark.TFrame")
        inner_wrapper = ttk.Frame(frame, style="dark.TFrame")
        inner_wrapper.pack(fill=ttk.BOTH, padx=(15, 10), pady=10)

        script_name = ttk.Label(inner_wrapper, text=script, font=("Host Grotesk", 14 if sys.platform != "darwin" else 16, "bold"))
        script_name.configure(background=self.root.style.colors.get("dark"))
        script_name.grid(row=0, column=0, sticky=ttk.W)
        inner_wrapper.columnconfigure(0, weight=1)

        button_wrapper = ttk.Frame(inner_wrapper, style="dark.TFrame", width=60, height=20)
        button_wrapper.grid(row=0, column=1, sticky=ttk.E)

        self.hover_images = {}
        buttons = {
            "editor": {
                "image_key": "file-signature",
                "hover_colour": "#c8c8c8",
                "command": lambda: self._open_editor(script),
                "relx": 0.3,
            },
            "delete": {
                "image_key": "trash-white",
                "hover_colour": "#ff6464",
                "command": lambda: self._delete_script(script),
                "relx": 0.7,
            },
        }

        def on_hover(event, btn_key, canvas_item, canvas):
            if event.type == "7":  # Enter
                canvas.itemconfig(canvas_item, image=self.hover_images[btn_key])
            elif event.type == "8":  # Leave
                canvas.itemconfig(canvas_item, image=self.images.get(buttons[btn_key]["image_key"]))

        for key, data in buttons.items():
            canvas = ttk.Canvas(button_wrapper, width=15, height=15, highlightthickness=0, bg=self.root.style.colors.get("dark"))
            canvas.place(relx=data["relx"], rely=0.5, anchor="center")

            normal_img = self.images.get(data["image_key"])
            hover_img = self.images.get(data["image_key"], hover_colour=data["hover_colour"])

            self.hover_images[key] = hover_img

            canvas_item = canvas.create_image(0, 0, anchor="nw", image=normal_img)
            canvas.bind("<Button-1>", lambda e, cmd=data["command"]: cmd())
            canvas.bind("<Enter>", lambda e, btn_key=key, item=canvas_item, cnv=canvas: on_hover(e, btn_key, item, cnv))
            canvas.bind("<Leave>", lambda e, btn_key=key, item=canvas_item, cnv=canvas: on_hover(e, btn_key, item, cnv))

        return frame
    
    def _draw_scripts(self, parent):
        scripts = self.cfg.get_scripts()
        self.scripts_wrapper = ScrolledFrame(parent, width=parent.winfo_width(), height=parent.winfo_height())
        self.scripts_wrapper.pack(fill=ttk.BOTH, expand=True)
        
        self.scripts_wrapper.hide_scrollbars()
        self.scripts_wrapper.enable_scrolling()
        
        for script in scripts:
            script_frame = self._draw_script_frame(self.scripts_wrapper, script)
            script_frame.pack(fill=ttk.X, pady=5)
            
            self.script_frames.append({
                "name": script,
                "frame": script_frame
            })
            
    def _draw_restart_warning(self, parent):
        wrapper = RoundedFrame(parent, radius=(15, 15, 15, 15), bootstyle="warning.TFrame")
        inner_wrapper = ttk.Frame(wrapper, style="warning.TFrame")
        inner_wrapper.pack(fill=ttk.BOTH, padx=15, pady=10, expand=True)
        
        warning_label = ttk.Label(inner_wrapper, text="A restart is required to apply changes!", font=("Host Grotesk", 14 if sys.platform != "darwin" else 16, "bold"), anchor="center")
        warning_label.configure(background=self.root.style.colors.get("warning"))
        warning_label.pack(fill=ttk.BOTH, expand=True)
        
        return wrapper
    
    def draw(self, parent):
        self.restart_warning = self._draw_restart_warning(parent)
        self.restart_warning.pack(fill=ttk.X, side=ttk.TOP, pady=(10, 0))
        self.restart_warning.pack_forget()
        
        title = ttk.Label(parent, text="Scripts", font=("Host Grotesk", 20 if sys.platform != "darwin" else 24, "bold"))
        title.configure(background=self.root.style.colors.get("bg"))
        title.pack(pady=(0, 15), anchor=ttk.W)
        # title.grid(row=0, column=0, sticky=ttk.W, pady=(0, 15))
        
        header = self._draw_header(parent)
        header.pack(fill=ttk.X)
        
        ttk.Separator(parent, orient="horizontal").pack(fill=ttk.X, pady=(20, 16), padx=4)
        
        self._draw_scripts(parent)
        self._listen_to_directory()
        self._new_scripts_listener()