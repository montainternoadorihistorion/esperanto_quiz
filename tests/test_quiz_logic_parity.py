import json
import subprocess
import unittest
from pathlib import Path

from data_sources import VOCAB_CSV
from quiz_scoring import compute_result_summary, scale_spartan_points, score_for_correct
from vocab_grouping import _default_audio_key, build_groups


ROOT = Path(__file__).resolve().parents[1]


def run_node_json(source: str):
    result = subprocess.run(
        ["node", "--input-type=module", "-e", source],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return json.loads(result.stdout)


def group_summary(groups):
    return [
        {
            "id": group.id,
            "pos": group.pos,
            "stages": group.stages,
            "size": group.size,
            "entryIds": [entry.source_index for entry in group.entries],
        }
        for group in groups
    ]


class QuizLogicParityTest(unittest.TestCase):
    def test_mobile_vocab_groups_match_python(self):
        js_source = """
            import fs from "node:fs";
            import { buildVocabGroups } from "./mobile_app/quiz_core.mjs";

            const vocab = JSON.parse(fs.readFileSync("./mobile_app/data/vocab.json", "utf8"));
            const seeds = [1, 17, 8192];
            const result = {};
            for (const seed of seeds) {
              result[seed] = buildVocabGroups(vocab.entries, seed).map((group) => ({
                id: group.id,
                pos: group.pos,
                stages: group.stages,
                size: group.entries.length,
                entryIds: group.entries.map((entry) => entry.id),
              }));
            }
            console.log(JSON.stringify(result));
        """
        js_groups_by_seed = run_node_json(js_source)

        for seed in (1, 17, 8192):
            with self.subTest(seed=seed):
                py_groups = build_groups(VOCAB_CSV, seed=seed, audio_key_fn=_default_audio_key)
                self.assertEqual(js_groups_by_seed[str(seed)], group_summary(py_groups))

    def test_mobile_scoring_matches_python(self):
        score_cases = [
            {"question": {"mode": "vocab", "stages": ["beginner_1"]}, "streak": 1},
            {"question": {"mode": "vocab", "stages": ["intermediate_2"]}, "streak": 3},
            {"question": {"mode": "vocab", "stages": ["beginner_3", "advanced_1"]}, "streak": 4},
            {"question": {"mode": "sentence", "level": 5}, "streak": 1},
            {"question": {"mode": "sentence", "level": 12}, "streak": 5},
        ]
        summary_cases = [
            {"mode": "vocab", "total": 20, "correct": 17, "mainPoints": 211.5, "spartanScaledPoints": 14.0},
            {"mode": "sentence", "total": 12, "correct": 9, "mainPoints": 186.0, "spartanScaledPoints": 21.7},
            {"mode": "vocab", "total": 0, "correct": 0, "mainPoints": 0.0, "spartanScaledPoints": 0.0},
        ]

        js_source = f"""
            import {{ computeResultSummary, scaleSpartanPoints, scoreForCorrect }} from "./mobile_app/quiz_core.mjs";

            const scoreCases = {json.dumps(score_cases)};
            const summaryCases = {json.dumps(summary_cases)};
            const result = {{
              scores: scoreCases.map((item) => scoreForCorrect(item.question, item.streak)),
              summaries: summaryCases.map((item) => computeResultSummary({{
                questions: Array.from({{ length: item.total }}, (_, index) => index),
                correct: item.correct,
                mainPoints: item.mainPoints,
                spartanScaledPoints: item.spartanScaledPoints,
                settings: {{ mode: item.mode }},
              }})),
              spartanScaled: [0, 12.5, 99].map((points) => scaleSpartanPoints(points)),
            }};
            console.log(JSON.stringify(result));
        """
        js_result = run_node_json(js_source)

        expected_scores = [
            score_for_correct(
                mode=case["question"]["mode"],
                streak=case["streak"],
                stages=case["question"].get("stages"),
                level=case["question"].get("level"),
            )
            for case in score_cases
        ]
        for actual, expected in zip(js_result["scores"], expected_scores):
            self.assertAlmostEqual(actual, expected)

        expected_summaries = [
            compute_result_summary(
                mode=case["mode"],
                total=case["total"],
                correct=case["correct"],
                main_points=case["mainPoints"],
                spartan_scaled_points=case["spartanScaledPoints"],
            )
            for case in summary_cases
        ]
        for actual, expected in zip(js_result["summaries"], expected_summaries):
            self.assertEqual(actual["total"], expected["total"])
            self.assertEqual(actual["correct"], expected["correct"])
            self.assertAlmostEqual(actual["accuracy"], expected["accuracy"])
            self.assertAlmostEqual(actual["accuracyBonus"], expected["accuracyBonus"])
            self.assertAlmostEqual(actual["points"], expected["points"])

        for actual, raw_points in zip(js_result["spartanScaled"], [0, 12.5, 99]):
            self.assertAlmostEqual(actual, scale_spartan_points(raw_points))


if __name__ == "__main__":
    unittest.main()
