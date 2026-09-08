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
        print(f"[*] Initializing Bot Object for {server}:{port}...", flush=True)
        
        if port == 6697:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            # Use a connection factory with a 20-second timeout
            factory = irc.connection.Factory(wrapper=ctx.wrap_socket, timeout=20)
        else:
            factory = irc.connection.Factory(timeout=20)

        super().__init__([(server, port)], nickname, nickname, connect_factory=factory)
        self.admin = "antonio"

    def on_connect(self, c, e):
        print("[*] TCP Connection established. Sending NICK/USER...", flush=True)

    def on_all_raw_messages(self, c, e):
        # This will show us EXACTLY why the server is rejecting the bot
        print(f"[RAW SERVER] {e.type}: {e.arguments}", flush=True)

    def on_welcome(self, c, e):
        print(f"[SUCCESS] Welcome received from {e.source}!", flush=True)
        c.join("#chatwithworld")
        print("[*] Joined #chatwithworld", flush=True)

    def on_nicknameinuse(self, c, e):
        new_nick = c.get_nickname() + "_"
        print(f"[!] Nick taken, switching to {new_nick}", flush=True)
        c.nick(new_nick)

    def on_pubmsg(self, c, e):
        msg = e.arguments[0].strip()
        target = e.target
        if msg.lower() == "!aiocmd":
            c.privmsg(target, "🤖 AllinOne is alive! Commands: !gtime, !weather, !wiki, !topnews, !quote")

    # Add error logging
    def on_error(self, c, e):
        print(f"[IRC ERROR] {e.arguments}", flush=True)
