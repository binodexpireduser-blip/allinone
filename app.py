from flask import Flask
import threading
import os
import time
from bot import AllinOneBot

app = Flask(__name__)

# This function starts the bot
def run_irc():
    IRC_SERVER = "irc.hybridirc.com"
    IRC_PORT = 6667 # We are using 6667 as discussed
    IRC_NICK = "AllinOne"
    
    print("[*] IRC Thread is initializing...")
    while True:
        try:
            print(f"[*] Attempting to connect to {IRC_SERVER}...")
            bot = AllinOneBot(IRC_NICK, IRC_SERVER, IRC_PORT)
            bot.start()
        except Exception as e:
            print(f"[ERROR] Bot crashed: {e}")
            time.sleep(15)

# --- THE FIX: Start the thread HERE, not in the __main__ block ---
print("[*] Starting background IRC thread...")
t = threading.Thread(target=run_irc)
t.daemon = True
t.start()

@app.route('/')
def home():
    return "AllinOne Bot is active! 🚀 Check #chatwithworld on HybridIRC."

if __name__ == "__main__":
    # This block is only used when you run 'python app.py' locally.
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
