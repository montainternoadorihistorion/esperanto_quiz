import unittest
from unittest.mock import call, patch

import score_sync_service


class ScoreSyncServiceTests(unittest.TestCase):
    @patch.object(score_sync_service, "upsert_user_total", return_value=True)
    def test_update_sentence_user_stats_updates_sentence_sheet_only(self, upsert_user_total):
        result = score_sync_service.update_sentence_user_stats(
            user="MontaInterno",
            last_updated="2026-06-06T00:00:00Z",
            totals={"overall": 120.0, "vocab": 80.0, "sentence": 40.0},
        )

        self.assertTrue(result)
        upsert_user_total.assert_called_once_with(
            score_sync_service.USER_STATS_SENTENCE_SHEET,
            user="MontaInterno",
            total_points=40.0,
            last_updated="2026-06-06T00:00:00Z",
            retries=score_sync_service.SCORE_WRITE_RETRIES,
            retry_base_sec=score_sync_service.SCORE_WRITE_RETRY_BASE_SEC,
        )

    @patch.object(score_sync_service, "load_score_totals_for_user")
    @patch.object(score_sync_service, "upsert_user_total", return_value=True)
    def test_update_totals_for_sentence_record_updates_overall_and_sentence(
        self,
        upsert_user_total,
        load_score_totals_for_user,
    ):
        load_score_totals_for_user.return_value = {"overall": 120.0, "vocab": 80.0, "sentence": 40.0}

        result = score_sync_service.update_totals_for_record(
            {"user": "MontaInterno", "mode": "sentence", "ts": "2026-06-06T00:00:00Z"}
        )

        self.assertEqual(result, (True, True))
        self.assertEqual(
            upsert_user_total.call_args_list,
            [
                call(
                    score_sync_service.USER_STATS_SHEET,
                    user="MontaInterno",
                    total_points=120.0,
                    last_updated="2026-06-06T00:00:00Z",
                    retries=score_sync_service.SCORE_WRITE_RETRIES,
                    retry_base_sec=score_sync_service.SCORE_WRITE_RETRY_BASE_SEC,
                ),
                call(
                    score_sync_service.USER_STATS_SENTENCE_SHEET,
                    user="MontaInterno",
                    total_points=40.0,
                    last_updated="2026-06-06T00:00:00Z",
                    retries=score_sync_service.SCORE_WRITE_RETRIES,
                    retry_base_sec=score_sync_service.SCORE_WRITE_RETRY_BASE_SEC,
                ),
            ],
        )

    @patch.object(score_sync_service, "load_score_totals_for_user")
    @patch.object(score_sync_service, "upsert_user_total", return_value=True)
    def test_update_totals_for_vocab_record_updates_overall_only(
        self,
        upsert_user_total,
        load_score_totals_for_user,
    ):
        load_score_totals_for_user.return_value = {"overall": 120.0, "vocab": 80.0, "sentence": 40.0}

        result = score_sync_service.update_totals_for_record(
            {"user": "MontaInterno", "mode": "vocab", "ts": "2026-06-06T00:00:00Z"}
        )

        self.assertEqual(result, (True, True))
        upsert_user_total.assert_called_once_with(
            score_sync_service.USER_STATS_SHEET,
            user="MontaInterno",
            total_points=120.0,
            last_updated="2026-06-06T00:00:00Z",
            retries=score_sync_service.SCORE_WRITE_RETRIES,
            retry_base_sec=score_sync_service.SCORE_WRITE_RETRY_BASE_SEC,
        )


if __name__ == "__main__":
    unittest.main()
