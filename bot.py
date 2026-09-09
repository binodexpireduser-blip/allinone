import threading
import time

import irc.bot

import config
import services
import storage

PUBLIC_COMMANDS = [
    "!weather", "!time", "!horoscope", "!wiki", "!define",
    "!news", "!sportsnews", "!translate", "!aiocmd"
]
ADMIN_COMMANDS = ["!on", "!off", "!call", "!part", "!djchan", "!rjchan"]

AIOCMD_TEXT = (
    "\U0001f916 Public commands: "
    "!weather <city> | !time <city> | !horoscope <sign> | !wiki <topic> | "
    "!define <word> | !news <country> | !sportsnews <sport> | "
    "!translate <text> | !aiocmd "
    "(each usable once every {}s)"
).format(config.COMMAND_COOLDOWN_SECONDS)


class AllinOneBot(irc.bot.SingleServerIRCBot):
    def __init__(self):
        server_list = [(config.IRC_SERVER, config.IRC_PORT)]
        super().__init__(
            server_list,
            config.IRC_NICK,
            config.IRC_REALNAME,
            # Native library-level reconnection with exponential backoff.
            # Handles dropped connections, server timeouts, etc. automatically.
            recon=irc.bot.ExponentialBackoff(min_interval=10, max_interval=120)
        )
        self._cooldowns = {}
        self._cooldown_lock = threading.Lock()

    # ---------------- connection lifecycle ----------------

    def on_welcome(self, c, e):
        print(f"[+] Connected to {config.IRC_SERVER} as {c.get_nickname()}")
        data = storage.get_channels()
        for chan in data["default_channels"]:
            c.join(chan)
            print(f"[+] Joined {chan}")

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_disconnect(self, c, e):
        print("[!] Disconnected from server \u2014 reconnect will be attempted automatically.")

    def on_kick(self, c, e):
        # Auto-rejoin if kicked from a default-join channel.
        channel = e.target
        data = storage.get_channels()
        if channel.lower() in [x.lower() for x in data["default_channels"]]:
            time.sleep(5)
            try:
                c.join(channel)
            except Exception as ex:
                print(f"[!] Failed to rejoin {channel} after kick: {ex}")

    def on_ping(self, c, e):
        # The irc library replies to PING automatically at the connection level;
        # this is just here for visibility/logging.
        pass

    # ---------------- helpers ----------------

    def _is_admin(self, nick):
        return nick.strip().lower() == config.ADMIN_NICK.strip().lower()

    def _check_cooldown(self, nick, cmd):
        """Returns seconds remaining if still on cooldown, else 0 and marks used."""
        key = (nick.lower(), cmd)
        now = time.time()
        with self._cooldown_lock:
            last = self._cooldowns.get(key, 0)
            remaining = config.COMMAND_COOLDOWN_SECONDS - (now - last)
            if remaining > 0:
                return remaining
            self._cooldowns[key] = now
        return 0

    def _reply(self, c, target, msg):
        if len(msg) > 420:
            msg = msg[:417] + "..."
        try:
            c.privmsg(target, msg)
        except Exception as ex:
            print(f"[!] Failed to send message to {target}: {ex}")

    # ---------------- public commands (channel messages) ----------------

    def on_pubmsg(self, c, e):
        msg = e.arguments[0].strip()
        if not msg.startswith("!"):
            return

        nick = e.source.nick
        channel = e.target
        parts = msg.split(maxsplit=1)
        cmd = parts[0].lower()
        arg = parts[1].strip() if len(parts) > 1 else ""

        if cmd == "!aiocmd":
            self._reply(c, channel, AIOCMD_TEXT)
            return

        if cmd not in PUBLIC_COMMANDS:
            return

        # !off disables these service commands in this channel (aiocmd stays available above)
        if storage.is_channel_disabled(channel):
            return

        if not arg:
            self._reply(c, channel, f"\u26a0\ufe0f Usage: {cmd} <value>")
            return

        wait = self._check_cooldown(nick, cmd)
        if wait > 0:
            self._reply(c, channel, f"\u23f3 {nick}, please wait {int(wait) + 1}s before using {cmd} again.")
            return

        threading.Thread(
            target=self._handle_public_command, args=(c, channel, cmd, arg), daemon=True
        ).start()

    def _handle_public_command(self, c, channel, cmd, arg):
        try:
            if cmd == "!weather":
                result = services.get_weather(arg)
            elif cmd == "!time":
                result = services.get_time(arg)
            elif cmd == "!horoscope":
                result = services.get_horoscope(arg)
            elif cmd == "!wiki":
                result = services.get_wiki_summary(arg)
            elif cmd == "!define":
                result = services.get_definition(arg)
            elif cmd == "!news":
                result = services.get_news(arg)
            elif cmd == "!sportsnews":
                result = services.get_sportsnews(arg)
            elif cmd == "!translate":
                result = services.get_translation(arg)
            else:
                return
        except Exception as ex:
            print(f"[!] Error handling {cmd} '{arg}': {ex}")
            result = "\u26a0\ufe0f Something went wrong fetching that. Try again shortly."
        self._reply(c, channel, result)

    # ---------------- admin commands (PM only) ----------------

    def on_privmsg(self, c, e):
        msg = e.arguments[0].strip()
        nick = e.source.nick

        if not msg.startswith("!"):
            return

        parts = msg.split(maxsplit=1)
        cmd = parts[0].lower()
        arg = parts[1].strip() if len(parts) > 1 else ""

        if cmd == "!aiocmd":
            c.privmsg(nick, AIOCMD_TEXT)
            return

        if cmd not in ADMIN_COMMANDS:
            return

        if not self._is_admin(nick):
            c.privmsg(nick, "\U0001f6ab Admin commands only.")
            return

        if not arg:
            c.privmsg(nick, f"\u26a0\ufe0f Usage: {cmd} #channel")
            return

        channel = arg.split()[0]
        if not channel.startswith("#"):
            c.privmsg(nick, "\u26a0\ufe0f Channel must start with #.")
            return

        if cmd == "!on":
            storage.set_channel_enabled(channel, True)
            c.privmsg(nick, f"\u2705 Public commands enabled in {channel}.")

        elif cmd == "!off":
            storage.set_channel_enabled(channel, False)
            c.privmsg(nick, f"\U0001f6d1 Public commands disabled in {channel}.")

        elif cmd == "!call":
            try:
                c.join(channel)
                c.privmsg(nick, f"\u27a1\ufe0f Joined {channel}.")
            except Exception as ex:
                c.privmsg(nick, f"\u26a0\ufe0f Failed to join {channel}: {ex}")

        elif cmd == "!part":
            try:
                c.part(channel)
                c.privmsg(nick, f"\u2b05\ufe0f Left {channel}.")
            except Exception as ex:
                c.privmsg(nick, f"\u26a0\ufe0f Failed to part {channel}: {ex}")

        elif cmd == "!djchan":
            added = storage.add_default_channel(channel)
            if added:
                c.privmsg(nick, f"\u2b50 {channel} added to default-join channels.")
            else:
                c.privmsg(nick, f"\u2139\ufe0f {channel} is already a default-join channel.")

        elif cmd == "!rjchan":
            result = storage.remove_default_channel(channel)
            if result == "protected":
                c.privmsg(nick, f"\U0001f512 {channel} is the primary default channel and can't be removed.")
            elif result:
                c.privmsg(nick, f"\U0001f5d1\ufe0f {channel} removed from default-join channels.")
            else:
                c.privmsg(nick, f"\u2139\ufe0f {channel} wasn't in the default-join list.")
