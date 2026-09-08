import irc.bot
import ssl
import time
import requests
import urllib.parse
import storage

class AllinOneBot(irc.bot.SingleServerIRCBot):
    def __init__(self, nickname, server, port):
        print(f"[*] Initializing bot: {nickname} on {server}:{port}...")
        
        # FIX: Create a more relaxed SSL context for IRC servers
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE  # This ignores SSL certificate errors
        
        factory = irc.connection.Factory(wrapper=ssl_context.wrap_socket)
        
        super().__init__([(server, port)], nickname, nickname, connect_factory=factory)
        self.admin = "antonio"
        self.cooldowns = {}
        self.cd_time = 8

    def on_connect(self, c, e):
        print(f"[DEBUG] Socket connected to server!")

    def on_welcome(self, c, e):
        print(f"[DEBUG] Welcome message received from server. Joining channels...")
        config = storage.get_config()
        # Ensure we join the primary channel requested
        if "#chatwithworld" not in config["default_channels"]:
            config["default_channels"].append("#chatwithworld")
            
        for channel in config["default_channels"]:
            c.join(channel)
            print(f"[+] AllinOne joined {channel}")

    def on_join(self, c, e):
        print(f"[DEBUG] Successfully joined: {e.target}")

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

        # Admin Control
        if author.lower() == self.admin:
            if cmd == "!callbot" and len(parts) > 1:
                c.join(parts[1])
                c.privmsg(target, f"🚀 Joining {parts[1]} for you, Antonio!")
            elif cmd == "!rembot" and len(parts) > 1:
                c.part(parts[1])
                c.privmsg(target, f"👋 Left {parts[1]}.")
            elif cmd == "!djchan" and len(parts) > 1:
                chan = parts[1].lower()
                cfg = storage.get_config()
                if chan in cfg["default_channels"]:
                    cfg["default_channels"].remove(chan)
                    c.privmsg(target, f"➖ {chan} removed from auto-join.")
                else:
                    cfg["default_channels"].append(chan)
                    c.privmsg(target, f"➕ {chan} added to auto-join.")
                storage.save_config(cfg)

        # Main Commands
        if cmd == "!aiocmd":
            c.privmsg(target, "🛠️ **Commands:** !gtime, !topnews, !wiki, !weather, !btc, !eth, !quote, !advice, !catfact, !iss, !today, !isup, !math, !number, !urban, !affirm, !excuse, !zen, !stoic, !bored, !gender, !element, !verse, !rhyme, !cocktail, !poke, !dict, !space, !brewery, !sun, !kanye, !fruit, !holiday, !pass 📜")

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
                c.privmsg(target, f"📰 [News {cc.upper()}] {item['title']} 🔗 {item['link'].split('&url=')[-1]} 🗞️")
            except: c.privmsg(target, "❌ News error.")

        elif cmd == "!wiki":
            ok, _ = self.check_cd("wiki")
            if not ok: return
            topic = " ".join(parts[1:]) if len(parts) > 1 else "Internet"
            try:
                data = requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(topic)}").json()
                c.privmsg(target, f"📖 {data.get('extract', 'Not found')[:350]}... 🧐")
            except: pass

        elif cmd == "!weather":
            ok, _ = self.check_cd("weather")
            if not ok: return
            city = parts[1] if len(parts) > 1 else "London"
            try:
                geo = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1").json()
                res = geo['results'][0]
                w = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={res['latitude']}&longitude={res['longitude']}&current_weather=true").json()
                c.privmsg(target, f"🌡️ Weather in {res['name']}: {w['current_weather']['temperature']}°C 🌤️")
            except: c.privmsg(target, "❌ Weather error.")

        elif cmd in ["!btc", "!eth"]:
            ok, _ = self.check_cd("crypto")
            if not ok: return
            coin = "bitcoin" if "btc" in cmd else "ethereum"
            data = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd").json()
            c.privmsg(target, f"💰 {coin.upper()}: ${data[coin]['usd']:,} USD 🚀")

    def on_nicknameinuse(self, c, e):
        new_nick = c.get_nickname() + "_"
        print(f"[!] Nickname in use, trying {new_nick}")
        c.nick(new_nick)

    def on_error(self, c, e):
        print(f"[ERROR] IRC Error: {e.arguments}")

    def on_disconnect(self, c, e):
        print("[!] Bot disconnected from server. Reconnecting in 10s...")
        time.sleep(10)
