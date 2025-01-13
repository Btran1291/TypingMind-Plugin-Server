from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import requests
import os
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

        # Function to check if a parameter should be included
        def is_valid_param(param):
            return param and param != "" and not param.startswith("{") and not param.endswith("}")

        # Construct API URL with careful parameter handling
        params = {
            'q': query,
        }

        # Only add parameters if they have valid values
        param_mapping = {
            'offset': ('offset', data.get('offset')),
            'freshness': ('freshness', data.get('freshness')),
            'result_filter': ('result_filter', data.get('result_filter')),
            'country': ('country', data.get('country')),
            'search_lang': ('search_lang', data.get('searchLang')),
            'ui_lang': ('ui_lang', data.get('uiLang')),
            'count': ('count', data.get('count')),
            'safesearch': ('safesearch', data.get('safesearch')),
            'goggles_id': ('goggles_id', data.get('gogglesId')),
            'units': ('units', data.get('units'))
        }

        for api_param, (param_name, value) in param_mapping.items():
            if is_valid_param(value):
                params[api_param] = value

        # Construct API URL
        api_url = 'https://api.search.brave.com/res/v1/web/search'
        
        headers = {
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip',
            'X-Subscription-Token': api_key,
        }

        # Make the request
        print("Request Parameters:", params)
        response = requests.get(api_url, params=params, headers=headers, proxies=None)
        response.raise_for_status()
        
        # Process the response
        data = response.json()
        
        # Return the raw JSON response
        return jsonify(data)

    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Request error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
