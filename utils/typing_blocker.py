import os
import glob
import re

_FLAG_FILE = os.path.join(os.path.expanduser("~"), ".ghost_silent_typing")

_INJECTED_JS = r"""const _ghostFs = require('fs');
const _ghostPath = require('path');
const _ghostOs = require('os');
const _ghostFlagPath = _ghostPath.join(_ghostOs.homedir(), '.ghost_silent_typing');
const _ghostElectron = require('electron');

function _ghostInstallTypingBlock(ses) {
    ses.webRequest.onBeforeRequest({ urls: ['https://*.discord.com/*'] }, (details, callback) => {
        if (details.url.endsWith('/typing') && details.method === 'POST') {
            try {
                if (_ghostFs.existsSync(_ghostFlagPath)) {
                    callback({ cancel: true });
                    return;
                }
            } catch (e) {}
        }
        callback({});
    });
}

_ghostElectron.app.on('ready', () => {
    _ghostInstallTypingBlock(_ghostElectron.session.defaultSession);
});

_ghostElectron.app.on('browser-window-created', (e, w) => {
    if (w.webContents.session !== _ghostElectron.session.defaultSession) {
        _ghostInstallTypingBlock(w.webContents.session);
    }
});"""


import sys

def find_discord_index():
    app_dirs = []
    
    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA", "")
        if base:
            for c in ["Discord", "DiscordPTB", "DiscordCanary"]:
                app_dirs.extend(glob.glob(os.path.join(base, c, "app-*")))
    elif sys.platform == "darwin":
        base = os.path.join(os.path.expanduser("~"), "Library", "Application Support")
        for c in ["discord", "discordptb", "discordcanary"]:
            app_dirs.extend(glob.glob(os.path.join(base, c, "[0-9]*.[0-9]*.[0-9]*")))

    app_dirs.sort(reverse=True)

    for app_dir in app_dirs:
        if os.name == "nt":
            pattern = os.path.join(app_dir, "modules", "discord_desktop_core-*", "discord_desktop_core", "index.js")
        else:
            pattern = os.path.join(app_dir, "modules", "discord_desktop_core", "index.js")
            
        matches = glob.glob(pattern)
        if matches:
            return matches[0]
            
    return None


def is_injected(index_path=None):
    if index_path is None:
        index_path = find_discord_index()
    if index_path is None or not os.path.isfile(index_path):
        return False

    with open(index_path, "r", encoding="utf-8") as f:
        return _INJECTED_JS in f.read()


def inject(index_path=None):
    if index_path is None:
        index_path = find_discord_index()
    if index_path is None or not os.path.isfile(index_path):
        return False, "Discord installation not found"

    if is_injected(index_path):
        return True, ""

    with open(index_path, "r", encoding="utf-8") as f:
        original_content = f.read()

    new_content = _INJECTED_JS + "\n" + original_content

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    return True, ""


def uninject(index_path=None):
    if index_path is None:
        index_path = find_discord_index()
    if index_path is None or not os.path.isfile(index_path):
        return False, "Discord installation not found"

    if not is_injected(index_path):
        return True, ""

    with open(index_path, "r", encoding="utf-8") as f:
        content = f.read()

    cleaned = content.replace(_INJECTED_JS + "\n", "")

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(cleaned)

    return True, ""


def set_enabled(enabled):
    if enabled:
        with open(_FLAG_FILE, "w") as f:
            f.write("1")
    elif os.path.isfile(_FLAG_FILE):
        os.remove(_FLAG_FILE)


def is_enabled():
    return os.path.isfile(_FLAG_FILE)
