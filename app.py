from flask import Flask, request, Response, json
import httpx
import re

app = Flask(__name__)

chaves = {
    
    '0a2c56b54cfb002b1baeb40d8ae71ea82d92dff1': 'cliente_desde',
    '7475d515fa7500fdcffb3785ed167db9559a4d74': 'sencon_ultimo_credito',
    'f6a357cb300ec5ab6c26301c4de721c310631b81': 'patrimnio_declarado',
    '4aa08dc5c198dba0151f15bea5d2c028aac95a08': 'patrimnio_xp',
    '9c080d3b1deee4c4b29acdfb091eb81173253da0': 'saldo_em_',
    '4cbd1f76cc1ee4ecb6bedf74ea10248a560d0139': 'cliente_perfil_do_cliente',
    '9011d0f0a699759b313f5245877fc704926ab064': 'max_aloc', 
    '754d3639b9705d33a4b664ddab5466026597ef60': 'max_rv', 
    '1244d2d51f726b3397d92cb8705656105350620d': 'rd_rlp_ativo',
    '6645b632c2ff223481658347bfb5caa877eb20b9': 'status',
    '6f34640413c0bd27c1d071a0411eba7b0d790c2a': 'cod_cliente',
    '657af87f9622875cde313deb4d10ad274ca6aa04': 'telefone',
    '6355acc8eb0f02217dbae67b6faf66d3cdcd8f04': 'atendimento_corporate',
    'owner_id': 'cliente_assessor',
    'f86cbe3aaf2f15880814b46135c5be40738b570a': 'cliente_atendimento_alocacao',
    '68b1fc616650304ff64be50b8fbd8adcd6646780': 'cliente_atendimento_banker',
    'b5fce4ab4a7c45ab9d95dddac83360d6a6eaeeb5': 'cliente_atendimento_private',
    '59d117d3bb53b33be948d0236f8a9316cfc08aaa': 'cliente_atendimento_rv',
    'b79bf961c8a06ef5a9140514836ea8a31303952b': 'cliente_campanha_atual',
    '7bf3c1051ec7c91212d1299053acb70ea6793ef3': 'cliente_captado_por',
    '90074eb7a6d982df48c04f46cf8d5bc97b6f5da9': 'cliente_lead',
    '99cfb895b577dddcb383670d61ba1c236854d289': 'corretagem_ultimo_mes',
    '2bba43ef31d44f56bcc17384149f832baa79da25': 'cpf_cnpj',
    'email': 'email',
    'ff10ceb0bd184d77d55b9ede0aa5b082d092927f': 'multiplas_contas',
    'name': 'nome_cliente',
    'bb4d6a5f8cc3cff24473f8d2d0c7dabc3b517ed6': 'sencon_beneficio',
    '657af87f9622875cde313deb4d10ad274ca6aa04': 'whatsapp'
}

chaves_inversas = {v: k for k, v in chaves.items()}

@app.route('/')
def api_root():
    return 'Tá funcionando!'

@app.route('/webhook', methods=['POST'])
def respond():
    dados = request.json
    print(dados.keys())
    id = getIdFromEmailZendesk(dados['previous']['email'][0]['value'])
    dicio = MontaDicionario(dados['current'])
    base_url = 'https://bsinvestimentos.zendesk.com/'
    if id is not None:
        r = httpx.put(base_url+f'/api/v2/users/{id}', auth=('gustavo.garcia@bsinvestimentos.com.br', 'bs@2021'), data=dicio, headers={"Content-Type": "application/json"})
        print(r.json())
        print('teste', r.status_code)
        return Response(status=200)
    else: return Response(status=200)

def trataTelefone(dado, campo):
    if dado[campo] is None:
        return None
    else:
        lista = re.findall(r"\d+", (dado[campo]))
        valor = ''.join(lista)
        valor = '55' + valor
        valor = int(float(valor))
        print(valor)
        return valor

def MontaDicionario(dado):
    dicio = {"user":{}}
    dicio['user']['telefone'] = trataTelefone(dado, '657af87f9622875cde313deb4d10ad274ca6aa04')
    print(dicio)
    return json.dumps(dicio)
    

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
