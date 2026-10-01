import io
import json
import tempfile
import unittest
from pathlib import Path
import sys
from unittest.mock import patch
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from social_influence.openrouter_media import (
    GenerationRecord,
    OpenRouterMediaClient,
    OpenRouterMediaError,
    load_records,
    write_records,
)


class OpenRouterMediaTests(unittest.TestCase):
    def test_non_json_http_error_preserves_status_and_body(self):
        error = HTTPError('https://openrouter.ai/api/v1/videos', 402, 'Payment Required', {}, io.BytesIO(b'quota exceeded'))
        with patch('social_influence.openrouter_media.urlopen', side_effect=error):
            with self.assertRaises(OpenRouterMediaError) as raised:
                OpenRouterMediaClient(api_key='test')._request('POST', '/videos', {})
        self.assertEqual(raised.exception.status_code, 402)
        self.assertEqual(raised.exception.body, 'quota exceeded')

    def test_invalid_success_body_is_not_reported_as_json_error(self):
        class Response:
            status = 200
            def read(self):
                return b'<html>upstream error</html>'
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False
        with patch('social_influence.openrouter_media.urlopen', return_value=Response()):
            with self.assertRaises(OpenRouterMediaError) as raised:
                OpenRouterMediaClient(api_key='test')._request('GET', '/videos/models')
        self.assertIn('upstream error', raised.exception.body)

    def test_video_submission_is_recorded_before_polling_and_resumes_by_job_id(self):
        client = OpenRouterMediaClient(api_key='test')
        calls = []
        submissions = []

        def submit_request(method, path, payload=None, *, raw=False, timeout=None):
            calls.append(('submit', method, path))
            if method == 'POST':
                return {'id': 'job-1', 'polling_url': 'https://openrouter.ai/api/v1/videos/job-1', 'status': 'pending'}
            if raw:
                return b'video'
            return {'id': 'job-1', 'status': 'completed', 'generation_id': 'gen-1', 'usage': {'cost': 0.1}}

        client._request = submit_request
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / 'video.mp4'
            record = client.submit_video(
                route='t2v/test',
                model='test/video',
                prompt='test',
                output_path=output,
                params={'duration': 4},
                poll_seconds=0,
                on_submit=lambda item: (submissions.append(item), calls.append(('recorded', item['job_id']))),
            )
        self.assertEqual(record.job_id, 'job-1')

        def resume_request(method, path, payload=None, *, raw=False, timeout=None):
            calls.append(('resume', method, path, raw))
            if path.endswith('/content?index=0'):
                return b'video'
            return {'id': 'job-1', 'status': 'completed', 'generation_id': 'gen-1', 'usage': {'cost': 0.1}}

        client._request = resume_request
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / 'resumed.mp4'
            resumed = client.complete_video_job(
                route='t2v/test',
                model='test/video',
                prompt='test',
                job_id=submissions[0]['job_id'],
                output_path=output,
                poll_seconds=0,
            )
        self.assertEqual(resumed.job_id, 'job-1')
        self.assertTrue(any(item[0] == 'recorded' for item in calls))
        self.assertFalse(any(item[0] == 'submit' and item[1] == 'POST' and item[2].endswith('/videos/job-1') for item in calls))

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
