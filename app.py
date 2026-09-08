from flask import Flask
import threading
import os
from bot import AllinOneBot

app = Flask(__name__)

@app.route('/')
def home():
    return "AllinOne Bot is running! 🚀"

def run_irc():
    # IRC config
    IRC_SERVER = "irc.hybridirc.com"
    IRC_PORT = 6697
    IRC_NICK = "AllinOne"
    
    bot = AllinOneBot(IRC_NICK, IRC_SERVER, IRC_PORT)
    bot.start()

if __name__ == "__main__":
    # Start IRC bot in background
    threading.Thread(target=run_irc, daemon=True).start()
    
    # Run Flask for Render/Heroku
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
