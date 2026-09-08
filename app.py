from flask import Flask
import threading
import os
import time
import sys
from bot import AllinOneBot

app = Flask(__name__)

def run_irc():
    # Attempting Port 6667 first as it is often more stable for bots
    IRC_SERVER = "irc.hybridirc.com"
    IRC_PORT = 6667 
    IRC_NICK = f"AIO_Ant_{int(time.time()) % 1000}"
    
    print("[*] IRC Thread starting. Waiting 3s...", flush=True)
    time.sleep(3)
    
    while True:
        try:
            print(f"[*] Attempting connection to {IRC_SERVER}:{IRC_PORT}...", flush=True)
            bot = AllinOneBot(IRC_NICK, IRC_SERVER, IRC_PORT)
            bot.start()
        except Exception as e:
            print(f"[CRASH] Bot loop exited: {e}", flush=True)
            print("[*] Restarting in 15 seconds...", flush=True)
            time.sleep(15)

# Start the bot thread immediately
print("[*] Main script starting. Launching thread...", flush=True)
t = threading.Thread(target=run_irc, daemon=True)
t.start()

@app.route('/')
def home():
    return "Bot is alive! 🚀"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
