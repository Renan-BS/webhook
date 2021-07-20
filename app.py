from flask import Flask, request, Response, json, jsonify

app = Flask(__name__)

@app.route('/')
def api_root():
    return 'Tá funcionando!'

@app.route('/webhook', methods=['POST'])
def respond():
    request_data = request.get_json()
    return "{}".format(request_data)

    
if __name__=='__main__':
    app.run()
