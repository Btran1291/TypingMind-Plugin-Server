from flask import Flask, request, jsonify, make_response, Blueprint
from flask_cors import CORS
import requests

vectorize_query_bp = Blueprint('vectorize_query', __name__)
CORS(vectorize_query_bp, resources={r"/vectorize-rag-retrieve": {"origins": "*"}})

@vectorize_query_bp.route('/vectorize-rag-retrieve', methods=['OPTIONS', 'POST'])
def vectorize_rag_retrieve():
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
        
        # Extract parameters from the request
        access_token = data.get('accessToken')
        retrieval_endpoint_url = data.get('retrievalEndpointURL')
        question = data.get('question')
        num_results = data.get('numResults')

        if not num_results:
            num_results = 5
        else:
            try:
                num_results = int(num_results)
                # Handle case where num_results is 0
                if num_results <= 0:
                    num_results = 5
            except ValueError:
                num_results = 5
        
        rerank = data.get('rerank', True)
        
        # Validate required parameters
        if not access_token or not retrieval_endpoint_url:
            return jsonify({
                "error": "Missing access token or retrieval endpoint URL"
            }), 400
        if not question:
            return jsonify({'error': 'Search query is required'}), 400
        
        # Prepare request to Vectorize
        vectorize_payload = {
            "question": question,
            "numResults": num_results,
            "rerank": rerank
        }
        
        # Make request to Vectorize
        vectorize_response = requests.post(
            retrieval_endpoint_url,
            headers={
                'Content-Type': 'application/json',
                'Authorization': access_token
            },
            json=vectorize_payload
        )
        
        # Check if Vectorize request was successful
        if not vectorize_response.ok:
            return jsonify({
                "error": f"Vectorize API error: {vectorize_response.text}"
            }), vectorize_response.status_code
        
        # Return the Vectorize response
        return jsonify(vectorize_response.json())
    
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Request error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500
