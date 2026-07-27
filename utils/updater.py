import os
from dataclasses import dataclass
import shlex
import subprocess
import sys
import tempfile
import zipfile

import requests

from utils import VERSION, console, REPO, files

MACOS = "https://github.com/ghostselfbot/ghost/releases/latest/download/Ghost-Mac.zip"
WINDOWS = "https://github.com/ghostselfbot/ghost/releases/latest/download/Ghost-Windows.zip"


def _compare_url(current_version, latest_version):
    return f"{REPO}/compare/{_normalize_release_tag(current_version)}...{_normalize_release_tag(latest_version)}"


@dataclass
class UpdateInfo:
    current_version: str
    latest_version: str
    changelog: str = ""

    @property
    def full_changelog_url(self):
        return _compare_url(self.current_version, self.latest_version)

    @property
    def has_update(self):
        return _should_update(self.current_version, self.latest_version)

    def install(self, progress_callback=None):
        return install_update(self, progress_callback=progress_callback)


def _normalize_version(version):
    version = str(version).strip()
    if version.startswith(("v", "V")):
        version = version[1:]

    base_version = version.split("-", 1)[0]
    parts = []
    for part in base_version.split("."):
        if part.isdigit():
            parts.append(int(part))
        else:
            break

    return tuple(parts)


def _should_update(current_version, latest_version):
    current_parts = _normalize_version(current_version)
    latest_parts = _normalize_version(latest_version)

    max_len = max(len(current_parts), len(latest_parts))
    current_parts += (0,) * (max_len - len(current_parts))
    latest_parts += (0,) * (max_len - len(latest_parts))

    return current_parts < latest_parts


def should_update():
    update_info = get_update_info()
    return bool(update_info and update_info.has_update)


def _release_api_url():
    return REPO.replace("https://github.com/", "https://api.github.com/repos/") + "/releases/latest"


def _normalize_release_tag(tag_name):
    tag_name = str(tag_name).strip()
    if tag_name.startswith(("v", "V")):
        return tag_name[1:]
    return tag_name


def _fetch_release_metadata():
    response = requests.get(_release_api_url(), timeout=5, headers={"Accept": "application/vnd.github+json"})
    response.raise_for_status()
    release_data = response.json()
    latest_version = _normalize_release_tag(release_data.get("tag_name", VERSION))
    changelog = _strip_admonitions(release_data.get("body", "") or "")
    return latest_version, changelog


def _strip_admonitions(changelog):
    cleaned_lines = []

    for line in changelog.splitlines():
        line = line.replace("[!NOTE]", "NOTE")
        line = line.replace("[!WARNING]", "WARNING")
        cleaned_lines.append(line)

    return "\n".join(cleaned_lines).strip()


def get_update_info():
    try:
        latest_version, changelog = _fetch_release_metadata()
        if _should_update(VERSION, latest_version):
            return UpdateInfo(current_version=VERSION, latest_version=latest_version, changelog=changelog)

        return None
    except requests.exceptions.RequestException as exc:
        console.error(f"Failed to check for updates: {exc}")
        return None


def check_for_updates():
    update_info = get_update_info()
    if update_info:
        console.info(f"A new version is available: {update_info.latest_version}. You are currently on {update_info.current_version}.")
        return update_info

    console.success("You are using the latest version.")
    return None


def _get_update_url():
    if sys.platform == "darwin":
        return MACOS
    if sys.platform == "win32":
        return WINDOWS
    raise RuntimeError("Unsupported platform for automatic updates.")


def _find_executable(extract_dir):
    if sys.platform == "darwin":
        app_paths = []
        for root, dirs, _ in os.walk(extract_dir):
            for dirname in dirs:
                if dirname.lower().endswith(".app"):
                    app_paths.append(os.path.join(root, dirname))
        return app_paths[0] if app_paths else None

    if sys.platform == "win32":
        exe_paths = []
        for root, _, files in os.walk(extract_dir):
            for filename in files:
                if filename.lower().endswith(".exe"):
                    exe_paths.append(os.path.join(root, filename))
        return exe_paths[0] if exe_paths else None

    return None


def _prepare_macos_app(app_path):
    if sys.platform != "darwin":
        return

    subprocess.run(["xattr", "-cr", app_path], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["chmod", "-R", "u+rwX", app_path], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    macos_bin_dir = os.path.join(app_path, "Contents", "MacOS")
    if os.path.isdir(macos_bin_dir):
        for entry in os.listdir(macos_bin_dir):
            executable_file = os.path.join(macos_bin_dir, entry)
            subprocess.run(["chmod", "+x", executable_file], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def _extract_update_archive(archive_path, extract_dir):
    if sys.platform == "darwin":
        subprocess.run(["ditto", "-x", "-k", archive_path, extract_dir], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return

    with zipfile.ZipFile(archive_path, "r") as archive:
        archive.extractall(extract_dir)


def _current_install_path():
    if not getattr(sys, "frozen", False):
        return None

    if sys.platform == "darwin":
        return os.path.realpath(os.path.dirname(os.path.dirname(os.path.dirname(sys.executable))))

    if sys.platform == "win32":
        return os.path.realpath(sys.executable)

    return None


def _start_replacement_handoff(current_path, updated_path, update_dir):
    current_pid = str(os.getpid())

    if sys.platform == "darwin":
        script_path = os.path.join(update_dir, "install-update.sh")
        log_path = os.path.join(update_dir, "install-update.log")
        updated_executable = os.path.join(updated_path, "Contents", "MacOS", os.path.basename(sys.executable))
        current_executable = os.path.join(current_path, os.path.relpath(updated_executable, updated_path))
        script = "\n".join([
            "#!/bin/sh",
            f"exec >> {shlex.quote(log_path)} 2>&1",
            f"while kill -0 {current_pid} 2>/dev/null; do sleep 1; done",
            f"rm -rf {shlex.quote(current_path)}",
            f"mv {shlex.quote(updated_path)} {shlex.quote(current_path)}",
            "unset _PYI_APPLICATION_HOME_DIR _PYI_PARENT_PROCESS_LEVEL _PYI_SPLASH_IPC",
            "export PYINSTALLER_RESET_ENVIRONMENT=1",
            f"{shlex.quote(current_executable)} &",
            f"rm -rf {shlex.quote(update_dir)}",
            "exit 0",
        ])
        with open(script_path, "w", encoding="utf-8") as script_file:
            script_file.write(f"{script}\n")
        os.chmod(script_path, 0o700)
        subprocess.Popen(["/bin/sh", script_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return

    if sys.platform == "win32":
        script_path = os.path.join(update_dir, "install-update.cmd")
        powershell_update_dir = update_dir.replace("'", "''")
        script = "\r\n".join([
            "@echo off",
            f"powershell -NoProfile -Command \"Wait-Process -Id {current_pid} -ErrorAction SilentlyContinue\"",
            f"move /Y \"{updated_path}\" \"{current_path}\" >nul",
            f"start \"\" \"{current_path}\"",
            f"start \"\" /b powershell -NoProfile -WindowStyle Hidden -Command \"Start-Sleep -Seconds 2; Remove-Item -LiteralPath '{powershell_update_dir}' -Recurse -Force\"",
        ])
        with open(script_path, "w", encoding="utf-8") as script_file:
            script_file.write(f"{script}\r\n")
        subprocess.Popen(["cmd", "/c", script_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return

    raise RuntimeError("Unsupported platform for automatic updates.")


def install_update(update_info=None, progress_callback=None):
    def report(status, progress=None):
        if progress_callback:
            progress_callback(status, progress)

    try:
        url = _get_update_url()
    except RuntimeError as exc:
        console.error(f"{exc}")
        return False

    try:
        report("Downloading update", 0)
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        filename = os.path.basename(url)
        update_dir = os.path.join(files.get_application_support(), ".ghost-updates")
        os.makedirs(update_dir, exist_ok=True)
        archive_path = os.path.join(update_dir, filename)
        content_length = int(response.headers.get("content-length", 0))
        downloaded_bytes = 0
        if not content_length:
            report("Downloading update", None)

        with open(archive_path, "wb") as update_file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    update_file.write(chunk)
                    downloaded_bytes += len(chunk)
                    if content_length:
                        report("Downloading update", downloaded_bytes * 100 / content_length)

        console.info(f"Downloaded update archive: {filename}")

        report("Preparing update", None)
        extract_dir = tempfile.mkdtemp(prefix="ghost-update-", dir=update_dir)
        _extract_update_archive(archive_path, extract_dir)

        executable_path = _find_executable(extract_dir)
        if not executable_path:
            console.error("Could not find an executable inside the downloaded update archive.")
            return False

        current_path = _current_install_path()
        if not current_path:
            console.error("Automatic updates are only available from an installed Ghost application.")
            return False

        if sys.platform == "darwin" and executable_path.lower().endswith(".app"):
            report("Preparing application", None)
            _prepare_macos_app(executable_path)

        report("Restarting Ghost", None)
        _start_replacement_handoff(current_path, executable_path, update_dir)
        console.info(f"Installed update to {current_path}; restarting Ghost.")
        raise SystemExit(0)
    except requests.exceptions.RequestException as exc:
        console.error(f"Failed to download update: {exc}")
        return False
    except (OSError, zipfile.BadZipFile) as exc:
        console.error(f"Failed to install update: {exc}")
        return False


def download_update():
    return install_update()