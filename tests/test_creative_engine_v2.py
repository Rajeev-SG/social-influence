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

    def test_asset_routes_are_replaceable_and_execution_is_explicit(self):
        for route in self.engine.stage_c():
            self.assertTrue(route['replaceable'])
            self.assertIn(route['route'], {'stock', 'image-generation', 'image-to-video', 'text-to-video', 'code-generated'})
            self.assertIn(route['execution_status'], {'executed-local', 'executed-provider', 'planned-not-executed'})
            if route['route'] == 'code-generated':
                self.assertEqual(route['execution_status'], 'executed-local')
            else:
                self.assertEqual(route['execution_status'], 'planned-not-executed')

    def test_committed_projections_match_single_manifest_source(self):
        out = ROOT / 'brands/gutkitchen/creative-engine-v2/candidates'
        projected = json.loads((out / 'manifest.json').read_text())
        projection = projected.pop('_projection')
        self.assertEqual(projected, json.loads((ROOT / 'brands/gutkitchen/creative-engine-v2/manifest.json').read_text()))
        self.assertEqual(projection['decisionScope'], 'copy-and-structure-only')
        self.assertEqual(projection['visualQualityValidation'], 'not-performed')
        self.assertEqual(json.loads((out / 'review-payload.json').read_text()), json.loads(json.dumps(self.engine.static_review_payload(), sort_keys=True)))
        self.assertEqual(json.loads((out / 'stage-output.json').read_text()), json.loads(json.dumps(self.engine.run_stages(), sort_keys=True)))

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
        for label in ('OLD BASELINE', 'CURRENT V2 STORYBOARD', 'NEW A', 'NEW B', 'NEW C', 'FINAL MEDIA', 'Mark as winner', 'Local review notes', 'ref-05-action'):
            self.assertIn(label, page)

    def test_finished_openrouter_media_has_zero_planned_critical_routes(self):
        path = ROOT / 'brands/gutkitchen/creative-engine-v2/candidates/final-media/final-media-manifest.json'
        manifest = json.loads(path.read_text())
        self.assertTrue(manifest['openRouterOnly'])
        self.assertEqual(manifest['candidateCount'], 3)
        self.assertEqual(manifest['plannedCriticalRoutes'], 0)
        self.assertEqual(manifest['experiment']['issueTargetDurationSeconds'], [8, 15])
        self.assertEqual([item['id'] for item in manifest['candidates']], ['new-a', 'new-b', 'new-c'])
        for candidate in manifest['candidates']:
            self.assertGreaterEqual(candidate['duration'], 8.0)
            self.assertLessEqual(candidate['duration'], 15.0)
            self.assertTrue((ROOT / candidate['video'].removeprefix('../../')).is_file())
            self.assertTrue((ROOT / candidate['firstFrame'].removeprefix('../../')).is_file())
            self.assertTrue((ROOT / candidate['filmstrip'].removeprefix('../../')).is_file())
            for shot in candidate['shots']:
                self.assertEqual(shot['executionStatus'], 'executed-provider')
                self.assertNotEqual(shot['route'], 'planned-not-executed')
                self.assertFalse(shot['fallback'])
                self.assertTrue(shot['model'])
            self.assertEqual(
                candidate['qa']['routeComposition'],
                {'new-a': {'i2v': 6, 't2v': 0, 'fallback': 0}, 'new-b': {'i2v': 0, 't2v': 6, 'fallback': 0}, 'new-c': {'i2v': 3, 't2v': 3, 'fallback': 0}}[candidate['id']],
            )
        self.assertEqual(manifest['candidateOverlap']['new-a:new-b'], [])
        review_data = (ROOT / 'brands/gutkitchen/creative-engine-v2/candidates/final-media/review-data.json').read_text()
        self.assertNotIn('tiktok.com', review_data)
        self.assertNotIn('sourceUrl', review_data)

    def test_reference_library_is_self_contained(self):
        library = json.loads((ROOT / 'brands/gutkitchen/references/library.json').read_text())
        self.assertIn('No committable creator frames are expected to exist', library['capturePolicy'])
        for item in library['references'] + library['searchEvidence']:
            self.assertNotIn('capture', item)
            self.assertNotIn('capturePath', item)
        self.assertFalse((ROOT / 'brands/gutkitchen/references/frames').exists())

    def test_generation_date_matches_evidence_directory(self):
        self.assertEqual(self.engine.manifest.provenance['generated_at'], '2026-09-30')
        verification = json.loads((ROOT / 'docs/evidence/2026-09-30/creative-engine-v2/verification.json').read_text())
        self.assertEqual(verification['generatedAtUtc'][:10], self.engine.manifest.provenance['generated_at'])


if __name__ == '__main__':
    unittest.main()
