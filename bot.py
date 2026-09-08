import irc.bot
import irc.connection
import ssl
import time
import requests
import urllib.parse
import storage

class AllinOneBot(irc.bot.SingleServerIRCBot):
    def __init__(self, nickname, server, port):
        print(f"[*] Initializing {nickname} on {server}:{port}...")
        
        # Use SSL for 6697, Plain for 6667
        if port == 6697:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            factory = irc.connection.Factory(wrapper=ctx.wrap_socket)
            print("[*] SSL Context created.")
        else:
            factory = irc.connection.Factory()

        # Added 'realname' and increased reconnection frequency
        super().__init__([(server, port)], nickname, "Antonio AllInOne Bot", connect_factory=factory)
        
        self.admin = "antonio"
        self.cooldowns = {}
        self.cd_time = 8

    def on_welcome(self, c, e):
        print(f"[SUCCESS] Welcome received from {e.source}. Joining channels...")
        config = storage.get_config()
        if "#chatwithworld" not in config["default_channels"]:
            config["default_channels"].append("#chatwithworld")
            
        for channel in config["default_channels"]:
            print(f"[*] Joining {channel}...")
            c.join(channel)

    def on_join(self, c, e):
        print(f"[+] Successfully joined: {e.target}")

    def on_nicknameinuse(self, c, e):
        new_nick = c.get_nickname() + "_"
        print(f"[!] Nickname taken, trying {new_nick}")
        c.nick(new_nick)

    # This helps us see what is happening if it hangs
    def on_all_raw_messages(self, c, e):
        # Only print server notices/errors to keep logs clean
        if e.type in ["notice", "error", "433", "422"]:
            print(f"[SERVER] {e.type}: {e.arguments}")

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

        if author.lower() == self.admin:
            if cmd == "!callbot" and len(parts) > 1:
                c.join(parts[1])
            elif cmd == "!rembot" and len(parts) > 1:
                c.part(parts[1])
            elif cmd == "!djchan" and len(parts) > 1:
                chan = parts[1].lower()
                cfg = storage.get_config()
                if chan in cfg["default_channels"]: cfg["default_channels"].remove(chan)
                else: cfg["default_channels"].append(chan)
                storage.save_config(cfg)
                c.privmsg(target, f"⚙️ Default channels updated.")

        if cmd == "!aiocmd":
            c.privmsg(target, "🛠️ !gtime, !topnews, !wiki, !weather, !btc, !eth, !quote, !advice, !catfact, !iss, !math, !urban 📜")

        elif cmd == "!gtime":
            ok, sec = self.check_cd("gtime")
            if not ok: return c.privmsg(target, f"⏳ {author}, wait {sec}s...")
            loc = parts[1] if len(parts) > 1 else "London"
            res = requests.get(f"https://wttr.in/{urllib.parse.quote(loc)}?format=%T+%Z").text.strip()
            c.privmsg(target, f"🕒 Time in {loc.upper()}: {res} 🌍")

        elif cmd == "!topnews":
            ok, _ = self.check_cd("news")
            if not ok: return
            cc = parts[1] if len(parts) > 1 else "us"
            rss = f"https://news.google.com/rss/headlines/section/geo/{cc.upper()}"
            url = f"https://api.rss2json.com/v1/api.json?rss_url={urllib.parse.quote(rss)}"
            try:
                data = requests.get(url).json()
                item = data['items'][0]
                c.privmsg(target, f"📰 {item['title']} 🔗 {item['link'].split('&url=')[-1]}")
            except: pass

        elif cmd == "!wiki":
            ok, _ = self.check_cd("wiki")
            if not ok: return
            topic = " ".join(parts[1:]) if len(parts) > 1 else "Internet"
            data = requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(topic)}").json()
            c.privmsg(target, f"📖 {data.get('extract', '...')[:300]}")
