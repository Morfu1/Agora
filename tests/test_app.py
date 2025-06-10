import os
import sys
import unittest
import json

# Add the project root to the Python path to allow importing 'app'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

ORIGINAL_VIDEOS_JSON_PATH = 'videos.json'
BACKUP_VIDEOS_JSON_PATH = 'videos.json.bak'

class TestApp(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['DEBUG'] = False # Ensure debug is off for tests unless specifically testing debug features
        self.app = app.test_client()

        # Back up the original videos.json if it exists
        if os.path.exists(ORIGINAL_VIDEOS_JSON_PATH):
            os.rename(ORIGINAL_VIDEOS_JSON_PATH, BACKUP_VIDEOS_JSON_PATH)

    def tearDown(self):
        # Remove any videos.json created during a test
        if os.path.exists(ORIGINAL_VIDEOS_JSON_PATH):
            os.remove(ORIGINAL_VIDEOS_JSON_PATH)

        # Restore the original videos.json if it was backed up
        if os.path.exists(BACKUP_VIDEOS_JSON_PATH):
            os.rename(BACKUP_VIDEOS_JSON_PATH, ORIGINAL_VIDEOS_JSON_PATH)

    def test_index_loads_ok(self):
        """Test that the index page loads correctly with a generic title."""
        # Create a minimal dummy videos.json for this test to ensure the page renders the main structure
        # without hitting the "no videos found" case, unless that's what we want to test for page structure.
        # For just loading OK, an empty list is fine if the template handles it.
        sample_videos = []
        with open(ORIGINAL_VIDEOS_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(sample_videos, f)

        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Agora Meditations Videos", response.data) # From base template title or H1

    def test_no_videos_file(self):
        """Test how the index page behaves when videos.json is missing."""
        # Ensure videos.json does not exist (setUp handles backup, tearDown handles removal of test one)
        # If a previous test created one and tearDown failed, this ensures it's gone.
        if os.path.exists(ORIGINAL_VIDEOS_JSON_PATH):
            os.remove(ORIGINAL_VIDEOS_JSON_PATH)

        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        # This message is from templates/index.html {% else %} block
        self.assertIn(b"No videos found. Please make sure 'videos.json' exists and is correctly populated, then refresh.", response.data)

    def test_videos_are_displayed(self):
        """Test that videos from videos.json are correctly displayed on the index page."""
        sample_videos = [
            {
                'title': 'Test Video Alpha',
                'url': 'http://example.com/videoAlpha',
                'thumbnail_url': 'http://example.com/thumbAlpha.jpg',
                'description': 'Description for video Alpha.'
            },
            {
                'title': 'Test Video Beta',
                'url': 'http://example.com/videoBeta',
                'thumbnail_url': 'http://example.com/thumbBeta.jpg',
                'description': 'Description for video Beta.'
            }
        ]
        with open(ORIGINAL_VIDEOS_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(sample_videos, f)

        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

        # Check for content from the videos
        self.assertIn(b"Test Video Alpha", response.data)
        self.assertIn(b"http://example.com/videoAlpha", response.data)
        # Assuming description is displayed (it is, truncated)
        self.assertIn(b"Description for video Alpha", response.data)

        self.assertIn(b"Test Video Beta", response.data)
        self.assertIn(b"http://example.com/videoBeta", response.data)

        # Check for the video item class structure
        self.assertIn(b'class="video-item"', response.data)

        # Check for thumbnail presence (actual src)
        self.assertIn(b'src="http://example.com/thumbAlpha.jpg"', response.data)

if __name__ == '__main__':
    unittest.main()
