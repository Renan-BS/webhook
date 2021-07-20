from flask import Flask, request, Response, json

app = Flask(__name__)

@app.route('/')
def api_root(dados):
    try: 
        print(dados)
        return Response(200)
    except:
        return 'Tá funcionando!'

@app.route('/webhook', methods=['POST'])
def respond():
    if request.headers['Content-Type'] == 'application/json':
        return api_root(json.dumps(request.json))
    
if __name__=='__main__':
    app.run()
