from flask import Flask, request, jsonify, make_response, Blueprint
from flask_cors import CORS
import requests
from dotenv import load_dotenv

load_dotenv()

brave_search_bp = Blueprint('brave_search', __name__)
CORS(brave_search_bp, resources={r"/brave_search": {"origins": "*"}})

@brave_search_bp.route('/brave_search', methods=['OPTIONS', 'POST'])
def brave_search():
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response

    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        api_key = data.get('braveSearchAPIKey')
        query = data.get('q')
        
        if not api_key:
            return jsonify({'error': 'Brave Search API Key is required'}), 400
        if not query:
            return jsonify({'error': 'Search query is required'}), 400

        params = {
            'q': query,
        }

        param_mapping = {
            'offset': ('offset', data.get('offset')),
            'freshness': ('freshness', data.get('freshness')),
            'result_filter': ('result_filter', data.get('result_filter')),
            'country': ('country', data.get('country')),
            'search_lang': ('search_lang', data.get('searchLang')),
            'count': ('count', data.get('count')),
            'safesearch': ('safesearch', data.get('safesearch')),
            'goggles_id': ('goggles_id', data.get('gogglesId')),
            'units': ('units', data.get('units'))
        }
        
        for api_param, (param_name, value) in param_mapping.items():
            if value is not None:
                params[api_param] = value

        api_url = 'https://api.search.brave.com/res/v1/web/search'
        
        headers = {
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip',
            'X-Subscription-Token': api_key,
        }

        print("Request Parameters:", params)
        response = requests.get(api_url, params=params, headers=headers, proxies=None)
        response.raise_for_status()
        
        data = response.json()
        
        return jsonify(data)

    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Request error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500
