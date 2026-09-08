from flask import Flask
import threading
import os
import time
from bot import AllinOneBot

app = Flask(__name__)

def run_irc():
    # HybridIRC Server Settings
    IRC_SERVER = "irc.hybridirc.com"
    IRC_PORT = 6697  # Back to SSL
    IRC_NICK = f"AIOBot_{int(time.time()) % 1000}"
    
    print("[*] IRC Thread starting...", flush=True)
    
    while True:
        try:
            print(f"[*] Connecting to {IRC_SERVER}:{IRC_PORT}...", flush=True)
            bot = AllinOneBot(IRC_NICK, IRC_SERVER, IRC_PORT)
            bot.start()
        except Exception as e:
            print(f"[CRASH] {e}", flush=True)
            time.sleep(20)

# Launch thread
t = threading.Thread(target=run_irc, daemon=True)
t.start()

@app.route('/')
def home():
    return "AllinOne Bot is running! 🚀"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
