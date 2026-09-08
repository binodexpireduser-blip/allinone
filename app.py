from flask import Flask
import threading
import os
import time
from bot import AllinOneBot

app = Flask(__name__)

@app.route('/')
def home():
    return "AllinOne Bot is running! 🚀 Check your IRC channel."

def run_irc():
    # IRC config
    IRC_SERVER = "irc.hybridirc.com"
    IRC_PORT = 6667
    IRC_NICK = "AllinOne"
    
    print("[*] Thread starting: IRC Bot")
    while True:
        try:
            bot = AllinOneBot(IRC_NICK, IRC_SERVER, IRC_PORT)
            bot.start()
        except Exception as e:
            print(f"[!] Bot crashed or couldn't connect: {e}")
            print("[*] Retrying in 15 seconds...")
            time.sleep(15)

if __name__ == "__main__":
    # Start IRC bot in background
    irc_thread = threading.Thread(target=run_irc)
    irc_thread.daemon = True
    irc_thread.start()
    
    # Run Flask
    port = int(os.environ.get("PORT", 5000))
    print(f"[*] Flask starting on port {port}")
    app.run(host='0.0.0.0', port=port)
