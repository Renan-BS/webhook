from flask import Flask, request, Response, json, jsonify

app = Flask(__name__)

@app.route('/')
def api_root(dados):
return 'Tá funcionando!'

@app.route('/webhook', methods=['POST'])
def respond():
    if request.headers['Content-Type'] == 'application/json':
        data = request.json
        return jsonify(data)

    
if __name__=='__main__':
    app.run()
