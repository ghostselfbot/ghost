import sys
import string
import random
import ttkbootstrap as ttk
from gui.components import RoundedFrame, ToolPage, RoundedButton
from gui.helpers import Style

class PasswordGenPage(ToolPage):
    def __init__(self, toolspage, root, bot_controller, images, layout):
        super().__init__(toolspage, root, bot_controller, images, layout, title="Password Generator", frame=None)
        self.generated_password = None
        self.password_length = 12
        self.include_uppercase = True
        self.include_lowercase = True
        self.include_numbers = False
        self.include_symbols = True
    
    def copy_to_clipboard(self):
        if self.generated_password:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.generated_password.get())
            self.root.update()  # Now it stays on the clipboard after the window is closed
            # set generated password text to "Copied!" for 1.5 seconds
            original_text = self.generated_password.get()
            self.generated_password.configure(state="normal")
            self.generated_password.delete(0, ttk.END)
            self.generated_password.insert(0, "Copied!")
            self.generated_password.configure(state="readonly")
            self.root.after(1500, lambda: self.generated_password.configure(state="normal") or self.generated_password.delete(0, ttk.END) or self.generated_password.insert(0, original_text) or self.generated_password.configure(state="readonly"))
        
    def draw_password_field(self, parent):
        entry_wrapper = RoundedFrame(parent, radius=(15, 15, 15, 15), bootstyle="dark.TFrame")
        entry_wrapper.pack(fill=ttk.BOTH, pady=(0, 10))
        
        self.generated_password = ttk.Entry(entry_wrapper, bootstyle="dark.TFrame", font=("Host Grotesk", 12 if sys.platform != "darwin" else 13))
        self.generated_password.grid(row=0, column=0, sticky=ttk.EW, padx=(18, 0), pady=10, columnspan=2, ipady=10)
        self.generated_password.insert(0, "Click 'Generate' to create a password")
        self.generated_password.configure(state="readonly")
        
        copy_button = ttk.Label(entry_wrapper, image=self.images.get("copy"), style="dark.TButton")
        copy_button.grid(row=0, column=2, sticky=ttk.E, padx=(0, 0), pady=10)
        copy_button.bind("<Button-1>", lambda e: self.copy_to_clipboard())
        
        reset_button = ttk.Label(entry_wrapper, image=self.images.get("reset"), style="dark.TButton")
        reset_button.grid(row=0, column=3, sticky=ttk.E, padx=(0, 10), pady=10)
        reset_button.bind("<Button-1>", lambda e: self.generate_password())
        
        entry_wrapper.columnconfigure(1, weight=1)
        
    def generate_password(self):
        character_pool = ""
        if self.include_uppercase:
            character_pool += string.ascii_uppercase
        if self.include_lowercase:
            character_pool += string.ascii_lowercase
        if self.include_numbers:
            character_pool += string.digits
        if self.include_symbols:
            character_pool += string.punctuation
            
        if not character_pool:
            return  # No character types selected
        
        password = ''.join(random.choice(character_pool) for _ in range(self.password_length))
        self.generated_password.configure(state="normal")
        self.generated_password.delete(0, ttk.END)
        self.generated_password.insert(0, password)
        self.generated_password.configure(state="readonly")
        
    def update_password_length(self, value):
        self.password_length = int(float(value))
        self.length_label.configure(text=f"Password Length {self.password_length}")
            
    def on_slider_release(self, event):
        self.on_option_change()
            
    def update_strength(self):
        length = self.password_length

        if length <= 4:
            value = 10
            label = "Very Weak"
            style = "danger"
        elif length <= 6:
            value = 30
            label = "Weak"
            style = "danger"
        elif length <= 10:
            value = 50
            label = "Medium"
            style = "warning"
        elif length <= 14:
            value = 80
            label = "Strong"
            style = "success"
        else:
            value = 100
            label = "Very Strong"
            style = "success"

        self.strength_bar.configure(value=value, bootstyle=style)
        self.strength_label.configure(text=label)
            
    def on_option_change(self, *args):
        # sync vars → internal state
        try:
            self.include_uppercase = self.uppercase_var.get()
            self.include_lowercase = self.lowercase_var.get()
            self.include_numbers = self.numbers_var.get()
            self.include_symbols = self.symbols_var.get()
        except AttributeError:
            pass  # vars not initialized yet

        # regenerate + update strength
        self.generate_password()
        self.update_strength()
        
    def draw_options(self, parent):
        options_wrapper = RoundedFrame(parent, radius=(15, 15, 15, 15), bootstyle="dark.TFrame")
        options_wrapper.pack(fill=ttk.BOTH)
        options_wrapper.columnconfigure(1, weight=1)
        
        # password strength
        strength_wrapper = ttk.Frame(options_wrapper, bootstyle="dark.TFrame")
        strength_wrapper.grid(row=0, column=0, sticky=ttk.EW, padx=18, pady=(15, 5), columnspan=2)
        strength_wrapper.columnconfigure(0, weight=1)
        
        self.strength_label = ttk.Label(strength_wrapper, text="Strong", font=("Host Grotesk", 12), background=self.root.style.colors.get("dark"))
        self.strength_label.grid(row=0, column=1, sticky=ttk.W, padx=(15, 0))
        self.strength_bar = ttk.Progressbar(strength_wrapper, bootstyle="success", maximum=100, value=80)
        self.strength_bar.grid(row=0, column=0, sticky=ttk.EW)
        
        # password length
        self.length_label = ttk.Label(options_wrapper, text=f"Password Length {self.password_length}", font=("Host Grotesk", 12), background=self.root.style.colors.get("dark"))
        self.length_label.grid(row=1, column=0, sticky=ttk.W, padx=18, pady=(5, 5))
        length_slider = ttk.Scale(options_wrapper, from_=4, to=48, orient=ttk.HORIZONTAL, command=self.update_password_length)
        length_slider.bind("<ButtonRelease-1>", self.on_slider_release)
        length_slider.set(self.password_length)
        length_slider.grid(row=1, column=1, sticky=ttk.EW, padx=18, pady=(5, 5))
        
        # uppercase, lowercase, numbers, symbols
        self.uppercase_var = ttk.BooleanVar(value=self.include_uppercase)
        self.uppercase_var.trace_add("write", self.on_option_change)
        uppercase_label = ttk.Label(options_wrapper, text="Include Uppercase Letters", font=("Host Grotesk", 12), background=self.root.style.colors.get("dark"))
        uppercase_label.grid(row=2, column=0, sticky=ttk.W, padx=(18, 0), pady=(5, 5))
        uppercase_check = ttk.Checkbutton(options_wrapper, variable=self.uppercase_var, bootstyle="success-round-toggle", command=self.on_option_change)
        uppercase_check.grid(row=2, column=1, sticky=ttk.E, padx=18, pady=(5, 5))
        
        self.lowercase_var = ttk.BooleanVar(value=self.include_lowercase)
        self.lowercase_var.trace_add("write", self.on_option_change)
        lowercase_label = ttk.Label(options_wrapper, text="Include Lowercase Letters", font=("Host Grotesk", 12), background=self.root.style.colors.get("dark"))
        lowercase_label.grid(row=3, column=0, sticky=ttk.W, padx=(18, 0), pady=(5, 5))
        lowercase_check = ttk.Checkbutton(options_wrapper, variable=self.lowercase_var, bootstyle="success-round-toggle", command=self.on_option_change)
        lowercase_check.grid(row=3, column=1, sticky=ttk.E, padx=18, pady=(5, 5))
        
        self.numbers_var = ttk.BooleanVar(value=self.include_numbers)
        self.numbers_var.trace_add("write", self.on_option_change)
        numbers_label = ttk.Label(options_wrapper, text="Include Numbers", font=("Host Grotesk", 12), background=self.root.style.colors.get("dark"))
        numbers_label.grid(row=4, column=0, sticky=ttk.W, padx=(18, 0), pady=(5, 5))
        numbers_check = ttk.Checkbutton(options_wrapper, variable=self.numbers_var, bootstyle="success-round-toggle", command=self.on_option_change)
        numbers_check.grid(row=4, column=1, sticky=ttk.E, padx=18, pady=(5, 5))
        
        self.symbols_var = ttk.BooleanVar(value=self.include_symbols)
        self.symbols_var.trace_add("write", self.on_option_change)
        symbols_label = ttk.Label(options_wrapper, text="Include Symbols", font=("Host Grotesk", 12), background=self.root.style.colors.get("dark"))
        symbols_label.grid(row=5, column=0, sticky=ttk.W, padx=(18, 0), pady=(5, 15))
        symbols_check = ttk.Checkbutton(options_wrapper, variable=self.symbols_var, bootstyle="success-round-toggle", command=self.on_option_change)
        symbols_check.grid(row=5, column=1, sticky=ttk.E, padx=18, pady=(5, 15))
        
        # generate_button = RoundedButton(options_wrapper, text="Generate", bootstyle="success.TButton", command=self.generate_password)
        # generate_button.grid(row=6, column=1, columnspan=2, pady=(0, 15), padx=18, sticky=ttk.E)
        
    def draw_content(self, wrapper):
        self.draw_password_field(wrapper)
        self.draw_options(wrapper)
        self.generate_password()
        self.update_strength()