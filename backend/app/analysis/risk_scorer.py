def score_risks(results: dict) -> dict:
    """Prioritize observed propagation signals without claiming truth verification."""

    signals = []
    score = 0.0

    cascades = results.get("cascades", {})
    trends = results.get("trends", {})
    classification = results.get("classification", {})

    if cascades.get("available"):
        largest = max(
            cascades.get("cascades", []),
            key=lambda item: item.get("size", 0),
            default=None,
        )

        if largest:
            size = largest.get("size", 0)
            depth = largest.get("depth", 0)

            if size >= 20:
                score += 25
                signals.append("Large observed cascade")
            elif size >= 10:
                score += 15
                signals.append("Moderate observed cascade")

            if depth >= 5:
                score += 15
                signals.append("Deep propagation chain")
            elif depth >= 3:
                score += 8
                signals.append("Multi-level propagation chain")
    else:
        signals.append("Cascade evidence unavailable")

    if trends.get("available"):
        daily = trends.get("daily_posts", [])
        counts = [item["count"] for item in daily]

        if len(counts) >= 2 and max(counts) >= 2 * max(1, min(counts)):
            score += 10
            signals.append("Posting volume varies substantially")
    else:
        signals.append("Temporal evidence unavailable")

    if classification.get("available"):
        signals.append(
            "Dataset labels available; label meaning must be confirmed"
        )
    else:
        signals.append("No usable dataset labels detected")

    score = round(min(score, 100.0), 2)

    if score >= 60:
        level = "high"
    elif score >= 30:
        level = "medium"
    else:
        level = "low"

    return {
        "available": True,
        "score": score,
        "level": level,
        "signals": signals,
        "interpretation": (
            "This is a preliminary propagation-priority score, not a "
            "probability that content is false. It uses only the observed "
            "signals available in the uploaded dataset."
        ),
    }
