from flask import Flask
import threading
import os
import time
from bot import AllinOneBot

app = Flask(__name__)

@app.route('/')
def home():
    return "AllinOne Bot is active! 🚀 Check #chatwithworld on HybridIRC."

def run_irc():
    # IRC config
    IRC_SERVER = "irc.hybridirc.com"
    IRC_PORT = 6667 # PLAIN PORT
    IRC_NICK = "AllinOne"
    
    print("[*] Starting IRC thread...")
    while True:
        try:
            bot = AllinOneBot(IRC_NICK, IRC_SERVER, IRC_PORT)
            bot.start()
        except Exception as e:
            print(f"[ERROR] {e}")
            time.sleep(15)

if __name__ == "__main__":
    t = threading.Thread(target=run_irc)
    t.daemon = True
    t.start()
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
