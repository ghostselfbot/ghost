import os
import shutil
import sys
import ctypes
import subprocess

from utils.files import resource_path
from ctypes import wintypes

# FONTS = [
#     resource_path("data/fonts/Roboto-Regular.ttf"),
#     resource_path("data/fonts/Roboto-Bold.ttf"),
#     resource_path("data/fonts/Roboto-LightItalic.ttf")
# ]

FONTS = [resource_path(f"data/fonts/{path}") for path in os.listdir(resource_path("data/fonts")) if path.endswith(".ttf")
         and not path.startswith(".")
         and not path.startswith("_")
         and not path.startswith("~")
         and not path.startswith("#")
         and not path.startswith("._")]

SYSTEM_FONT_DIR = {
    "darwin": os.path.expanduser("~/Library/Fonts"),
    "win32": os.path.expandvars("%WINDIR%\\Fonts"),
    "linux": "/usr/share/fonts",
}

if sys.platform == "win32":
    try:
        import winreg
    except ImportError:
        import _winreg as winreg

    user32 = ctypes.WinDLL('user32', use_last_error=True)
    gdi32 = ctypes.WinDLL('gdi32', use_last_error=True)

    FONTS_REG_PATH = r'Software\Microsoft\Windows NT\CurrentVersion\Fonts'

    HWND_BROADCAST   = 0xFFFF
    SMTO_ABORTIFHUNG = 0x0002
    WM_FONTCHANGE    = 0x001D
    GFRI_DESCRIPTION = 1
    GFRI_ISTRUETYPE  = 3

    if not hasattr(wintypes, 'LPDWORD'):
        wintypes.LPDWORD = ctypes.POINTER(wintypes.DWORD)

    user32.SendMessageTimeoutW.restype = wintypes.LPVOID
    user32.SendMessageTimeoutW.argtypes = (
        wintypes.HWND,   # hWnd
        wintypes.UINT,   # Msg
        wintypes.LPVOID, # wParam
        wintypes.LPVOID, # lParam
        wintypes.UINT,   # fuFlags
        wintypes.UINT,   # uTimeout
        wintypes.LPVOID) # lpdwResult

    gdi32.AddFontResourceW.argtypes = (
        wintypes.LPCWSTR,) # lpszFilename

    # http://www.undocprint.org/winspool/getfontresourceinfo
    gdi32.GetFontResourceInfoW.argtypes = (
        wintypes.LPCWSTR, # lpszFilename
        wintypes.LPDWORD, # cbBuffer
        wintypes.LPVOID,  # lpBuffer
        wintypes.DWORD)   # dwQueryType

def get_fonts():
    font_files = [os.path.basename(font) for font in FONTS]
    
    # sort them by first letter
    font_files.sort()
    
    return font_files

def already_installed(font_path):
    """
    Checks if the font is already installed on the system.
    """
    font_name = os.path.basename(font_path)
    system_platform = sys.platform

    # Check if the font exists in the system font directories
    if system_platform == "darwin":
        font_dir = os.path.expanduser("~/Library/Fonts")
    elif system_platform == "win32":
        font_dir = "C:\\Windows\\Fonts"
        
        # Check if the font is in the registry
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, FONTS_REG_PATH) as key:
            try:
                winreg.QueryValueEx(key, font_name)
                return True
            except FileNotFoundError:
                pass
        
    elif system_platform == "linux":
        font_dir = "/usr/share/fonts"
    else:
        return False  # Unsupported platform
    
    # Check if the font file is present in the system font directory
    font_installed = os.path.join(font_dir, font_name)
    return os.path.exists(font_installed)

def check_fonts():
    installed = []
    
    for font in FONTS:
        if already_installed(font):
            installed.append(font)
            
    return len(installed) == len(FONTS)

def load_custom_font(font_path):
    """
    Load the font into the system if not already installed.
    """
    if already_installed(font_path):
        print(f"Font already installed: {font_path}")
        return
    
    font_name = os.path.basename(font_path)
    system_platform = sys.platform

    # Define where to install the font based on the platform
    if system_platform == "darwin":
        install_dir = os.path.expanduser("~/Library/Fonts")
    elif system_platform == "win32":
        # copy the font to the Windows Fonts folder
        dst_path = os.path.join(os.environ['SystemRoot'], 'Fonts',
                                os.path.basename(font_path))
        shutil.copy(font_path, dst_path)
        # load the font in the current session
        if not gdi32.AddFontResourceW(dst_path):
            os.remove(dst_path)
            raise OSError('AddFontResource failed to load "%s"' % font_path)
        # notify running programs
        user32.SendMessageTimeoutW(HWND_BROADCAST, WM_FONTCHANGE, 0, 0,
                                SMTO_ABORTIFHUNG, 1000, None)
        # store the fontname/filename in the registry
        filename = os.path.basename(dst_path)
        fontname = os.path.splitext(filename)[0]
        # try to get the font's real name
        cb = wintypes.DWORD()
        if gdi32.GetFontResourceInfoW(filename, ctypes.byref(cb), None,
                                    GFRI_DESCRIPTION):
            buf = (ctypes.c_wchar * cb.value)()
            if gdi32.GetFontResourceInfoW(filename, ctypes.byref(cb), buf,
                                        GFRI_DESCRIPTION):
                fontname = buf.value
        is_truetype = wintypes.BOOL()
        cb.value = ctypes.sizeof(is_truetype)
        gdi32.GetFontResourceInfoW(filename, ctypes.byref(cb),
            ctypes.byref(is_truetype), GFRI_ISTRUETYPE)
        if is_truetype:
            fontname += ' (TrueType)'
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, FONTS_REG_PATH, 0,
                            winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, fontname, 0, winreg.REG_SZ, filename)
        
    elif system_platform == "linux":
        install_dir = "/usr/share/fonts"
    else:
        print(f"Unsupported platform: {system_platform}")
        return
    
    if system_platform != "win32":
        shutil.copy(font_path, os.path.join(install_dir, font_name))
    
    print(f"Font installed: {font_path}")

def load_fonts():
    """
    Loads all fonts into the system.
    """
    for font in FONTS:
        if not os.path.exists(font):
            print(f"Warning: Font file '{font}' not found.")
            continue
        
        try:
            load_custom_font(font)
        except Exception as e:
            print(f"Failed to load font '{font}': {e}")

def uninstall_fonts():
    """
    Removes all fonts from the system after app is finished.
    """
    for font in FONTS:
        font_name = os.path.basename(font)
        system_platform = sys.platform

        # Uninstall fonts based on platform
        if system_platform == "darwin":
            font_dir = os.path.expanduser("~/Library/Fonts")
            font_path = os.path.join(font_dir, font_name)
            if os.path.exists(font_path):
                os.remove(font_path)
                print(f"Uninstalled font: {font_name}")
                # Run the AppleScript to remove the font from Font Book (macOS)
                uninstall_mac_font(font_name)
        elif system_platform == "win32":
            font_dir = os.path.expandvars("%WINDIR%\\Fonts")
            font_path = os.path.join(font_dir, font_name)
            if os.path.exists(font_path):
                os.remove(font_path)
                print(f"Uninstalled font: {font_name}")
        elif system_platform == "linux":
            font_dir = "/usr/share/fonts"
            font_path = os.path.join(font_dir, font_name)
            if os.path.exists(font_path):
                os.remove(font_path)
                print(f"Uninstalled font: {font_name}")
        else:
            print(f"Unsupported platform: {system_platform}")

def uninstall_mac_font(font_name):
    """
    Uses AppleScript to remove the font from Font Book on macOS.
    """
    script = f'''
    tell application "Font Book"
        set theFont to (first font whose name is "{font_name}")
        remove theFont
    end tell
    '''
    
    try:
        subprocess.run(['osascript', '-e', script], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
        print(f"Font '{font_name}' removed from Font Book.")
    except subprocess.CalledProcessError:
        print(f"Failed to remove font '{font_name}' from Font Book.")
