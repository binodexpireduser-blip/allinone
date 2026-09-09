# AllinOne IRC Bot

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Get a free GNews API key at https://gnews.io/ (used for `!news` and `!sportsnews`).
   Either:
   - Open `config.py` and replace `YOUR_GNEWS_API_KEY_HERE`, **or**
   - Set an environment variable `GNEWS_API_KEY` (recommended for deployment, so
     you don't commit the key to the repo).

3. (Optional) Set `MYMEMORY_EMAIL` env var to your email to raise the free
   translation quota from 5,000 to 50,000 words/day.

4. Run it:
   ```
   python app.py
   ```

## Deploying (e.g. Render)

- Set `GNEWS_API_KEY` (and optionally `MYMEMORY_EMAIL`) as environment variables
  in your host's dashboard rather than editing config.py directly.
- The Flask app exposes:
  - `/` \u2014 simple "is it running" ping, good for an external uptime monitor
    (e.g. UptimeRobot, cron-job.org) to stop the free-tier host from sleeping.
  - `/health` \u2014 returns `{"irc_connected": true/false}` with HTTP 200/503,
    so your monitor can tell if the process is up but the IRC connection has
    actually dropped.

## How reconnection works

Two layers:
1. The `irc` library's built-in `ExponentialBackoff` reconnection strategy
   (configured in `bot.py`) automatically retries the IRC connection on drops,
   timeouts, etc. This handles the vast majority of disconnects invisibly.
2. `app.py`'s `run_irc()` loop is a safety net: if the whole bot object ever
   dies from an unhandled exception, it's recreated and reconnected from
   scratch after a short delay.

PING/PONG keepalive is handled automatically at the library's connection
level \u2014 no extra code needed.

## Public commands (usable in any enabled channel)

| Command | Description |
|---|---|
| `!weather <city>` | Current temp (\u00b0C/\u00b0F) and conditions |
| `!time <city>` | Current local time and timezone |
| `!horoscope <sign>` | Today's horoscope for a zodiac sign |
| `!wiki <topic>` | 2\u20133 sentence Wikipedia summary + link |
| `!define <word>` | Definition, part of speech, example sentence |
| `!news <country>` | Top 3 headlines for a country |
| `!sportsnews <sport>` | Top 3 recent headlines mentioning that sport |
| `!translate <text>` | Auto-detect language \u2192 English |
| `!aiocmd` | Lists all commands |

Each command has a **10-second cooldown per user**. `!aiocmd` is exempt from
this and always works, even in a channel where the bot's other commands have
been turned off.

## Admin commands (PM the bot only, nick `Antonio`, case-insensitive)

| Command | Description |
|---|---|
| `!on #channel` | Re-enable public commands in a channel |
| `!off #channel` | Disable public commands in a channel (bot stays joined) |
| `!call #channel` | Join a channel |
| `!part #channel` | Leave a channel |
| `!djchan #channel` | Add a channel to the default-join list (auto-joined on connect/reconnect) |
| `!rjchan #channel` | Remove a channel from the default-join list |

`#ChatWithWorld` is the seed default channel and is protected \u2014
`!rjchan #ChatWithWorld` will refuse to remove it, so the bot can never end up
with zero default channels.

Admin commands only work via **private message** to the bot, never in a
channel, and only from a user whose nick matches `Antonio` (case-insensitive).

## Files

- `app.py` \u2014 Flask keep-alive server + IRC bot process supervisor
- `bot.py` \u2014 IRC bot: connection handling, command routing, cooldowns, admin auth
- `services.py` \u2014 all external API calls (weather, time, horoscope, wiki, dictionary, news, translate)
- `storage.py` \u2014 JSON persistence for default-join channels and per-channel on/off state
- `config.py` \u2014 all settings (API keys, nick, admin name, server, cooldown)
- `data/channels.json` \u2014 auto-created; stores channel state across restarts
