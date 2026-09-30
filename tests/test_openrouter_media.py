import json
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from social_influence.openrouter_media import (
    GenerationRecord,
    OpenRouterMediaClient,
    load_records,
    write_records,
)


class OpenRouterMediaTests(unittest.TestCase):
    def test_reference_data_urls_are_redacted_from_provenance(self):
        with tempfile.TemporaryDirectory() as temp:
            image = Path(temp) / 'reference.png'
            image.write_bytes(b'reference-bytes')
            payload = {
                'model': 'test/video',
                'frame_images': [
                    {
                        'type': 'image_url',
                        'image_url': {'url': OpenRouterMediaClient.data_url(image)},
                        'frame_type': 'first_frame',
                    }
                ],
            }
            redacted = OpenRouterMediaClient._redacted_request(payload, [image])
            serialized = json.dumps(redacted)
            self.assertNotIn('data:image/png;base64', serialized)
            self.assertIn('sha256:', serialized)
            self.assertEqual(redacted['frame_images'][0]['frame_type'], 'first_frame')

    def test_generation_records_are_deduplicated_by_route_output_and_start(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / 'output.mp4'
            output.write_bytes(b'video')
            record = GenerationRecord(
                route='i2v/test',
                model='test/video',
                prompt='test',
                request={},
                input_references=[],
                output_path=str(output),
                output_sha256='hash',
                started_at='2026-09-30T00:00:00Z',
                completed_at='2026-09-30T00:00:01Z',
                elapsed_seconds=1,
                job_id='job-1',
                generation_id='gen-1',
                provider=None,
                usage={'cost': 0.1},
                attempts=[],
            )
            ledger = Path(temp) / 'generations.json'
            write_records([record, record], ledger)
            self.assertEqual(len(load_records(ledger)), 1)


if __name__ == '__main__':
    unittest.main()
