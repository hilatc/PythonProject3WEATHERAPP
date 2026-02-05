import requests

WIKI_SUMMARY_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/{title}"

# Wikipedia strongly prefers a real User-Agent:
# https://meta.wikimedia.org/wiki/User-Agent_policy
HEADERS = {
    "User-Agent": "SurfWeatherDashboard/1.0 (educational project; contact: hila@example.com)",
    "Accept": "application/json",
}


class SurferAPIError(Exception):
    pass


def get_wiki_summary(title: str) -> dict:
    """
    Fetches a Wikipedia summary + thumbnail (if available) for a given page title.
    """
    url = WIKI_SUMMARY_URL.format(title=title.replace(" ", "_"))
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            raise SurferAPIError(f"Wikipedia error {r.status_code} for {title}")
        return r.json()
    except requests.RequestException as e:
        raise SurferAPIError(str(e))


def build_top_surfers() -> list[dict]:
    """
    Curated legends list. We show "known_for" and pull bio+image from Wikipedia.
    """
    return [
        {"name": "Kelly Slater", "wiki_title": "Kelly Slater", "known_for": "11× World Champion (men)"},
        {"name": "Stephanie Gilmore", "wiki_title": "Stephanie Gilmore", "known_for": "8× World Champion (women)"},
        {"name": "Layne Beachley", "wiki_title": "Layne Beachley", "known_for": "7× World Champion (women)"},
    ]
