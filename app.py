from flask import Flask, request, Response, json

app = Flask(__name__)

@app.route('/')
def api_root():
    return 'Tá funcionando!'

@app.route('/webhook', methods=['POST',])
def respond():
    print(request.json)
    if request.headers['Content-Type'] == 'application/json':
        #return json.dumps(request.json)
        return Response(status=200)
    
if __name__=='__main__':
    app.run()
