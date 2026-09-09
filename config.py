import os

# --- Replace this with your own GNews API key ---
# Get a free key at https://gnews.io/ (free tier: 100 requests/day)
# You can either paste it directly below, or set it as an env var GNEWS_API_KEY
GNEWS_API_KEY = os.environ.get("GNEWS_API_KEY", "494b8d3eb4619e3e14d9e8a74895374e")

# Optional: adding a contact email raises MyMemory's free translation limit
# from 5,000 to 50,000 words/day. Leave blank to skip.
MYMEMORY_EMAIL = os.environ.get("MYMEMORY_EMAIL", "binod.expireduser@gmail.com")

# --- IRC connection settings ---
IRC_SERVER = "irc.hybridirc.com"
IRC_PORT = 6667
IRC_NICK = "AllinOne"
IRC_REALNAME = "AllinOne IRC Bot"

# --- Admin ---
# Nick check is case-insensitive (done in bot.py)
ADMIN_NICK = "Antonio"

# --- Channels ---
DEFAULT_CHANNEL = "#ChatWithWorld"  # seed default channel, protected from removal

# --- Rate limiting ---
COMMAND_COOLDOWN_SECONDS = 10
