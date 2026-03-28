"""가이드 서비스 테스트"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.guide_service import STAGE_GUIDES, get_guide, get_all_stages


class TestGuideService(unittest.TestCase):
    def test_all_stages_have_guides(self):
        """SWE.1~SWE.6 모든 단계에 가이드 존재 확인"""
        for swe in ["SWE.1", "SWE.2", "SWE.3", "SWE.4", "SWE.5", "SWE.6"]:
            self.assertIn(swe, STAGE_GUIDES, f"Missing guide for {swe}")
            self.assertIn("ko", STAGE_GUIDES[swe], f"Missing Korean guide for {swe}")
            self.assertIn("en", STAGE_GUIDES[swe], f"Missing English guide for {swe}")

    def test_guide_content_not_empty(self):
        """가이드 내용이 비어있지 않은지 확인"""
        required_fields = ["title", "what", "why", "documents", "tips", "next_step", "v_model_pair"]
        for swe in STAGE_GUIDES:
            for lang in ["ko", "en"]:
                guide = STAGE_GUIDES[swe][lang]
                for field in required_fields:
                    self.assertIn(field, guide, f"Missing field '{field}' in {swe}/{lang}")
                    value = guide[field]
                    if isinstance(value, str):
                        self.assertTrue(len(value) > 0, f"Empty '{field}' in {swe}/{lang}")
                    elif isinstance(value, list):
                        self.assertTrue(len(value) > 0, f"Empty list '{field}' in {swe}/{lang}")

    def test_get_guide_function(self):
        """get_guide 함수 테스트"""
        guide = get_guide("SWE.1", "ko")
        self.assertEqual(guide["title"], "소프트웨어 요구사항 분석")

        guide_en = get_guide("SWE.1", "en")
        self.assertEqual(guide_en["title"], "Software Requirements Analysis")

        # 존재하지 않는 단계
        empty = get_guide("SWE.99", "ko")
        self.assertEqual(empty, {})

    def test_get_all_stages(self):
        """get_all_stages 함수 테스트"""
        stages = get_all_stages()
        self.assertEqual(len(stages), 6)
        self.assertIn("SWE.1", stages)
        self.assertIn("SWE.6", stages)

    def test_vmodel_pairs_in_guides(self):
        """가이드에 V-model 쌍 정보가 포함되어 있는지 확인"""
        pairs = {"SWE.1": "SWE.6", "SWE.2": "SWE.5", "SWE.3": "SWE.4",
                 "SWE.4": "SWE.3", "SWE.5": "SWE.2", "SWE.6": "SWE.1"}
        for swe, pair in pairs.items():
            guide = STAGE_GUIDES[swe]["ko"]
            self.assertIn(pair, guide["v_model_pair"],
                         f"{swe} guide should reference {pair} as V-model pair")


if __name__ == "__main__":
    unittest.main()
