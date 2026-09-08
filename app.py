from flask import Flask
import threading
import os
import time
from bot import AllinOneBot

app = Flask(__name__)

def run_irc():
    IRC_SERVER = "irc.hybridirc.com"
    IRC_PORT = 6697  # SSL Port is usually safer on cloud hosts
    IRC_NICK = f"AIO_Ant_Bot_{int(time.time()) % 1000}" # Unique Nickname
    
    print(f"[*] Starting IRC Thread. Nick: {IRC_NICK}")
    while True:
        try:
            bot = AllinOneBot(IRC_NICK, IRC_SERVER, IRC_PORT)
            bot.start()
        except Exception as e:
            print(f"[CRASH] {e}")
            time.sleep(15)

# Trigger thread
threading.Thread(target=run_irc, daemon=True).start()

@app.route('/')
def home():
    return "AllinOne Bot is active! 🚀"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
