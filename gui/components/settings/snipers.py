import ttkbootstrap as ttk
import utils.console as console
from gui.components import SettingsPanel, RoundedFrame

class SnipersPanel(SettingsPanel):
    def __init__(self, root, parent, images, config, width=None):
        super().__init__(root, parent, "Snipers", images.get("snipers"), width=width, collapsed=False)
        self.cfg = config
        self.images = images
        self.snipers = None
        self.snipers_tk_entries = {}
        self.placeholder = "Paste webhook URL here..."
        
    def _save_sniper(self, sniper_name):
        sniper = self.cfg.get_sniper(sniper_name)
        
        if not sniper:
            return
        
        sniper.enabled = self.snipers_tk_entries[sniper_name]["enabled"].get()
        sniper.ignore_invalid = self.snipers_tk_entries[sniper_name]["ignore_invalid"].get()
        
        value = self.snipers_tk_entries[sniper_name]["webhook"].get()
        sniper.webhook = "" if value == self.placeholder else value
        
        sniper.save(notify=False)
        
    def _draw_card(self, sniper):
        card = RoundedFrame(self.wrapper, radius=(10, 10, 10, 10), bootstyle="dark.TFrame")
        self.snipers_tk_entries[sniper.name] = {}

        header = ttk.Frame(card, style="dark.TFrame")
        header.grid(row=0, column=0, sticky=ttk.NSEW, pady=(10, 10), padx=10)

        title = ttk.Label(header, text=sniper.name.capitalize() + " Sniper", font=("Host Grotesk", 18, "bold"))
        title.configure(background=self.root.style.colors.get("dark"))
        title.grid(row=0, column=0, sticky=ttk.NSEW)

        entries = [
            {
                "label": "Enable sniper",
                "type": "checkbox",
                "value": sniper.enabled,
                "config_key": "enabled"
            },
            {
                "label": "Ignore invalid codes",
                "type": "checkbox",
                "value": sniper.ignore_invalid,
                "config_key": "ignore_invalid"
            },
            {
                "label": "Webhook",
                "type": "entry",
                "value": sniper.webhook,
                "config_key": "webhook"
            }
        ]

        for i, entry in enumerate(entries):
            if entry["type"] == "checkbox":
                checkbox_wrapper = RoundedFrame(card, radius=8, bootstyle="secondary.TFrame")
                checkbox_wrapper.grid(row=i + 1, column=0, sticky=ttk.NSEW, padx=10, pady=(0, 5))

                label = ttk.Label(checkbox_wrapper, text=" " + entry["label"])
                label.configure(background=self.root.style.colors.get("secondary"))
                label.grid(row=0, column=0, sticky=ttk.W, pady=10, padx=(8, 0))

                var = ttk.BooleanVar(value=entry["value"])
                
                checkbox = ttk.Checkbutton(
                    checkbox_wrapper,
                    style="success-round-toggle",
                    variable=var,
                    command=lambda sniper_name=sniper.name: self._save_sniper(sniper_name),
                    tristatevalue=None
                )
                checkbox.grid(row=0, column=1, sticky=ttk.E, pady=10, padx=(0, 10))
                checkbox_wrapper.grid_columnconfigure(0, weight=1)

                self.snipers_tk_entries[sniper.name][entry["config_key"]] = var
                
                def toggle_checkbox(event, var_obj=var, sniper_name=sniper.name):
                    var_obj.set(not var_obj.get())
                    self._save_sniper(sniper_name)

                label.bind("<Button-1>", toggle_checkbox)
                checkbox_wrapper.bind("<Button-1>", toggle_checkbox)
                
            else:
                wrapper = RoundedFrame(card, radius=8, bootstyle="dark.TFrame")
                wrapper.grid(row=i + 1, column=0, sticky=ttk.NSEW, padx=10, pady=(10, 10))

                label = ttk.Label(wrapper, text=entry["label"])
                label.configure(background=self.root.style.colors.get("dark"))
                label.grid(row=0, column=0, sticky=ttk.W, pady=(0, 5))

                textbox = ttk.Entry(wrapper, font=("Host Grotesk",))
                textbox.grid(row=1, column=0, sticky=ttk.EW)
                wrapper.grid_columnconfigure(0, weight=1)

                placeholder_color = "#6c757d"  # subtle grey
                normal_color = self.root.style.colors.get("fg")

                def set_placeholder(entry_widget):
                    entry_widget.delete(0, ttk.END)
                    entry_widget.insert(0, self.placeholder)
                    entry_widget.configure(foreground=placeholder_color)

                def clear_placeholder(entry_widget):
                    if entry_widget.get() == self.placeholder:
                        entry_widget.delete(0, ttk.END)
                        entry_widget.configure(foreground=normal_color)

                def on_focus_in(event, entry_widget=textbox):
                    clear_placeholder(entry_widget)

                def on_focus_out(event, entry_widget=textbox, sniper_name=sniper.name):
                    if not entry_widget.get():
                        set_placeholder(entry_widget)
                    self._save_sniper(sniper_name)

                # Initial state
                if entry["value"]:
                    textbox.insert(0, entry["value"])
                    textbox.configure(foreground=normal_color)
                else:
                    set_placeholder(textbox)

                textbox.bind("<FocusIn>", on_focus_in)
                textbox.bind("<FocusOut>", on_focus_out)
                textbox.bind("<Return>", lambda e, sniper_name=sniper.name: self._save_sniper(sniper_name))

                self.snipers_tk_entries[sniper.name][entry["config_key"]] = textbox

        card.grid_rowconfigure(i + 2, weight=1)
        card.grid_columnconfigure(0, weight=1)

        return card
        
    def draw(self):
        self.body.grid_remove()
        self.snipers = self.cfg.get_snipers()
        
        if not self.snipers:
            console.log_to_gui("error", "No snipers found.")
            return
        
        row = 0
        
        for sniper in self.snipers:
            card = self._draw_card(sniper)
            card.grid(row=row, column=0, sticky=ttk.NSEW, padx=0, pady=(0, 10))
            
            row += 1
        
        return self.wrapper
        