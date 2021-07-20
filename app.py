from flask import Flask, request, Response, json
import httpx

app = Flask(__name__)

@app.route('/')
def api_root():
    return 'Tá funcionando!'

@app.route('/webhook', methods=['POST'])
def respond():
    dados = request.json
    print(dados.keys())
    id = getIdFromEmailZendesk(dados['previous']['email'][0]['value'])
    dicio = {"user": {"user_fields": {'corretagem_ultimo_mes':'teste'}}}
    base_url = 'https://bsinvestimentos.zendesk.com/'
    if id is not None:
        r = httpx.put(base_url+f'/api/v2/users/{id}', auth=('gustavo.garcia@bsinvestimentos.com.br', 'bs@2021'), data=json.dumps(dicio), headers={"Content-Type": "application/json"})
        print(r.json())
        print('teste', r.status_code)
        return Response(status=200)
    else: return Response(status=200)

def getIdFromEmailZendesk(email):
    base_url = 'https://bsinvestimentos.zendesk.com/'
    headers = {"Content-Type": "application/json"}
    params = {'role': 'end-user'}
    r = httpx.get(base_url + f'/api/v2/search?query=email:{email}', auth=('gustavo.garcia@bsinvestimentos.com.br', 'bs@2021'), headers=headers, params=params, timeout=None)
    id = r.json()['results'][0]['id']
    if id is None:
        return None
    else: 
        return id
   
if __name__=='__main__':
    app.run()
