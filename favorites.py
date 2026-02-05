import json
from pathlib import Path

FAV_FILE = Path("favorites.json")


def load_favorites() -> list[str]:
    if not FAV_FILE.exists():
        return []
    try:
        return json.loads(FAV_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []


def save_favorites(favs: list[str]) -> None:
    seen = set()
    clean = []
    for x in favs:
        if x not in seen:
            clean.append(x)
            seen.add(x)

    try:
        FAV_FILE.write_text(json.dumps(clean, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        # On Streamlit Cloud it may reset; it's ok for the project.
        pass


def toggle_favorite(name: str) -> list[str]:
    favs = load_favorites()
    if name in favs:
        favs.remove(name)
    else:
        favs.insert(0, name)
    save_favorites(favs)
    return favs

