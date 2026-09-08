import irc.bot
import irc.connection
import ssl
import time
import requests
import urllib.parse
import storage

class AllinOneBot(irc.bot.SingleServerIRCBot):
    def __init__(self, nickname, server, port):
        print(f"[*] STARTING BOT: {nickname} on {server}:{port}")
        
        # SSL Context setup
        if port == 6697:
            print("[*] Creating SSL Context...")
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            # Force TLS 1.2+ for better compatibility
            ctx.options |= ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3
            factory = irc.connection.Factory(wrapper=ctx.wrap_socket)
        else:
            print("[*] Using Plain TCP Connection...")
            factory = irc.connection.Factory()

        # Initialize with a fixed username and realname (required by some servers)
        super().__init__([(server, port)], nickname, nickname, connect_factory=factory)
        
        self.admin = "antonio"
        self.cooldowns = {}
        self.cd_time = 8

    def on_connect(self, c, e):
        print("[*] Connection successful! Waiting for welcome...")

    def on_all_raw_messages(self, c, e):
        # This will print EVERYTHING from the server to your Render logs
        # If the server is rejecting you, you will see it here
        print(f"[RAW SERVER] {e.arguments}")

    def on_welcome(self, c, e):
        print(f"[SUCCESS] Joined {e.source}! Proceeding to channels...")
        config = storage.get_config()
        if "#chatwithworld" not in config["default_channels"]:
            config["default_channels"].append("#chatwithworld")
            
        for channel in config["default_channels"]:
            print(f"[*] Attempting JOIN: {channel}")
            c.join(channel)

    def on_join(self, c, e):
        print(f"[+] Bot is now in {e.target}")

    def on_nicknameinuse(self, c, e):
        new_nick = c.get_nickname() + "_"
        print(f"[!] Nick {c.get_nickname()} taken, trying {new_nick}")
        c.nick(new_nick)

    # --- COMMANDS ---
    def on_pubmsg(self, c, e):
        msg = e.arguments[0].strip()
        author = e.source.nick
        target = e.target
        parts = msg.split()
        if not parts: return
        cmd = parts[0].lower()

        if cmd == "!aiocmd":
            c.privmsg(target, "🛠️ !gtime, !topnews, !wiki, !weather, !btc, !eth, !quote, !advice, !catfact, !iss, !math, !urban 📜")

        elif cmd == "!gtime":
            loc = parts[1] if len(parts) > 1 else "London"
            try:
                res = requests.get(f"https://wttr.in/{urllib.parse.quote(loc)}?format=%T+%Z").text.strip()
                c.privmsg(target, f"🕒 Time in {loc.upper()}: {res} 🌍")
            except: pass
