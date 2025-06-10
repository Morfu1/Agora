import os
import sys
import unittest
import json
import shutil # For rmtree

# Add the project root to the Python path to allow importing 'app'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
# We also need to be able to call blog_utils directly for setting up test data
from blog_utils import get_post_slug # Example, though not directly used in app tests usually

# --- Constants for videos.json testing ---
ORIGINAL_VIDEOS_JSON_PATH = 'videos.json'
BACKUP_VIDEOS_JSON_PATH = 'videos.json.bak'

# --- Constants for blog testing ---
ORIGINAL_BLOG_POSTS_DIR = 'blog_posts' # The actual dir app uses
BACKUP_BLOG_POSTS_DIR = 'blog_posts.bak' # Backup of actual dir
TEST_BLOG_POSTS_DIR_TEMP = 'test_blog_posts_for_test_app' # Temp dir for test file creation

TEST_POST_FILENAME = 'test-sample-post.md'
TEST_POST_SLUG = 'test-sample-post'
TEST_POST_FRONTMATTER = f"""---
title: "A Test Blog Post Title"
date: "November 01, 2023"
author: "Test Author Name"
featuredImage: "https://example.com/test-image.jpg"
categories: [TestCategory, Sample]
tags: ["testing", "example-tag"]
metaDescription: "This is a meta description for the test blog post."
---
"""
TEST_POST_MARKDOWN_CONTENT = f"""
# A Test Blog Post Title

This is the main content of the *test blog post*.

## Test Heading for ToC
Some details under the test heading.
"""
FULL_TEST_POST_CONTENT = TEST_POST_FRONTMATTER + TEST_POST_MARKDOWN_CONTENT


class TestApp(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        self.app = app.test_client()

        # 1. Handle videos.json backup
        if os.path.exists(ORIGINAL_VIDEOS_JSON_PATH):
            os.rename(ORIGINAL_VIDEOS_JSON_PATH, BACKUP_VIDEOS_JSON_PATH)

        # 2. Handle blog_posts directory backup and test setup
        # Back up the original blog_posts directory if it exists
        if os.path.exists(ORIGINAL_BLOG_POSTS_DIR):
            os.rename(ORIGINAL_BLOG_POSTS_DIR, BACKUP_BLOG_POSTS_DIR)

        # Create a temporary clean 'blog_posts' directory for app to use
        # This ensures app always starts with a known state for blog posts (empty)
        if os.path.exists(TEST_BLOG_POSTS_DIR_TEMP): # Clean up from previous failed test
            shutil.rmtree(TEST_BLOG_POSTS_DIR_TEMP)
        os.makedirs(TEST_BLOG_POSTS_DIR_TEMP) # This is where we'll stage test files
        # For tests that need the app to see posts, we'll copy/move from here to ORIGINAL_BLOG_POSTS_DIR

    def tearDown(self):
        # 1. Restore videos.json
        if os.path.exists(ORIGINAL_VIDEOS_JSON_PATH): # If test created one
            os.remove(ORIGINAL_VIDEOS_JSON_PATH)
        if os.path.exists(BACKUP_VIDEOS_JSON_PATH):
            os.rename(BACKUP_VIDEOS_JSON_PATH, ORIGINAL_VIDEOS_JSON_PATH)

        # 2. Restore blog_posts directory
        # Remove the 'blog_posts' dir that might have been created by tests or was TEST_BLOG_POSTS_DIR_TEMP renamed
        if os.path.exists(ORIGINAL_BLOG_POSTS_DIR):
            shutil.rmtree(ORIGINAL_BLOG_POSTS_DIR) # Remove the one app used

        # Clean up the staging directory
        if os.path.exists(TEST_BLOG_POSTS_DIR_TEMP):
            shutil.rmtree(TEST_BLOG_POSTS_DIR_TEMP)

        # Restore the original blog_posts directory if it was backed up
        if os.path.exists(BACKUP_BLOG_POSTS_DIR):
            os.rename(BACKUP_BLOG_POSTS_DIR, ORIGINAL_BLOG_POSTS_DIR)

    def _create_test_blog_file(self, filename=TEST_POST_FILENAME, content=FULL_TEST_POST_CONTENT, target_dir=TEST_BLOG_POSTS_DIR_TEMP):
        """Helper to create a test blog post file in a specified directory."""
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        file_path = os.path.join(target_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return file_path

    def _setup_app_blog_posts_dir_with_test_file(self):
        """Moves the test blog content into the directory the app uses."""
        # Ensure the app's blog_posts dir is clean first
        if os.path.exists(ORIGINAL_BLOG_POSTS_DIR):
            shutil.rmtree(ORIGINAL_BLOG_POSTS_DIR)
        # Create the test file in the temp staging dir
        self._create_test_blog_file()
        # Rename the temp staging dir to what the app expects
        os.rename(TEST_BLOG_POSTS_DIR_TEMP, ORIGINAL_BLOG_POSTS_DIR)


    # --- Video Tests (Existing) ---
    def test_index_loads_ok(self):
        sample_videos = []
        with open(ORIGINAL_VIDEOS_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(sample_videos, f)
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Agora Meditations Videos", response.data)

    def test_no_videos_file(self):
        if os.path.exists(ORIGINAL_VIDEOS_JSON_PATH):
            os.remove(ORIGINAL_VIDEOS_JSON_PATH)
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"No videos found", response.data)

    def test_videos_are_displayed(self):
        sample_videos = [{'title': 'Test Video Alpha', 'url': 'http://example.com/videoAlpha', 'thumbnail_url': 'http://example.com/thumbAlpha.jpg', 'description': 'Description for video Alpha.'}]
        with open(ORIGINAL_VIDEOS_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(sample_videos, f)
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Test Video Alpha", response.data)
        self.assertIn(b"http://example.com/videoAlpha", response.data)
        self.assertIn(b'class="video-item"', response.data)
        self.assertIn(b'src="http://example.com/thumbAlpha.jpg"', response.data)

    # --- Blog Tests (New) ---
    def test_blog_index_loads_ok(self):
        """Test /blog loads with its title."""
        # It's okay if there are no posts, the page should still load.
        # The setUp ensures ORIGINAL_BLOG_POSTS_DIR is initially empty for the app.
        # For this test, we rename TEST_BLOG_POSTS_DIR_TEMP (empty) to ORIGINAL_BLOG_POSTS_DIR
        os.rename(TEST_BLOG_POSTS_DIR_TEMP, ORIGINAL_BLOG_POSTS_DIR)

        response = self.app.get('/blog')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Agora Meditations Blog", response.data) # From blog_index.html <title> or <h1>

    def test_blog_index_shows_posts(self):
        """Test /blog shows posts when they exist."""
        self._setup_app_blog_posts_dir_with_test_file() # Creates and renames dir

        response = self.app.get('/blog')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"A Test Blog Post Title", response.data)
        self.assertIn(f'href="/blog/{TEST_POST_SLUG}"'.encode('utf-8'), response.data)

    def test_blog_index_no_posts(self):
        """Test /blog shows 'No posts' message when directory is empty."""
        # setUp creates an empty TEST_BLOG_POSTS_DIR_TEMP. Rename it to what app uses.
        os.rename(TEST_BLOG_POSTS_DIR_TEMP, ORIGINAL_BLOG_POSTS_DIR)

        response = self.app.get('/blog')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"No blog posts yet. Stay tuned!", response.data) # From blog_index.html

    def test_single_blog_post_loads_ok(self):
        """Test /blog/<slug> loads a specific post."""
        self._setup_app_blog_posts_dir_with_test_file()

        response = self.app.get(f'/blog/{TEST_POST_SLUG}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"A Test Blog Post Title", response.data) # Title in body/header
        self.assertIn(b"This is the main content of the <em>test blog post</em>.", response.data) # Check for HTML output
        self.assertIn(b"Test Author Name", response.data) # Author metadata
        self.assertIn(b"Table of Contents", response.data) # ToC section
        self.assertIn(b'href="#test-heading-for-toc"', response.data) # A link from ToC

    def test_single_blog_post_404_for_invalid_slug(self):
        """Test /blog/<slug> returns 404 for a non-existent post."""
        # Ensure no posts exist in the app's view
        os.rename(TEST_BLOG_POSTS_DIR_TEMP, ORIGINAL_BLOG_POSTS_DIR)

        response = self.app.get('/blog/non-existent-slug-here')
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()
