from flask import Flask, render_template, request, jsonify
import socket 

app = Flask(__name__)

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': str(error)}), 400

@app.route('/analyze', methods=['GET'])
def analyze():
    url = request.args.get('http://<flask-endpoints>/?url=http://example.com')

    if not url:
        return bad_request('Missing URL parameter.')



    response = {
        'info': {
            'ip': socket.gethostbyname(url.split('/')[2]),  
            'location': 'NA' 
        },
        'subdomains': [], 
        'asset_domains': {
            'javascripts': [],
            'stylesheets': [],
            'images': [],
            'iframes': [],
            'anchors': [],
        }
    }

    return jsonify(response)



if __name__ == '__main__':
    app.run(debug=True)
