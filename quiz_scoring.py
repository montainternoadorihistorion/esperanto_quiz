BASE_POINTS = 10
STREAK_BONUS = 0.5
VOCAB_STAGE_FACTORS = {
    "beginner": 1.0,
    "intermediate": 1.3,
    "advanced": 1.6,
}
SENTENCE_SCORE_SCALE = 2.0 / 1.5
SENTENCE_STREAK_SCALE = 2.0
VOCAB_ACCURACY_BONUS = 5.0
SENTENCE_ACCURACY_BONUS = 10.0
SPARTAN_SCORE_MULTIPLIER = 0.7


def get_stage_factor(stages) -> float:
    labels = [str(stage) for stage in (stages or [])]
    if any("advanced" in label for label in labels):
        return VOCAB_STAGE_FACTORS["advanced"]
    if any("intermediate" in label for label in labels):
        return VOCAB_STAGE_FACTORS["intermediate"]
    return VOCAB_STAGE_FACTORS["beginner"]


def score_for_correct(*, mode: str, streak: int, stages=None, level=None) -> float:
    streak_count = max(0, int(streak) - 1)
    if mode == "sentence":
        return sentence_base_points_for_level(level) + streak_count * STREAK_BONUS * SENTENCE_STREAK_SCALE
    return BASE_POINTS * get_stage_factor(stages) + streak_count * STREAK_BONUS


def sentence_base_points_for_level(level) -> float:
    return (float(level) + 11.5) * SENTENCE_SCORE_SCALE


def scale_spartan_points(points) -> float:
    return float(points) * SPARTAN_SCORE_MULTIPLIER


def compute_result_summary(
    *,
    mode: str,
    total: int,
    correct: int,
    main_points: float,
    spartan_scaled_points: float,
) -> dict:
    accuracy = correct / total if total else 0
    accuracy_bonus_per_question = SENTENCE_ACCURACY_BONUS if mode == "sentence" else VOCAB_ACCURACY_BONUS
    accuracy_bonus = accuracy * total * accuracy_bonus_per_question
    points = main_points + spartan_scaled_points + accuracy_bonus
    return {
        "total": total,
        "correct": correct,
        "accuracy": accuracy,
        "accuracyBonus": accuracy_bonus,
        "points": points,
    }
