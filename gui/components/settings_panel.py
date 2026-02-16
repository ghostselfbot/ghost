import ttkbootstrap as ttk
from gui.components import SettingsFrame

class SettingsPanel:
    def __init__(self, root, parent, title, icon, collapsible=False, collapsed=False, width=None):
        self.root = root
        self.parent = parent
        self.title = title
        self.icon = icon
        self.collapsible = collapsible
        self.collapsed = collapsed
        self.width = width
        # Create the body and wrapper upfront
        self.body, self.wrapper = self._create_body_and_wrapper()
        self.root.bind("<Button-1>", self._remove_focus)

    def _create_body_and_wrapper(self):
        # You can use your existing logic for creating the body and wrapper
        body, wrapper = SettingsFrame(self.parent, self.title, self.icon, collapsible=self.collapsible, collapsed=self.collapsed, width=self.width).draw()
        return body, wrapper

    def _remove_focus(self, event):
        widget = event.widget
        if isinstance(widget, ttk.Entry):  # Ignore if clicking an entry field
            return
        self.root.focus_set()  # Set focus to the main window

    def draw(self):
        raise NotImplementedError("Each panel must implement the draw method")

    def save(self):
        raise NotImplementedError("Each panel must implement the save method")
