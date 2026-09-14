import base64
import threading
import time
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

import requests


class SpotifyLyricsService:
    redirect_uri = "http://127.0.0.1:8999/callback"
    auth_scopes = "user-read-currently-playing user-read-playback-state"

    def __init__(self, credentials, show_timestamp=True, show_label=True, status_callback=None):
        self.credentials = credentials
        self.show_timestamp = show_timestamp
        self.show_label = show_label
        self.status_callback = status_callback
        self.stop_event = threading.Event()
        self.thread = None
        self.spotify_token = None
        self.spotify_token_expires_at = 0
        self.session = requests.Session()

    def _set_status(self, message):
        if self.status_callback:
            self.status_callback(message)

    def start(self):
        if self.thread and self.thread.is_alive():
            return False

        self.stop_event.clear()
        self.thread = threading.Thread(target=self._run, name="spotify-lyrics", daemon=True)
        self.thread.start()
        return True

    def authenticate(self, callback=None):
        client_id = self.credentials.get("clientID", "").strip()
        if not client_id:
            raise ValueError("Spotify Client ID is required")

        auth_url = "https://accounts.spotify.com/authorize?" + urllib.parse.urlencode({
            "client_id": client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": self.auth_scopes,
        })

        service = self
        callback_result = callback or (lambda success, message: None)

        class CallbackHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
                if query.get("error"):
                    message = query["error"][0]
                    self._respond("Spotify authentication was cancelled.")
                    callback_result(False, message)
                    return

                code = query.get("code", [None])[0]
                if not code:
                    self._respond("Spotify authentication failed. You can close this window.")
                    callback_result(False, "Authorization code is missing")
                    return

                try:
                    service._exchange_code(code)
                    self._respond("Spotify authentication successful. You can close this window.")
                    callback_result(True, "Spotify authentication successful.")
                except (requests.RequestException, KeyError, ValueError) as error:
                    self._respond("Spotify authentication failed. You can close this window.")
                    callback_result(False, str(error))

            def log_message(self, format, *args):
                return

            def _respond(self, message):
                body = f"<html><body><h2>{message}</h2></body></html>".encode()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

        def wait_for_callback():
            try:
                server = HTTPServer(("127.0.0.1", 8999), CallbackHandler)
                server.handle_request()
                server.server_close()
            except OSError as error:
                callback_result(False, f"Could not start Spotify callback server: {error}")

        threading.Thread(target=wait_for_callback, name="spotify-oauth", daemon=True).start()
        webbrowser.open(auth_url)

    def _exchange_code(self, code):
        client_id = self.credentials.get("clientID", "").strip()
        client_secret = self.credentials.get("clientSecret", "").strip()
        if not client_id or not client_secret:
            raise ValueError("Spotify Client ID and client secret are required")

        response = self.session.post(
            "https://accounts.spotify.com/api/token",
            headers={
                "Authorization": "Basic " + base64.b64encode(f"{client_id}:{client_secret}".encode()).decode(),
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": self.redirect_uri,
            },
            timeout=15,
        )
        response.raise_for_status()
        payload = response.json()
        self.credentials["refreshToken"] = payload["refresh_token"]
        self.spotify_token = payload["access_token"]
        self.spotify_token_expires_at = time.time() + payload.get("expires_in", 3600) - 60

    def stop(self):
        self.stop_event.set()
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2)
        self.thread = None

    def _refresh_spotify_token(self):
        client_id = self.credentials.get("clientID", "").strip()
        client_secret = self.credentials.get("clientSecret", "").strip()
        refresh_token = self.credentials.get("refreshToken", "").strip()
        if not client_id or not client_secret or not refresh_token:
            raise ValueError("Spotify Client ID, client secret and refresh token are required")

        response = self.session.post(
            "https://accounts.spotify.com/api/token",
            auth=requests.auth.HTTPBasicAuth(client_id, client_secret),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={"grant_type": "refresh_token", "refresh_token": refresh_token},
            timeout=15,
        )
        response.raise_for_status()
        payload = response.json()
        self.spotify_token = payload["access_token"]
        self.spotify_token_expires_at = time.time() + payload.get("expires_in", 3600) - 60
        return True

    def _spotify_request(self, url):
        if not self.spotify_token or time.time() >= self.spotify_token_expires_at:
            self._refresh_spotify_token()

        response = self.session.get(
            url,
            headers={
                "Accept": "application/json",
                "Accept-Language": "en",
                "App-Platform": "WebPlayer",
                "Authorization": f"Bearer {self.spotify_token}",
                "Spotify-App-Version": "1.2.40.176.g6d58cb73",
                "Cookie": self.credentials.get("cookies", ""),
                "Referer": "https://open.spotify.com/",
            },
            timeout=15,
        )
        response.raise_for_status()
        return response

    def _get_current_playback(self):
        response = self._spotify_request("https://api.spotify.com/v1/me/player")
        if response.status_code == 204:
            return None

        payload = response.json()
        item = payload.get("item")
        if not payload.get("is_playing") or not item:
            return None

        track_id = item.get("id")
        if not track_id:
            return None

        return {
            "id": track_id,
            "name": item.get("name", ""),
            "artist": ", ".join(artist.get("name", "") for artist in item.get("artists", [])),
            "progress_ms": payload.get("progress_ms", 0),
        }

    def _get_lyrics(self, playback):
        try:
            response = self._spotify_request(
                f"https://spclient.wg.spotify.com/color-lyrics/v2/track/{playback['id']}"
                "?format=json&vocalRemoval=false&market=from_token"
            )
            lyrics = response.json().get("lyrics", {})
            if not lyrics.get("showUpsell") and lyrics.get("syncType") != "UNSYNCED":
                return [
                    {"time": int(line.get("startTimeMs", 0)), "text": line.get("words", "")}
                    for line in lyrics.get("lines", [])
                ]
        except requests.RequestException:
            pass

        response = self.session.get(
            "https://lrclib.net/api/get",
            params={"track_name": playback["name"], "artist_name": playback["artist"]},
            timeout=15,
        )
        response.raise_for_status()
        synced_lyrics = response.json().get("syncedLyrics") or ""
        return self._parse_lrc(synced_lyrics)

    def _parse_lrc(self, synced_lyrics):
        lines = []
        for raw_line in synced_lyrics.splitlines():
            if not raw_line.startswith("[") or "]" not in raw_line:
                continue
            timestamp, text = raw_line.split("]", 1)
            try:
                minutes, seconds = timestamp[1:].split(":", 1)
                time_ms = round((int(minutes) * 60 + float(seconds)) * 1000)
            except ValueError:
                continue
            lines.append({"time": time_ms, "text": text.strip()})
        return lines

    def _current_line(self, lines, progress_ms):
        current = None
        for line in lines:
            if line["time"] <= progress_ms:
                current = line
            else:
                break
        return current

    def _format_seconds(self, milliseconds):
        seconds = max(0, round(milliseconds / 1000))
        return f"{seconds // 60}:{seconds % 60:02d}"

    def _format_status(self, line):
        text = line["text"].replace("♪", "🎶")
        prefix = f"[{self._format_seconds(line['time'])}] " if self.show_timestamp else ""
        label = "Song lyrics - " if self.show_label else ""
        return (prefix + label + text)[:128]

    def _change_discord_status(self, text):
        token = self.credentials.get("token", "").strip()
        if not token:
            raise ValueError("Discord token is missing")

        response = self.session.patch(
            "https://discord.com/api/v9/users/@me/settings",
            headers={"Authorization": token, "Content-Type": "application/json"},
            json={
                "custom_status": {
                    "text": text,
                    "emoji_id": None,
                    "emoji_name": "🎶",
                    "expires_at": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime(time.time() + 60)),
                }
            },
            timeout=15,
        )
        response.raise_for_status()

    def _run(self):
        self._set_status("Starting Spotify Lyrics ...")
        last_track_id = None
        last_line_time = None
        lyrics = []

        while not self.stop_event.is_set():
            try:
                playback = self._get_current_playback()
                if not playback:
                    self._set_status("No Spotify track is playing.")
                    self.stop_event.wait(5)
                    continue

                if playback["id"] != last_track_id:
                    lyrics = self._get_lyrics(playback)
                    last_track_id = playback["id"]
                    last_line_time = None

                line = self._current_line(lyrics, playback["progress_ms"])
                if line and line["text"] and line["time"] != last_line_time:
                    self._change_discord_status(self._format_status(line))
                    last_line_time = line["time"]
                    self._set_status(f"{playback['artist']} - {playback['name']}")

                self.stop_event.wait(1)
            except (requests.RequestException, KeyError, ValueError) as error:
                self._set_status(f"Spotify Lyrics: {error}")
                self.stop_event.wait(10)

        self._set_status("Spotify Lyrics stopped.")