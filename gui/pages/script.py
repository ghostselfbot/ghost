import sys
import ttkbootstrap as ttk

from utils.files import get_application_support
from gui.helpers.images import Images
from gui.components.rounded_frame import RoundedFrame
from cupcake import Editor, Languages

class ScriptPage:
    def __init__(self, root, script):
        self.gui = root
        self.root = root.root
        self.script = script
        self.images = Images()
        self.editor = None
        self.linenumbers = None
        self.text_scrollbar = None
        
    def _go_back(self):
        self._save_script()
        self.gui.draw_scripts()
        
    def _get_script_content(self):
        with open(get_application_support() + f"/scripts/{self.script}", "r") as file:
            return file.read()
        
    def _save_script(self):
        # with open(get_application_support() + f"/scripts/{self.script}", "w") as file:
        #     file.write(self.editor.content.get("1.0", ttk.END))
        self.editor.save()

    def _draw_header(self, parent):
        wrapper = ttk.Frame(parent)
        
        back_button = ttk.Label(wrapper, image=self.images.get("left-chevron"))
        back_button.grid(row=0, column=0, sticky=ttk.W, padx=(0, 10))
        back_button.bind("<Button-1>", lambda e: self._go_back())
            
        script_name = ttk.Label(wrapper, text=self.script, font=("Host Grotesk", 16, "bold"))
        script_name.grid(row=0, column=1, sticky=ttk.W)
        
        return wrapper

    def draw(self, parent):
        header = self._draw_header(parent)
        header.pack(fill=ttk.X, pady=(0, 20))
        
        editor_wrapper = RoundedFrame(parent, radius=(15, 15, 15, 15), bootstyle="dark.TFrame")
        editor_wrapper.pack(fill=ttk.BOTH, expand=True)

        self.editor = Editor(
            editor_wrapper, 
            language=Languages.PYTHON, 
            darkmode=True, 
            font=("JetBrainsMono NF Regular", 10 if sys.platform != "darwin" else 12),
            path=get_application_support() + f"/scripts/{self.script}",
            showpath=False
        )
        self.editor.pack(fill=ttk.BOTH, expand=True)
        content = self.editor.content
        content.insert("end", self._get_script_content())