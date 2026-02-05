import pandas as pd


def surf_score_row(
    wave_h: float,
    period: float,
    wind_spd: float,
    wind_relation: str | None = None,
    level: str = "Intermediate",
) -> int:
    """
    Returns a surf score 0-100.
    level affects what is considered "good":
      - Beginner: prefers smaller waves & lower wind
      - Intermediate: balanced
      - Advanced: prefers bigger waves & tolerates more wind
    """
    score = 0

    if wave_h is None:
        return 0

    # -------------------------
    # Wave height contribution (changes by level)
    # -------------------------
    if level == "Beginner":
        # Best range: ~0.4-1.0m
        if wave_h < 0.2:
            score += 5
        elif wave_h < 0.4:
            score += 25
        elif wave_h < 0.8:
            score += 55
        elif wave_h < 1.2:
            score += 45
        else:
            score += 15  # too big for beginner

    elif level == "Advanced":
        # Best range: ~0.9-2.0m
        if wave_h < 0.4:
            score += 5
        elif wave_h < 0.8:
            score += 25
        elif wave_h < 1.2:
            score += 55
        elif wave_h < 2.0:
            score += 75
        else:
            score += 65

    else:  # Intermediate (your original logic, slightly polished)
        if wave_h < 0.3:
            score += 5
        elif wave_h < 0.6:
            score += 20
        elif wave_h < 1.0:
            score += 40
        elif wave_h < 1.5:
            score += 60
        else:
            score += 75

    # -------------------------
    # Period contribution (same for all levels)
    # -------------------------
    if period is not None:
        if period < 6:
            score += 5
        elif period < 9:
            score += 15
        elif period < 12:
            score += 25
        else:
            score += 30

    # -------------------------
    # Wind contribution (changes by level)
    # -------------------------
    if wind_spd is not None:
        if level == "Beginner":
            # stricter
            if wind_spd < 3:
                score += 20
            elif wind_spd < 6:
                score += 10
            elif wind_spd < 9:
                score -= 10
            else:
                score -= 20

        elif level == "Advanced":
            # more tolerant
            if wind_spd < 4:
                score += 15
            elif wind_spd < 8:
                score += 5
            elif wind_spd < 12:
                score -= 5
            else:
                score -= 12

        else:  # Intermediate (your original)
            if wind_spd < 4:
                score += 20
            elif wind_spd < 7:
                score += 10
            elif wind_spd < 10:
                score -= 5
            else:
                score -= 15

    # -------------------------
    # Wind relation adjustment
    # -------------------------
    if wind_relation == "Offshore":
        score += 10
    elif wind_relation == "Onshore":
        score -= 10

    return max(0, min(100, score))


def add_scores(df: pd.DataFrame, level: str = "Intermediate") -> pd.DataFrame:
    """
    Adds a 'surf_score' column based on level.
    """
    df = df.copy()
    df["surf_score"] = df.apply(
        lambda r: surf_score_row(
            r.get("wave_height"),
            r.get("wave_period"),
            r.get("wind_speed"),
            r.get("wind_relation"),
            level,
        ),
        axis=1,
    )
    return df


def best_hours(df: pd.DataFrame, top_n: int = 6) -> pd.DataFrame:
    cols = [
        "time",
        "wave_height",
        "wave_period",
        "wind_speed",
        "surf_score",
        "wave_dir",
        "wind_dir",
        "wind_relation",
    ]
    out = df.sort_values("surf_score", ascending=False).head(top_n)
    return out[cols]
