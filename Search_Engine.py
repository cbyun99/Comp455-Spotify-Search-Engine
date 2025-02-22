import csv, os, time
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

CURRENT_DIR = os.path.dirname(__file__)
csv_data_path = os.path.join(CURRENT_DIR, 'spotify.csv')

# Load data from CSV
def load_data_from_csv(file_path):
    with open(file_path, newline='', encoding='latin-1') as csvfile:
        reader = csv.DictReader(csvfile)
        return [row for row in reader]

# Load data into memory
data = load_data_from_csv(csv_data_path)

# Home route
@app.route('/')
def home():
    return render_template('index.html')

# Search API
@app.route('/search', methods=['GET'])
def search():
    import time
    start_time = time.time()

    # Get query parameters
    query = request.args.get('query', '').lower()
    artist_name = request.args.get('artist', '').lower()
    released_year = request.args.get('year', '')        # Year
    scale = request.args.get('scale', '')               # Scale
    streams_min = request.args.get('streams_min', '')   # Minimum streams
    streams_max = request.args.get('streams_max', '')   # Maximum streams
    sort_by = request.args.get('sort_by', 'track_name')
    order = request.args.get('order', 'asc').lower()    # Ascending (default) or Descending

    # Split scale into key and mode
    if scale:
        scale_parts = scale.split()
        key_filter = scale_parts[0].replace('s','#')
        mode_filter = scale_parts[1]
    else:
        key_filter = mode_filter = None

    # Filter data
    results = [
        item for item in data
        if (query in item['track_name'].lower() or query in item['artist(s)_name'].lower())
        and (artist_name in item['artist(s)_name'].lower() if artist_name else True)
        and (item['released_year'] == released_year if released_year else True)
        and (item['key'] == key_filter if key_filter else True)
        and (item['mode'].lower() == mode_filter.lower() if mode_filter else True)
        and (int(item['streams']) >= int(streams_min) if streams_min else True)
        and (int(item['streams']) <= int(streams_max) if streams_max else True)
    ]

    # Sort data with reverse order
    reverse_order = order == 'desc'
    if sort_by == 'streams':
        results.sort(key=lambda x: int(x['streams']), reverse=reverse_order)
    elif sort_by == 'released_year':
        results.sort(key=lambda x: int(x['released_year']), reverse=reverse_order)
    else:  # Default to track_name
        results.sort(key=lambda x: x['track_name'].lower(), reverse=reverse_order)

    end_time = time.time()
    elapsed_time_ms = (end_time - start_time) * 1000

    # Return results and elapsed time
    return jsonify({
        "results": results,
        "elapsed_time_ms": elapsed_time_ms
    })



# Run the app
if __name__ == '__main__':
    app.run(debug=True)
