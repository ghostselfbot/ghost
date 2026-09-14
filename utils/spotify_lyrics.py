import threading
import time

import requests


class SpotifyLyricsService:
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
            raise ValueError("Spotify Client ID, Client Secret und Refresh Token werden benötigt")

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

        return {
            "id": item.get("id"),
            "name": item.get("name", ""),
            "artist": ", ".join(artist.get("name", "") for artist in item.get("artists", [])),
            "progress_ms": payload.get("progress_ms", 0),
        }

    def _get_lyrics(self, track_id):
        response = self._spotify_request(
            f"https://spclient.wg.spotify.com/color-lyrics/v2/track/{track_id}"
            "?format=json&vocalRemoval=false&market=from_token"
        )
        lyrics = response.json().get("lyrics", {})
        if lyrics.get("showUpsell") or lyrics.get("syncType") == "UNSYNCED":
            return []

        return [
            {"time": int(line.get("startTimeMs", 0)), "text": line.get("words", "")}
            for line in lyrics.get("lines", [])
        ]

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
            raise ValueError("Discord Token fehlt")

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
        self._set_status("Spotify Lyrics wird gestartet ...")
        last_track_id = None
        last_line_time = None
        lyrics = []

        while not self.stop_event.is_set():
            try:
                playback = self._get_current_playback()
                if not playback:
                    self._set_status("Kein Spotify-Song läuft.")
                    self.stop_event.wait(5)
                    continue

                if playback["id"] != last_track_id:
                    lyrics = self._get_lyrics(playback["id"])
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

        self._set_status("Spotify Lyrics gestoppt.")