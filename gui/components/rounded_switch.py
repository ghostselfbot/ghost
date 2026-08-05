import ttkbootstrap as ttk
from PIL import Image, ImageDraw, ImageTk

from gui.components.rounded_frame import RoundedFrame
from gui.helpers.style import Style

class RoundedSwitch(ttk.Canvas):
    def __init__(self, parent, variable=None, command=None, parent_background=None, **kwargs):
        self.parent = parent
        self.root = parent.winfo_toplevel()
        self.style = self.root.style
        self.variable = variable or ttk.BooleanVar(value=False)
        self.command = command
        self.parent_background = parent_background or self._get_parent_background()
        self.on_color = kwargs.pop("on_color", self.style.colors.get("primary"))
        self.off_color = kwargs.pop("off_color", Style.ENTRY_BG.value)
        self.thumb_color = kwargs.pop("thumb_color", "#ffffff")
        self.disabled_color = kwargs.pop("disabled_color", self.style.colors.get("dark"))
        self.scale = float(kwargs.pop("scale", 1.15))
        if self.scale <= 0:
            raise ValueError("scale must be greater than zero")
        self._base_width = kwargs.pop("width", 28)
        self._base_height = kwargs.pop("height", 16)
        self._disabled = False

        canvas_kwargs = {
            key: value
            for key, value in kwargs.items()
            if key not in {"text", "bootstyle", "style", "padx", "pady", "background", "foreground"}
        }
        canvas_kwargs["width"] = round(self._base_width * self.scale)
        canvas_kwargs["height"] = round(self._base_height * self.scale)
        super().__init__(parent, highlightthickness=0, bd=0, **canvas_kwargs)
        super().configure(background=self.parent_background)
        self.variable.trace_add("write", self._draw)
        self.bind("<Configure>", self._draw)
        self.bind("<Button-1>", self.invoke)

    def _get_parent_background(self):
        if isinstance(self.parent, RoundedFrame):
            return self.parent.frame_background
        try:
            style_name = self.parent.cget("style")
            return self.style.lookup(style_name, "background") or self.style.colors.get("bg")
        except Exception:
            return self.style.colors.get("bg")

    def _draw(self, *args):
        self.delete("all")
        width = self.winfo_width()
        height = self.winfo_height()
        if width < 2 or height < 2:
            return

        selected = bool(self.variable.get())
        color = self.disabled_color if self._disabled else (self.on_color if selected else self.off_color)
        supersample = 4
        image_size = (width * supersample, height * supersample)
        image = Image.new("RGBA", image_size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        track_radius = image_size[1] // 2
        draw.rounded_rectangle((0, 0, *image_size), radius=track_radius, fill=color)

        thumb_diameter = max(height - round(6 * self.scale), 2)
        thumb_x = width - (height / 2) if selected else height / 2
        thumb_radius = (thumb_diameter * supersample) / 2
        thumb_center_x = thumb_x * supersample
        thumb_center_y = (height / 2) * supersample
        draw.ellipse(
            (
                round(thumb_center_x - thumb_radius),
                round(thumb_center_y - thumb_radius),
                round(thumb_center_x + thumb_radius),
                round(thumb_center_y + thumb_radius),
            ),
            fill=self.thumb_color,
        )

        image = image.resize((width, height), Image.Resampling.LANCZOS)
        self._switch_image = ImageTk.PhotoImage(image)
        self.create_image(0, 0, anchor="nw", image=self._switch_image)

    def invoke(self, event=None):
        if self._disabled:
            return
        self.variable.set(not bool(self.variable.get()))
        if self.command:
            self.command()

    def state(self, states=None):
        if states is None:
            return ("disabled",) if self._disabled else (("selected",) if self.variable.get() else ())

        for state in states:
            if state == "disabled":
                self._disabled = True
            elif state == "!disabled":
                self._disabled = False
            elif state == "selected":
                self.variable.set(True)
            elif state == "!selected":
                self.variable.set(False)
        self._draw()

    def instate(self, states):
        state_set = set(states)
        return (
            ("selected" not in state_set or bool(self.variable.get()))
            and ("!selected" not in state_set or not bool(self.variable.get()))
            and ("disabled" not in state_set or self._disabled)
            and ("!disabled" not in state_set or not self._disabled)
        )

    def configure(self, cnf=None, **kwargs):
        options = dict(cnf or {})
        options.update(kwargs)
        if "variable" in options:
            self.variable = options.pop("variable")
            self.variable.trace_add("write", self._draw)
        if "command" in options:
            self.command = options.pop("command")
        if "parent_background" in options:
            self.set_parent_background(options.pop("parent_background"))
        if "scale" in options:
            self.set_scale(options.pop("scale"))
        return super().configure(options) if options else None

    config = configure

    def set_parent_background(self, parent_background):
        self.parent_background = parent_background
        super().configure(background=parent_background)
        self._draw()

    def set_scale(self, scale):
        scale = float(scale)
        if scale <= 0:
            raise ValueError("scale must be greater than zero")
        self.scale = scale
        super().configure(
            width=round(self._base_width * scale),
            height=round(self._base_height * scale),
        )
        self._draw()