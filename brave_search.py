from flask import Flask, request, jsonify, make_response, Blueprint
from flask_cors import CORS
import requests
from dotenv import load_dotenv
import logging # Import the logging module

load_dotenv()
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(module)s - %(message)s')

brave_search_bp = Blueprint('brave_search', __name__)
CORS(brave_search_bp, resources={r"/brave_search": {"origins": "*"}})

def _format_web_results(results_data):
    if not results_data: return ""
    formatted_items = []
    for i, item in enumerate(results_data): 
        title = item.get('title', 'No Title')
        description = item.get('description', item.get('snippet', 'No Description Provided'))
        url = item.get('url', '#')
        if len(description) > 200: description = description[:197] + "..."
        formatted_items.append(f"  Result {i+1}:\n    Title: {title}\n    Description: {description}\n    URL: {url}")
    if not formatted_items: return ""
    return "Web Results:\n" + "\n\n".join(formatted_items)

def _format_news_results(results_data):
    if not results_data: return ""
    formatted_items = []
    for i, item in enumerate(results_data): 
        title = item.get('title', 'No Title')
        snippet = item.get('snippet', item.get('description', 'No Snippet Provided'))
        url = item.get('url', '#')
        publisher = item.get('meta_url', {}).get('hostname', item.get('publisher', 'Unknown Publisher'))
        date_published = item.get('date', '')
        if len(snippet) > 150: snippet = snippet[:147] + "..."
        formatted_items.append(f"  Article {i+1}:\n    Title: {title}\n    Snippet: {snippet}\n    Source: {publisher}\n    URL: {url}" + (f"\n    Date: {date_published}" if date_published else ""))
    if not formatted_items: return ""
    return "News Articles:\n" + "\n\n".join(formatted_items)

def _format_video_results(results_data):
    if not results_data: return ""
    formatted_items = []
    for i, item in enumerate(results_data): 
        title = item.get('title', 'No Title')
        description = item.get('description', 'No Description Provided')
        url = item.get('url', '#')
        publisher = item.get('meta_url', {}).get('hostname', item.get('publisher', 'Unknown Publisher'))
        duration = item.get('duration', '')
        if len(description) > 150: description = description[:147] + "..."
        formatted_items.append(f"  Video {i+1}:\n    Title: {title}\n    Description: {description}\n    Source: {publisher}\n    URL: {url}" + (f"\n    Duration: {duration}" if duration else ""))
    if not formatted_items: return ""
    return "Videos:\n" + "\n\n".join(formatted_items)

def _format_discussion_results(results_data):
    if not results_data: return ""
    formatted_items = []
    for i, item in enumerate(results_data): 
        title = item.get('title', "No Title")
        snippet = item.get('snippet', item.get('description', "No Snippet Provided"))
        url = item.get('url', "#")
        source = item.get('meta_url', {}).get('hostname', "Unknown Source")
        if len(snippet) > 150: snippet = snippet[:147] + "..."
        formatted_items.append(f"  Discussion {i+1}:\n    Title: {title}\n    Snippet: {snippet}\n    Source: {source}\n    URL: {url}")
    if not formatted_items: return ""
    return "Discussions:\n" + "\n\n".join(formatted_items)

def _format_location_results(results_data):
    if not results_data: return ""
    formatted_items = []
    for i, item in enumerate(results_data): 
        title = item.get('title', "No Name Provided")
        address_obj = item.get('address', {})
        address_display = address_obj.get('display_address', address_obj.get('text', item.get('description', "No Address Information")))
        url = item.get('url', item.get('website', "#"))
        formatted_items.append(f"  Location {i+1}:\n    Name: {title}\n    Address: {address_display}" + (f"\n    URL: {url}" if url != "#" else ""))
    if not formatted_items: return ""
    return "Locations:\n" + "\n\n".join(formatted_items)

def format_brave_response_comprehensive(brave_data):
    if not brave_data or not isinstance(brave_data, dict):
        logging.warning("Format_brave_response_comprehensive: No data or unexpected data format received.")
        return "No data received or data in unexpected format from Brave Search."

    all_formatted_sections = []
    result_type_map = {
        'web': _format_web_results,
        'news': _format_news_results,
        'videos': _format_video_results,
        'discussions': _format_discussion_results,
        'locations': _format_location_results
    }

    for key_in_json, formatter_func in result_type_map.items():
        if key_in_json in brave_data and brave_data[key_in_json].get('results'):
            formatted_section = formatter_func(brave_data[key_in_json]['results'])
            if formatted_section:
                all_formatted_sections.append(formatted_section)
    
    summary_text = ""
    if 'mixed' in brave_data and brave_data['mixed'].get('type') == 'summary':
        summary_text = brave_data['mixed'].get('summary', {}).get('text', '')
    elif 'infobox' in brave_data and brave_data['infobox'].get('results'):
        if brave_data['infobox']['results']:
            infobox_result = brave_data['infobox']['results'][0]
            summary_text = infobox_result.get('description', infobox_result.get('long_snippet', ''))

    if summary_text:
        all_formatted_sections.insert(0, f"Summary from Brave Search:\n  {summary_text.strip()}")

    all_formatted_sections = [section for section in all_formatted_sections if section and section.strip()]

    if not all_formatted_sections:
        logging.info("Format_brave_response_comprehensive: No relevant search results found or results could not be parsed.")
        return "No relevant search results found or results could not be parsed."
        
    return "\n\n===\n\n".join(all_formatted_sections)

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
            logging.error("No JSON data provided in request.")
            return jsonify({'error': 'No JSON data provided', 'search_summary': 'Error: No input data received by server.'}), 400

        api_key = data.get('braveSearchAPIKey')
        query = data.get('q')
        
        if not api_key:
            logging.error("Brave Search API Key is required but not provided.")
            return jsonify({'error': 'Brave Search API Key is required', 'search_summary': 'Error: API Key missing. Please configure the plugin.'}), 400
        if not query:
            logging.error("Search query is required but not provided.")
            return jsonify({'error': 'Search query is required', 'search_summary': 'Error: Search query missing.'}), 400

        def is_valid_param(param_value, param_name_for_log="parameter"): # Added param_name_for_log for better logging
            if param_value is None:
                return False
            s_value = str(param_value).strip()
            if not s_value:
                return False
            lower_s_value = s_value.lower()
            if lower_s_value == "undefined" or lower_s_value == "null":
                return False
            if s_value.startswith("{") and s_value.endswith("}"):
                logging.info(f"Parameter '{param_name_for_log}' value ('{s_value}') looks like an unsubstituted placeholder. Treating as invalid.")
                return False
            return True

        params = {'q': query}
        param_mapping = {
            'offset': data.get('offset'),
            'freshness': data.get('freshness'),
            'result_filter': data.get('result_filter'),
            'country': data.get('country'),
            'search_lang': data.get('searchLang'),
            'count': data.get('count'),
            'safesearch': data.get('safesearch'),
            'goggles_id': data.get('gogglesId'),
            'units': data.get('units')
        }

        for api_param, value in param_mapping.items():
            if is_valid_param(value, api_param): # Pass api_param for logging context
                if api_param in ['count', 'offset']:
                    try:
                        num_value = int(str(value))
                        if api_param == 'offset':
                            if num_value >= 0: params[api_param] = num_value
                        elif api_param == 'count': 
                            if num_value > 0: params[api_param] = min(num_value, 20) 
                    except (ValueError, TypeError):
                        logging.warning(f"Could not convert {api_param} ('{value}') to int. Skipping.")
                        continue
                else:
                    params[api_param] = value
        
        if 'count' not in params:
            params['count'] = 10
            logging.debug("Parameter 'count' not provided or invalid, defaulting to 10.")


        api_url = 'https://api.search.brave.com/res/v1/web/search'
        headers = {
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip',
            'X-Subscription-Token': api_key,
        }

        logging.info(f"Requesting Brave API. Query: '{query}', Params: {params}")
        
        api_response = requests.get(api_url, params=params, headers=headers, proxies=None)
        api_response.raise_for_status()
        
        brave_api_data = api_response.json()
        
        # For debugging, you might want to see the raw data sometimes
        # logging.debug(f"Raw Brave API Data: {brave_api_data}")

        formatted_text_response = format_brave_response_comprehensive(brave_api_data)
        
        return jsonify({'search_summary': formatted_text_response})

    except requests.exceptions.HTTPError as http_err:
        error_message = f'Brave API HTTP error: {http_err.response.status_code} - {http_err.response.reason}'
        try:
            brave_error_details = http_err.response.json()
            error_message += f". Details: {brave_error_details.get('message', brave_error_details)}"
        except ValueError: # If Brave error response is not JSON
            error_message += f". Response body (partial): {http_err.response.text[:200]}"
        
        logging.error(f"HTTPError when calling Brave API: {error_message}")
        return jsonify({'error': error_message, 'search_summary': 'Error communicating with the search service.'}), getattr(http_err.response, 'status_code', 500)

    except requests.exceptions.RequestException as req_err:
        error_message = f'Network or Request error when calling Brave API: {str(req_err)}'
        logging.error(error_message)
        return jsonify({'error': error_message, 'search_summary': 'Error connecting to the search service.'}), 500
        
    except Exception as e:
        error_message = f'An unexpected server error occurred: {str(e)}'
        # exc_info=True will include the full traceback in the log
        logging.error(error_message, exc_info=True) 
        return jsonify({'error': error_message, 'search_summary': 'An unexpected error occurred while processing your search.'}), 500
