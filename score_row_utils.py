from typing import Dict, Iterable, List


SENTENCE_MODE = "sentence"
VOCAB_MODE = "vocab"

_SENTENCE_MODE_ALIASES = {
    "sentence",
    "sentences",
    "phrase",
    "phrases",
}
_VOCAB_MODE_ALIASES = {
    "vocab",
    "word",
    "words",
    "vocabulary",
}
_SENTENCE_HINT_KEYS = (
    "topic",
    "subtopic",
    "levels",
    "phrase_id",
    "phrase_ids",
    "points_main",
    "points_spartan_raw",
    "points_spartan_scaled",
)
_VOCAB_HINT_KEYS = (
    "group_id",
    "seed",
    "raw_points_total",
    "raw_points_main",
    "raw_points_spartan",
    "spartan_scaled_points",
)


def _is_blank(value) -> bool:
    if value is None:
        return True
    # NaN check without importing numpy/pandas
    if isinstance(value, float) and value != value:
        return True
    if isinstance(value, str) and not value.strip():
        return True
    return False


def normalize_mode(value, fallback: str = VOCAB_MODE) -> str:
    normalized = str(value or "").strip().lower()
    if normalized in _SENTENCE_MODE_ALIASES:
        return SENTENCE_MODE
    if normalized in _VOCAB_MODE_ALIASES:
        return VOCAB_MODE
    return fallback


def infer_mode(row: Dict, fallback: str = VOCAB_MODE) -> str:
    mode = normalize_mode(row.get("mode"), fallback="")
    if mode in {SENTENCE_MODE, VOCAB_MODE}:
        return mode

    for key in _SENTENCE_HINT_KEYS:
        value = row.get(key)
        if _is_blank(value):
            continue
        return SENTENCE_MODE
    for key in _VOCAB_HINT_KEYS:
        value = row.get(key)
        if _is_blank(value):
            continue
        return VOCAB_MODE
    return fallback


def normalize_score_row(row: Dict, fallback_mode: str = VOCAB_MODE) -> Dict:
    normalized = dict(row or {})
    normalized["mode"] = infer_mode(normalized, fallback=fallback_mode)
    return normalized


def iter_unique_score_rows(rows: Iterable[Dict]):
    seen_save_ids = set()
    for row in rows or []:
        if not isinstance(row, dict):
            continue
        save_id = str(row.get("save_id", "")).strip()
        if save_id:
            if save_id in seen_save_ids:
                continue
            seen_save_ids.add(save_id)
        yield row


def normalize_score_rows(rows: Iterable[Dict], fallback_mode: str = VOCAB_MODE) -> List[Dict]:
    return [
        normalize_score_row(row, fallback_mode=fallback_mode)
        for row in iter_unique_score_rows(rows)
    ]
