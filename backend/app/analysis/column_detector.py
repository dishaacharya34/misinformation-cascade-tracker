import re

COLUMN_ALIASES = {
    "post_id": [
        "post_id", "postid", "tweet_id", "tweetid",
        "id", "status_id", "content_id"
    ],
    "text": [
        "text", "post_text", "content", "tweet",
        "tweet_text", "message", "claim", "headline",
        "news_text", "description"
    ],
    "timestamp": [
        "timestamp", "created_at", "createdat",
        "date", "datetime", "time", "published_at"
    ],
    "parent_id": [
        "parent_id", "parentid", "reply_to",
        "in_reply_to_status_id", "source_post_id",
        "original_post_id", "parent_post_id"
    ],
    "user_id": [
        "user_id", "userid", "author_id",
        "account_id", "username", "author"
    ],
    "label": [
        "label", "class", "target", "is_misinformation",
        "misinformation_label", "veracity"
    ],
    "share_count": [
        "share_count", "shares", "retweet_count",
        "reposts", "reshare_count"
    ],
    "engagement": [
        "engagement", "engagement_count", "interactions"
    ],
}


def normalize_column_name(name: str) -> str:
    name = name.strip().lower()
    return re.sub(r"[^a-z0-9]+", "_", name).strip("_")


def detect_columns(columns):
    normalized = {
        column: normalize_column_name(str(column))
        for column in columns
    }

    detected = {}
    used_columns = set()

    for field, aliases in COLUMN_ALIASES.items():
        normalized_aliases = {
            normalize_column_name(alias) for alias in aliases
        }

        for original, normalized_name in normalized.items():
            if (
                original not in used_columns
                and normalized_name in normalized_aliases
            ):
                detected[field] = original
                used_columns.add(original)
                break

    return {
        "detected_columns": detected,
        "missing_fields": [
            field for field in COLUMN_ALIASES
            if field not in detected
        ],
    }
