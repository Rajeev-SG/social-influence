import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from social_influence import cli


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.brand = self.root / 'brands' / 'example'
        self.brand.mkdir(parents=True)
        self.topic = 'First useful post'
        self.profile = '# Profile\n## Visual guidance\nDistinct composition\n## Evidence / QA\n- Validate claims.\n'
        (self.brand / 'profile.md').write_text(self.profile)
        (self.brand / 'queue.md').write_text('# Queue\n- [ ] First useful post\n- [ ] Second post\n')
        self.original = (self.brand / 'queue.md').read_bytes()
        (self.brand / 'evidence.txt').write_text('A source snapshot.')
        (self.brand / 'clip.mp4').write_bytes(b'UNIT TEST FIXTURE NOT A VIDEO')
        self.pack = {'topic': self.topic,
                     'sources': [{'url': 'https://example.org/evidence', 'file': 'evidence.txt',
                                  'sha256': cli.file_sha(self.brand / 'evidence.txt')}],
                     'evidence': {'Validate claims.': 'See source snapshot; review claim in final script.'},
                     'media': [{'file': 'clip.mp4', 'sha256': cli.file_sha(self.brand / 'clip.mp4'),
                                'rights': {'reviewStatus': 'owned', 'rightsStatus': 'owned', 'licenseName': 'Test only'}, 'kind': 'screen-recording'}]}
        self.pack_path = self.brand / 'posts' / (cli.post_id(self.topic) + '.json')
        self.save_pack()
        self.post = self.root / 'output/example' / cli.post_id(self.topic)
        self.calls = []

    def save_pack(self):
        cli.write_json(self.pack_path, self.pack)

    def fake_draft(self, cm, profile, topic, pack, sources, run):
        result = {key: 'Test ' + key for key in ('hook', 'script', 'pacing', 'caption', 'title', 'cta', 'first_frame')}
        result.update(shots=['approved clip'], hashtags=['#test'], source_record={'sources': sources})
        cli.write_json(run / 'production-brief.json', result)
        return result

    def fake_harness(self, cm, tool, request, run):
        self.calls.append((tool, request))
        if tool == 'generate-short':
            engine = run / 'engine'
            for name in ('video.mp4', 'captions.remotion.json', 'captions.srt', 'captions.ass'):
                path = engine / 'render' / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('UNIT TEST ONLY')
            for name in ('validate', 'score', 'provenance'):
                cli.write_json(engine / f'publish-prep/{name}.json', {'passed': True})
            cli.write_json(engine / 'provenance/asset-ledger.json', {'assets': [{'kind': 'visual-scene', 'localPath': str(next((run / 'media').iterdir())), 'reviewStatus': 'needs-review'}, {'kind': 'generated-script', 'reviewStatus': 'generated-local'}, {'kind': 'audio-stage-metadata', 'stage': 'script-to-audio', 'reviewStatus': 'generated-local'}]})
            cli.write_json(engine / 'quality-summary.json', {'ready': True})
            cli.write_json(engine / 'visuals/visuals.json', {
                'fallbacks': 0, 'scenes': [{'assetPath': str(next((run / 'media').iterdir()))}]})
        return {'passed': True}

    def invoke(self):
        with patch.object(cli, 'engine', return_value=self.root), \
             patch.object(cli, 'draft', side_effect=self.fake_draft), \
             patch.object(cli, 'harness', side_effect=self.fake_harness), \
             patch.object(cli, 'rebuild_locked_render', return_value=None):
            return cli.create(self.root, 'example')

    def pending_run(self):
        with self.assertRaisesRegex(cli.Blocked, 'awaits full playback'):
            self.invoke()
        self.assertEqual(self.original, (self.brand / 'queue.md').read_bytes())
        return self.post / cli.read_json(self.post / 'pending.json')['attempt']

    def approve(self, run):
        review = cli.read_json(run / 'review.required.json')
        review.update(passed=True, reviewer='Unit test reviewer (not a real render approval)')
        review['checks'] = {key: {'passed': True, 'notes': 'Unit-test fixture only.'} for key in cli.CHECKS}
        cli.write_json(run / 'review.json', review)

    def test_reviewed_success_resumes_without_regeneration(self):
        run = self.pending_run()
        self.approve(run)
        bundle = self.invoke()
        self.assertEqual(len(self.calls), 2)
        self.assertTrue((bundle / 'video.mp4').is_file())
        self.assertEqual((self.brand / 'queue.md').read_text(), '# Queue\n- [x] First useful post\n- [ ] Second post\n')
        handoff = cli.read_json(bundle / 'postiz-handoff.json')
        self.assertEqual(handoff['publish'], False)
        self.assertEqual(handoff['api_payload_template']['type'], 'draft')
        self.assertIn('${POSTIZ_MEDIA_ID}', handoff['api_payload_template']['posts'][0]['value'][0]['image'][0]['id'])
        self.assertEqual((run / 'profile.md').read_text(), self.profile)
        self.assertIn('Profile-derived visual brief', self.calls[0][1]['topic'])
        self.assertIn('PRE-APPROVED SCRIPT', self.calls[0][1]['topic'])
        self.assertEqual(self.calls[0][1]['visuals']['providers'], ['local'])
        self.assertTrue(self.calls[0][1]['publishPrep']['requirePass'])
        self.assertFalse(self.calls[0][1]['publishPrep']['enabled'])
        ledger = cli.read_json(run / 'engine/provenance/review-ledger.json')
        self.assertEqual(len(ledger['assets']), 3)
        self.assertEqual(ledger['assets'][0]['reviewStatus'], 'owned')
        self.assertEqual(ledger['assets'][1]['reviewStatus'], 'generated-local')
        self.assertEqual(ledger['assets'][2]['contentIdRisk'], 'none-known')
        self.assertEqual(cli.read_json(self.post / 'status.json')['status'], 'generated')

    def test_missing_pack_keeps_queue(self):
        self.pack_path.unlink()
        with self.assertRaisesRegex(cli.Blocked, 'Missing production pack'):
            self.invoke()
        self.assertEqual(self.original, (self.brand / 'queue.md').read_bytes())
        self.assertEqual(cli.read_json(self.post / 'status.json')['status'], 'blocked')

    def test_stale_video_rejected(self):
        run = self.pending_run()
        self.approve(run)
        (run / 'engine/render/video.mp4').write_text('changed')
        with self.assertRaisesRegex(cli.Blocked, 'stale'):
            self.invoke()
        self.assertEqual(self.original, (self.brand / 'queue.md').read_bytes())

    def test_stale_brief_rejected(self):
        run = self.pending_run()
        self.approve(run)
        brief = cli.read_json(run / 'production-brief.json')
        brief['caption'] = 'changed'
        cli.write_json(run / 'production-brief.json', brief)
        with self.assertRaisesRegex(cli.Blocked, 'stale'):
            self.invoke()

    def test_partial_review_rejected(self):
        run = self.pending_run()
        self.approve(run)
        review = cli.read_json(run / 'review.json')
        del review['checks']['visual_grammar']
        cli.write_json(run / 'review.json', review)
        with self.assertRaisesRegex(cli.Blocked, 'visual_grammar'):
            self.invoke()

    def test_string_true_is_not_approval(self):
        run = self.pending_run()
        self.approve(run)
        review = cli.read_json(run / 'review.json')
        review['passed'] = 'true'
        cli.write_json(run / 'review.json', review)
        with self.assertRaisesRegex(cli.Blocked, 'not passed'):
            self.invoke()

    def test_machine_qa_failed_or_missing_never_finalizes(self):
        for value in (False, None, 'true'):
            with self.subTest(value=value):
                run = self.pending_run()
                self.approve(run)
                path = run / 'engine/publish-prep/validate.json'
                cli.write_json(path, {'passed': value})
                with self.assertRaisesRegex(cli.Blocked, 'Required QA'):
                    self.invoke()
                self.assertEqual(self.original, (self.brand / 'queue.md').read_bytes())
                cli.write_json(path, {'passed': True})
                (run / 'review.json').unlink()

    def test_stock_fallback_rejected(self):
        run = self.pending_run()
        cli.write_json(run / 'engine/visuals/visuals.json', {'fallbacks': 1})
        with self.assertRaisesRegex(cli.Blocked, 'fallback'):
            self.invoke()

    def test_unapproved_media_rejected(self):
        run = self.pending_run()
        cli.write_json(run / 'engine/visuals/visuals.json', {
            'fallbacks': 0, 'scenes': [{'assetPath': '/tmp/unrelated.mp4'}]})
        with self.assertRaisesRegex(cli.Blocked, 'approved local'):
            self.invoke()

    def test_missing_caption_rejected(self):
        run = self.pending_run()
        (run / 'engine/render/captions.srt').unlink()
        with self.assertRaisesRegex(cli.Blocked, 'Missing render artifact'):
            self.invoke()

    def test_unknown_quality_rejected(self):
        run = self.pending_run()
        cli.write_json(run / 'engine/quality-summary.json', {'ready': None})
        with self.assertRaisesRegex(cli.Blocked, 'readiness'):
            self.invoke()

    def test_failed_engine_does_not_advance_queue(self):
        with patch.object(cli, 'engine', return_value=self.root), \
             patch.object(cli, 'draft', side_effect=self.fake_draft), \
             patch.object(cli, 'harness', side_effect=cli.Blocked('render failed')), \
             patch.object(cli, 'rebuild_locked_render', return_value=None):
            with self.assertRaisesRegex(cli.Blocked, 'render failed'):
                cli.create(self.root, 'example')
        self.assertEqual(self.original, (self.brand / 'queue.md').read_bytes())
        self.assertFalse((self.post / 'pending.json').exists())

    def test_evidence_coverage_required(self):
        self.pack['evidence'] = {}
        self.save_pack()
        with self.assertRaisesRegex(cli.Blocked, 'Every profile'):
            self.invoke()

    def test_media_hash_required(self):
        (self.brand / 'clip.mp4').write_text('different')
        with self.assertRaisesRegex(cli.Blocked, 'Media has changed'):
            self.invoke()

    def test_source_hash_required(self):
        (self.brand / 'evidence.txt').write_text('different')
        with self.assertRaisesRegex(cli.Blocked, 'Source snapshot'):
            self.invoke()

    def test_topic_binding(self):
        self.pack['topic'] = 'Other'
        self.save_pack()
        with self.assertRaisesRegex(cli.Blocked, 'topic does not match'):
            self.invoke()

    def test_nutrient_arithmetic(self):
        self.pack['calculations'] = [{'name': 'protein', 'terms': [{'grams': 200, 'per100g': 5}], 'claimed': 40}]
        self.save_pack()
        with self.assertRaisesRegex(cli.Blocked, 'Calculation mismatch'):
            self.invoke()
        self.pack['calculations'][0]['claimed'] = 10
        self.save_pack()
        cli.production_pack(self.brand, self.topic, self.profile)

    def test_path_traversal(self):
        self.pack['media'][0]['file'] = '../secret.mp4'
        self.save_pack()
        with self.assertRaisesRegex(cli.Blocked, 'leaves brand'):
            self.invoke()
        for brand in ('../example', '/tmp', 'a/b'):
            with self.assertRaisesRegex(cli.Blocked, 'Invalid brand'):
                cli.create(self.root, brand)

    def test_harness_tolerates_banner_before_json(self):
        class Run:
            returncode = 0
            stdout = "Downloading Chrome Headless Shell\n{\"ok\":true,\"result\":{\"x\":1}}"
        with patch("subprocess.run", return_value=Run()):
            self.assertEqual(cli.harness(Path("cm"), "t", {}, Path("/tmp/run"))["x"], 1)

    def test_lock(self):
        with cli.brand_lock(self.brand / '.create.lock'):
            with self.assertRaisesRegex(cli.Blocked, 'active create'):
                self.invoke()

    def test_queue_order_and_crlf(self):
        queue = '- [x] Done\r\n- [ ] First\r\n- [ ] Second\r\n'
        self.assertEqual(cli.next_item(queue), (1, 'First'))
        with self.assertRaisesRegex(cli.Blocked, 'No unused'):
            cli.next_item('- [x] Done\n')

    def test_shared_interface_distinct_profiles(self):
        for style in ('real food footage and moving fibre counters', 'desktop recording and INPUT → AI STEP → HUMAN CHECK'):
            with self.subTest(style=style):
                profile = self.profile + '\n## Visual guidance\n' + style
                (self.brand / 'profile.md').write_text(profile)
                run = self.pending_run()
                self.assertEqual((run / 'profile.md').read_text(), profile)
                self.assertIn('Profile-derived visual brief', self.calls[-2][1]['topic'])


if __name__ == '__main__':
    unittest.main()
