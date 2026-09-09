import requests

import config

HEADERS = {"User-Agent": "AllinOneIRCBot/1.0"}
TIMEOUT = 8

# Common country name -> ISO 3166-1 alpha-2 code, for !news.
# Extend this dict as needed.
COUNTRY_CODES = {
    "usa": "us", "united states": "us", "us": "us", "america": "us",
    "uk": "gb", "united kingdom": "gb", "britain": "gb", "gb": "gb",
    "nepal": "np", "np": "np",
    "india": "in", "in": "in",
    "china": "cn", "cn": "cn",
    "japan": "jp", "jp": "jp",
    "germany": "de", "de": "de",
    "france": "fr", "fr": "fr",
    "canada": "ca", "ca": "ca",
    "australia": "au", "au": "au",
    "russia": "ru", "ru": "ru",
    "brazil": "br", "br": "br",
    "italy": "it", "it": "it",
    "spain": "es", "es": "es",
    "south korea": "kr", "korea": "kr", "kr": "kr",
    "pakistan": "pk", "pk": "pk",
    "bangladesh": "bd", "bd": "bd",
    "mexico": "mx", "mx": "mx",
    "netherlands": "nl", "nl": "nl",
    "singapore": "sg", "sg": "sg",
    "uae": "ae", "united arab emirates": "ae", "ae": "ae",
    "ireland": "ie", "ie": "ie",
    "switzerland": "ch", "ch": "ch",
    "sweden": "se", "se": "se",
    "norway": "no", "no": "no",
    "south africa": "za", "za": "za",
    "egypt": "eg", "eg": "eg",
    "indonesia": "id", "id": "id",
    "philippines": "ph", "ph": "ph",
    "malaysia": "my", "my": "my",
    "turkey": "tr", "tr": "tr",
    "argentina": "ar", "ar": "ar",
    "new zealand": "nz", "nz": "nz",
}

WEATHER_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Depositing rime fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
    80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
    95: "Thunderstorm", 96: "Thunderstorm w/ hail", 99: "Thunderstorm w/ heavy hail",
}

VALID_SIGNS = [
    "aries", "taurus", "gemini", "cancer", "leo", "virgo", "libra",
    "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"
]


def _geocode(city):
    """City name -> {lat, lon, name, country} using Open-Meteo's free geocoder."""
    r = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": city, "count": 1},
        headers=HEADERS, timeout=TIMEOUT
    )
    r.raise_for_status()
    results = r.json().get("results")
    if not results:
        return None
    res = results[0]
    return {
        "lat": res["latitude"],
        "lon": res["longitude"],
        "name": res.get("name", city),
        "country": res.get("country", "")
    }


def get_weather(city):
    loc = _geocode(city)
    if not loc:
        return f"\u26a0\ufe0f Couldn't find a location named '{city}'."
    r = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": loc["lat"], "longitude": loc["lon"],
            "current": "temperature_2m,weather_code,wind_speed_10m"
        },
        headers=HEADERS, timeout=TIMEOUT
    )
    r.raise_for_status()
    cur = r.json().get("current", {})
    c = cur.get("temperature_2m")
    if c is None:
        return "\u26a0\ufe0f Weather data unavailable right now."
    f = round(c * 9 / 5 + 32, 1)
    desc = WEATHER_CODES.get(cur.get("weather_code"), "Unknown conditions")
    wind = cur.get("wind_speed_10m")
    place = f"{loc['name']}, {loc['country']}" if loc["country"] else loc["name"]
    return f"\U0001f324\ufe0f Weather in {place}: {c}\u00b0C / {f}\u00b0F, {desc}, wind {wind} km/h."


def get_time(city):
    loc = _geocode(city)
    if not loc:
        return f"\u26a0\ufe0f Couldn't find a location named '{city}'."
    r = requests.get(
        "https://timeapi.io/api/Time/current/coordinate",
        params={"latitude": loc["lat"], "longitude": loc["lon"]},
        headers=HEADERS, timeout=TIMEOUT
    )
    r.raise_for_status()
    data = r.json()
    dt = data.get("dateTime", "")[:19].replace("T", " ")
    tz = data.get("timeZone", "Unknown")
    place = f"{loc['name']}, {loc['country']}" if loc["country"] else loc["name"]
    return f"\U0001f552 {place}: {dt} ({tz})"


def get_horoscope(sign):
    sign_norm = sign.strip().lower()
    if sign_norm not in VALID_SIGNS:
        return f"\u26a0\ufe0f '{sign}' isn't a valid zodiac sign."
    r = requests.get(
        "https://horoscope-app-api.vercel.app/api/v1/get-horoscope/daily",
        params={"sign": sign_norm, "day": "today"},
        headers=HEADERS, timeout=TIMEOUT
    )
    r.raise_for_status()
    data = r.json().get("data", {})
    horoscope = data.get("horoscope_data", "No reading available today.")
    return f"\U0001f52e {sign_norm.capitalize()} \u2014 {horoscope}"


def get_wiki_summary(topic):
    r = requests.get(
        f"https://en.wikipedia.org/api/rest_v1/page/summary/{requests.utils.quote(topic)}",
        headers=HEADERS, timeout=TIMEOUT
    )
    if r.status_code == 404:
        return f"\u26a0\ufe0f No Wikipedia article found for '{topic}'."
    r.raise_for_status()
    data = r.json()
    extract = data.get("extract", "No summary available.")
    sentences = extract.split(". ")
    summary = ". ".join(sentences[:3]).strip()
    if summary and not summary.endswith("."):
        summary += "."
    url = data.get("content_urls", {}).get("desktop", {}).get("page", "")
    return f"\U0001f4d6 {data.get('title', topic)}: {summary} {url}".strip()


def get_definition(word):
    r = requests.get(
        f"https://api.dictionaryapi.dev/api/v2/entries/en/{requests.utils.quote(word)}",
        headers=HEADERS, timeout=TIMEOUT
    )
    if r.status_code == 404:
        return f"\u26a0\ufe0f No definition found for '{word}'."
    r.raise_for_status()
    data = r.json()[0]
    meaning = data.get("meanings", [{}])[0]
    pos = meaning.get("partOfSpeech", "unknown")
    definition_entry = meaning.get("definitions", [{}])[0]
    definition = definition_entry.get("definition", "No definition available.")
    example = definition_entry.get("example", "")
    result = f"\U0001f4d8 {word} ({pos}): {definition}"
    if example:
        result += f" | e.g. \"{example}\""
    return result


def _gnews_top_headlines(country_code):
    r = requests.get(
        "https://gnews.io/api/v4/top-headlines",
        params={"country": country_code, "lang": "en", "max": 3, "apikey": config.GNEWS_API_KEY},
        headers=HEADERS, timeout=TIMEOUT
    )
    r.raise_for_status()
    return r.json().get("articles", [])


def _gnews_search(query):
    r = requests.get(
        "https://gnews.io/api/v4/search",
        params={"q": query, "lang": "en", "max": 3, "apikey": config.GNEWS_API_KEY},
        headers=HEADERS, timeout=TIMEOUT
    )
    r.raise_for_status()
    return r.json().get("articles", [])


def get_news(country):
    code = COUNTRY_CODES.get(country.strip().lower())
    if not code:
        return (f"\u26a0\ufe0f Unknown country '{country}'. "
                f"Try the full name or a 2-letter code (e.g. 'us', 'np').")
    try:
        articles = _gnews_top_headlines(code)
    except requests.RequestException:
        return "\u26a0\ufe0f Couldn't fetch news right now."
    if not articles:
        return f"\u26a0\ufe0f No headlines found for '{country}'."
    lines = [f"{i+1}. {a['title']}" for i, a in enumerate(articles[:3])]
    return f"\U0001f4f0 Top headlines ({country}): " + " | ".join(lines)


def get_sportsnews(sport):
    try:
        articles = _gnews_search(sport)
    except requests.RequestException:
        return "\u26a0\ufe0f Couldn't fetch sports news right now."
    if not articles:
        return f"\u26a0\ufe0f No recent news found for '{sport}'."
    lines = [f"{i+1}. {a['title']}" for i, a in enumerate(articles[:3])]
    return f"\U0001f3c6 {sport.capitalize()} headlines: " + " | ".join(lines)


def get_translation(text):
    text = text.strip()
    if len(text) > 480:
        text = text[:480]
    params = {"q": text, "langpair": "autodetect|en"}
    if config.MYMEMORY_EMAIL:
        params["de"] = config.MYMEMORY_EMAIL
    r = requests.get(
        "https://api.mymemory.translated.net/get",
        params=params, headers=HEADERS, timeout=TIMEOUT
    )
    r.raise_for_status()
    data = r.json()
    translated = data.get("responseData", {}).get("translatedText", "")
    if not translated:
        return "\u26a0\ufe0f Translation failed."
    matches = data.get("matches", [])
    source_lang = matches[0].get("source", "auto").split("-")[0] if matches else "auto"
    return f"\U0001f310 {translated} ({source_lang} -> en)"
