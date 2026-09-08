from flask import Flask
import threading
import os
import time
from bot import AllinOneBot

app = Flask(__name__)

def run_irc():
    IRC_SERVER = "irc.hybridirc.com"
    # Try Port 6697 first. If it fails, we will try 6667.
    IRC_PORT = 6697 
    # Use a clean, simple nickname
    IRC_NICK = f"AIOBot_{int(time.time()) % 1000}"
    
    print(f"[*] Background thread started. Waiting 5s for Flask...")
    time.sleep(5)
    
    while True:
        try:
            print(f"[*] Connection attempt to {IRC_SERVER}:{IRC_PORT}...")
            bot = AllinOneBot(IRC_NICK, IRC_SERVER, IRC_PORT)
            bot.start()
        except Exception as e:
            print(f"[CRASH ERROR] {e}")
            print("[*] Restarting in 20 seconds...")
            time.sleep(20)

# Start the background thread
t = threading.Thread(target=run_irc, daemon=True)
t.start()

@app.route('/')
def home():
    return "AllinOne Bot is running! 🚀"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
