from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/brave_search": {"origins": "*"}})

@app.route('/brave_search', methods=['OPTIONS', 'POST'])
def brave_search():
    # Handle CORS preflight request
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response

    try:
        # Ensure JSON data is provided
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        # Validate required parameters
        api_key = data.get('braveSearchAPIKey')
        query = data.get('q')
        
        if not api_key:
            return jsonify({'error': 'Brave Search API Key is required'}), 400
        if not query:
            return jsonify({'error': 'Search query is required'}), 400

        # Construct API URL with careful parameter handling
        params = {
            'q': query,
        }
        if data.get('offset') and data.get('offset') != "":
            params['offset'] = data.get('offset')
        if data.get('freshness') and data.get('freshness') != "":
            params['freshness'] = data.get('freshness')
        if data.get('result_filter') and data.get('result_filter') != "":
            params['result_filter'] = data.get('result_filter')
        if data.get('country') and data.get('country') != "":
            params['country'] = data.get('country')
        if data.get('searchLang') and data.get('searchLang') != "":
            params['search_lang'] = data.get('searchLang')
        if data.get('uiLang') and data.get('uiLang') != "":
            params['ui_lang'] = data.get('uiLang')
        if data.get('count') and data.get('count') != "":
            params['count'] = data.get('count')
        if data.get('safesearch') and data.get('safesearch') != "":
            params['safesearch'] = data.get('safesearch')
        if data.get('gogglesId') and data.get('gogglesId') != "":
            params['goggles_id'] = data.get('gogglesId')
        if data.get('units') and data.get('units') != "":
            params['units'] = data.get('units')


        # Construct API URL
        api_url = 'https://api.search.brave.com/res/v1/web/search'
        
        headers = {
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip',
            'X-Subscription-Token': api_key,
        }

        # Make the request
        response = requests.get(api_url, params=params, headers=headers, proxies=None)
        response.raise_for_status()
        
        # Process the response
        data = response.json()

        if data.get('results') and len(data['results']) > 0:
            formatted_results = [
                f"Title: {item.get('title', 'N/A')}\nURL: {item.get('url', 'N/A')}\nDescription: {item.get('description', 'N/A')}"
                for item in data['results']
            ]
            
            return jsonify({'results': '\n\n'.join(formatted_results)})
        else:
            return jsonify({'results': 'No results found.'})

    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Request error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
