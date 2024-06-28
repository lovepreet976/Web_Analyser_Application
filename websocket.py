from flask import Flask, request, jsonify
import socket
import re
import requests
from threading import Thread
from time import sleep

app = Flask(__name__)

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': str(error)}), 400

@app.route('/ws', methods=['GET', 'POST'])
def handle_websocket():
    if 'websocket' in request.environ:
        ws = request.environ['websocket']
        data = ws.receive()
        if data:
            data_json = json.loads(data)
            if 'url' in data_json:
                url = data_json['url']
                ws.send(json.dumps({'data': f'Session created for {url}'}))
            elif 'operation' in data_json:
                operation = data_json['operation']
                if operation == 'get_info':
                    domain_info = get_domain_info(url)
                    ws.send(json.dumps({'data': domain_info}))
                elif operation == 'get_subdomains':
                    subdomains = get_subdomains(url)
                    ws.send(json.dumps({'data': subdomains}))
                elif operation == 'get_asset_domains':
                    asset_domains = get_asset_domains(url)
                    ws.send(json.dumps({'data': asset_domains}))
                else:
                    ws.send(json.dumps({'error': 'Invalid operation'}))
            else:
                ws.send(json.dumps({'error': 'Missing required parameters'}))
        return '', 200
    return 'Bad Request', 400

def get_domain_info(url):
    ip = socket.gethostbyname(url.split('/')[2])
    return {
        'ip': ip,
        'isp': 'N/A',
        'organization': 'N/A',
        'asn': 'N/A',
        'location': 'N/A'
    }

def get_subdomains(url):
    try:
        response = requests.get(url)
        subdomain_pattern = r'([\w-]+\.)?[\w-]+\.[\w-]+'
        subdomains = set(re.findall(subdomain_pattern, response.text))
        return list(subdomains)
    except Exception as e:
        raise Exception(f'Error fetching subdomains: {str(e)}')

def get_asset_domains(url):
    try:
        response = requests.get(url)
        stylesheet_pattern = r'href="([\w:/.-]+\.css)"'
        javascript_pattern = r'src="([\w:/.-]+\.js)"'
        image_pattern = r'src="([\w:/.-]+\.(png|jpg|gif|svg))"'
        iframe_pattern = r'src="([\w:/.-]+)"'
        anchor_pattern = r'href="([\w:/.-]+)"'

        stylesheets = re.findall(stylesheet_pattern, response.text)
        javascripts = re.findall(javascript_pattern, response.text)
        images = re.findall(image_pattern, response.text)
        iframes = re.findall(iframe_pattern, response.text)
        anchors = re.findall(anchor_pattern, response.text)

        return {
            'javascripts': javascripts,
            'stylesheets': stylesheets,
            'images': images,
            'iframes': iframes,
            'anchors': anchors
        }
    except Exception as e:
        raise Exception(f'Error fetching asset domains: {str(e)}')

def run_server():
    app.run(host='0.0.0.0', port=5000)

if __name__ == '__main__':
    server_thread = Thread(target=run_server)
    server_thread.start()
    while True:
        sleep(1)
    

