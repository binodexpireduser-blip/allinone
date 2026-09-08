import irc.bot
import irc.connection
import ssl
import time
import requests
import urllib.parse
import storage
import sys

class AllinOneBot(irc.bot.SingleServerIRCBot):
    def __init__(self, nickname, server, port):
        print(f"[*] Initializing Bot: {nickname} on {server}:{port}", flush=True)
        
        if port == 6697:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            # Create SSL factory without the 'timeout' argument that caused the crash
            wrapper = ctx.wrap_socket
            factory = irc.connection.Factory(wrapper=wrapper)
        else:
            factory = irc.connection.Factory()

        super().__init__([(server, port)], nickname, nickname, connect_factory=factory)
        self.admin = "antonio"
        self.cooldowns = {}
        self.cd_time = 8

    def on_connect(self, c, e):
        print("[*] TCP Connection established!", flush=True)

    def on_all_raw_messages(self, c, e):
        # This will show us why the server might be hanging
        if e.type in ["notice", "error", "433", "422", "privmsg"]:
            print(f"[RAW] {e.type}: {e.arguments}", flush=True)

    def on_welcome(self, c, e):
        print(f"[SUCCESS] Welcome received! Joining #chatwithworld", flush=True)
        c.join("#chatwithworld")

    def on_nicknameinuse(self, c, e):
        new_nick = c.get_nickname() + "_"
        print(f"[!] Nick taken, trying {new_nick}", flush=True)
        c.nick(new_nick)

    def check_cd(self, cmd):
        now = time.time()
        if cmd in self.cooldowns:
            elapsed = now - self.cooldowns[cmd]
            if elapsed < self.cd_time:
                return False, int(self.cd_time - elapsed)
        self.cooldowns[cmd] = now
        return True, 0

    def on_pubmsg(self, c, e):
        msg = e.arguments[0].strip()
        author = e.source.nick
        target = e.target
        parts = msg.split()
        if not parts: return
        cmd = parts[0].lower()

        if cmd == "!aiocmd":
            c.privmsg(target, "🤖 AllinOne Commands: !gtime, !topnews, !wiki, !weather, !btc, !quote, !advice, !catfact")

        elif cmd == "!gtime":
            ok, sec = self.check_cd("gtime")
            if not ok: return
            loc = parts[1] if len(parts) > 1 else "London"
            try:
                res = requests.get(f"https://wttr.in/{urllib.parse.quote(loc)}?format=%T+%Z").text.strip()
                c.privmsg(target, f"🕒 Time in {loc.upper()}: {res} 🌍")
            except: pass
