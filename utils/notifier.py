import subprocess
import sys

class Notifier:
    def __init__(self) -> None:
        pass

    @staticmethod
    def send(title: str, text :str) -> None:
        if sys.platform == "win32":
            # TODO: add notifs for windows
            pass
        elif sys.platform == "linux":
            subprocess.Popen(["notify-send", title, text])
        elif sys.platform == "darwin":
            cmd = '''on run argv
  display notification (item 2 of argv) with title (item 1 of argv)
end run'''
            subprocess.call(['osascript', '-e', cmd, title, text])