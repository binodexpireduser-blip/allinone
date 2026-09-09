import os
import threading
import time

from flask import Flask

from bot import AllinOneBot

app = Flask(__name__)

# Shared reference so the /health route can inspect live connection state.
_state = {"bot": None}


@app.route("/")
def home():
    return "AllinOneBOT is running! \U0001f680"


@app.route("/health")
def health():
    bot = _state.get("bot")
    connected = bool(bot and bot.connection and bot.connection.is_connected())
    status = {"irc_connected": connected}
    return status, (200 if connected else 503)


def run_irc():
    """
    Outer restart loop: the irc library's ExponentialBackoff strategy (configured
    in bot.py) already handles normal reconnects (dropped socket, server timeout,
    etc.) without this loop ever needing to run more than once. This loop is a
    safety net in case the whole bot object dies from an unexpected exception.
    """
    while True:
        try:
            bot = AllinOneBot()
            _state["bot"] = bot
            bot.start()  # blocks here; returns only if the bot truly gives up
            print("[!] bot.start() returned unexpectedly \u2014 restarting in 15s...")
        except Exception as ex:
            print(f"[!] IRC bot crashed: {ex} \u2014 restarting in 15s...")
        time.sleep(15)


if __name__ == "__main__":
    irc_thread = threading.Thread(target=run_irc, daemon=True)
    irc_thread.start()

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
