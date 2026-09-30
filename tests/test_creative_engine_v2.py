import json
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from social_influence.creative_engine_v2 import CreativeEngineV2
from social_influence.creative_engine_v2.pipeline import FORBIDDEN_CREATIVE_COPY, QAStatus


class CreativeEngineV2Tests(unittest.TestCase):
    def setUp(self):
        self.engine = CreativeEngineV2.from_path(ROOT / 'brands/gutkitchen/creative-engine-v2/manifest.json')

    def test_stages_are_explicit_and_three_treatments_exist(self):
        stages = self.engine.run_stages()
        self.assertEqual(len(self.engine.manifest.treatments), 3)
        self.assertEqual(
            list(stages),
            ['stage_a_creative_direction', 'stage_b_reference_art_direction', 'stage_c_asset_routing',
             'stage_d_deterministic_design', 'stage_e_candidate_generation', 'stage_f_qa'],
        )
        self.assertGreaterEqual(stages['stage_a_creative_direction']['angle_count'], 10)
        self.assertEqual(len(stages['stage_c_asset_routing']), 30)

    def test_reference_inputs_are_recorded_per_treatment(self):
        payload = self.engine.static_review_payload()
        refs = [ref for item in payload['treatments'] for ref in item['references']]
        self.assertGreaterEqual(len(refs), 3)
        self.assertTrue((ROOT / self.engine.manifest.reference_library).is_file())
        self.assertTrue((ROOT / self.engine.manifest.visual_grammar).is_file())

    def test_asset_routes_are_replaceable_per_shot(self):
        for route in self.engine.stage_c():
            self.assertTrue(route['replaceable'])
            self.assertIn(route['route'], {'stock', 'image-generation', 'image-to-video', 'text-to-video', 'code-generated'})

    def test_no_redundant_ai_branding_in_new_storyboards(self):
        payload = self.engine.static_review_payload()
        for treatment in payload['treatments']:
            copy = json.dumps(treatment).lower()
            for phrase in FORBIDDEN_CREATIVE_COPY:
                self.assertNotIn(phrase, copy)

    def test_qa_is_not_creative_selection(self):
        qa = QAStatus(facts=True, evidence=True, technical=True, caption_safe_region=True)
        self.assertTrue(qa.passed)
        self.assertEqual(self.engine.stage_f()['passed'], True)

    def test_materially_different_lanes(self):
        names = [t.name for t in self.engine.manifest.treatments]
        self.assertEqual(names, ['Quantified Recipe Build', 'Fibre Calculator / Counter', 'Tactile Editorial Food-Build'])
        stacks = [tuple(t.design_stack) for t in self.engine.manifest.treatments]
        self.assertEqual(len(set(stacks)), 3)

    def test_generated_stills_exist_for_every_candidate(self):
        out = ROOT / 'brands/gutkitchen/creative-engine-v2/candidates'
        for treatment in ('new-a', 'new-b', 'new-c'):
            for index in range(1, 11):
                self.assertTrue((out / f'{treatment}-frame-{index:02d}.jpg').is_file())
                self.assertTrue((out / f'{treatment}-preview.mp4').is_file())

    def test_review_page_mentions_baseline_and_all_new_lanes(self):
        page = (ROOT / 'reviews/gutkitchen-creative-v2/index.html').read_text()
        for label in ('OLD / BASELINE', 'NEW A', 'NEW B', 'NEW C', 'references/library.json', 'visual-grammar-v2.md'):
            self.assertIn(label, page)


if __name__ == '__main__':
    unittest.main()
