import json
from flask import Flask, render_template, abort
from blog_utils import get_all_blog_posts, get_post_by_slug

app = Flask(__name__)

# Video Gallery Route (existing)
@app.route('/')
def index():
    videos_data = []
    try:
        with open('videos.json', 'r', encoding='utf-8') as f:
            videos_data = json.load(f)
    except FileNotFoundError:
        print("Error: videos.json not found. Serving page with no videos.")
    except json.JSONDecodeError:
        print("Error: videos.json is corrupted or not valid JSON. Serving page with no videos.")

    return render_template('index.html', videos=videos_data)

# Blog Index Route
@app.route('/blog')
def blog_index():
    posts = get_all_blog_posts() # Fetches all posts, sorted by date by default
    # The template 'blog_index.html' will be created in a subsequent step.
    # For now, this will raise a TemplateNotFound error if accessed, which is expected.
    return render_template('blog_index.html', posts=posts)

# Single Blog Post Route
@app.route('/blog/<slug>')
def blog_post(slug):
    post = get_post_by_slug(slug)
    if post is None:
        abort(404) # Returns a 404 Not Found error if post doesn't exist
    # The template 'blog_post.html' will be created in a subsequent step.
    return render_template('blog_post.html', post=post)

if __name__ == '__main__':
    # Note: app.run() is suitable for development.
    # For production, a WSGI server like Gunicorn or uWSGI should be used.
    app.run(debug=True, host='0.0.0.0', port=8080)
