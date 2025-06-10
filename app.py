import json
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    videos_data = []
    try:
        with open('videos.json', 'r', encoding='utf-8') as f:
            videos_data = json.load(f)
    except FileNotFoundError:
        print("Error: videos.json not found. Serving page with no videos.")
        # Optionally, you could pass an error message to the template
        # videos_data = [] # Already initialized
    except json.JSONDecodeError:
        print("Error: videos.json is corrupted or not valid JSON. Serving page with no videos.")
        # videos_data = [] # Already initialized

    return render_template('index.html', videos=videos_data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
