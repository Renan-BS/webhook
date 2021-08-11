from flask import Flask, request, Response, json
from celery import Celery
import httpx
import re
import datetime
import time

flask_app = Flask(__name__)
celery_app = Celery(__name__)
celery_app.config_from_object('celery_settings')


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

simnao = {'Sim':'sim', "'-":'não', 'Não':'não', None:'não', '133':'sim', '134':'não'}

perfil_dict = {
    'Agressivo':'cliente_agressivo',
    'Não Preenchido': '0', 
    'Moderado': 'cliente_moderado',
    'Conservador': 'cliente_conservador',
    "'-":'0',
    '':'0',
    '-':'0',
    None:'0'
}

contas_duplicadas = {
    'Sim': 'sim_cd', 
    'Não': 'nao_cd'
}

@celery_app.task()
def update(id, dados):
    dicio = MontaDicionario(dados['current'])
    base_url = 'https://bsinvestimentos.zendesk.com/'
    print('to aqui', id)
   
    r = httpx.put(base_url+f'/api/v2/users/{id}', auth=('gustavo.garcia@bsinvestimentos.com.br', 'blu3st4r'), data=dicio, headers={"Content-Type": "application/json"}, timeout=None)    
    if r.status_code == 200:
        print(id, 'Deu certo Porra')
    else:
        print('Erro de código', r.status_code)
    r.close()
    return Response(status=200)
    
    
@flask_app.route('/')
def api_root():
    return 'Tá funcionando!'

@flask_app.route('/update', methods=['POST'])
def respond():
    dados = request.json
    id = getIdFromEmailZendesk(dados['previous']['email'][0]['value'])
    if id is not None:
        time.sleep(1)
        print(id)
        update.delay(id, dados)
        return Response(status=200)
    else: 
        return Response(status=200)

def trataTelefone(dado, campo):
    if dado[campo] is None:
        
        return 0
    else:
        lista = re.findall(r"\d+", (dado[campo]))
        valor = ''.join(lista)
        return int(float(valor))
        """if valor[0:2]=='55':
            return int(float(valor))
        else:
            valor = '55' + valor 
            return int(valor)"""

def retornaUser(id):
    if id is None:
        return None
    else:
        params = {'api_token': '0cb8d176cfa982bf4826707cd232b18b370ee818'}
        time.sleep(2)
        response = httpx.get(f'https://bsprivate.pipedrive.com/api/v1/users/{id}', params=params)
        dado = response.json()['data']['name']
        response.close()
        return dado

def retornaCampo(key, id):
    
    params = {'api_token': '0cb8d176cfa982bf4826707cd232b18b370ee818'}
    time.sleep(2)
    response = httpx.get(f'https://bsprivate.pipedrive.com/api/v1/personFields', params=params)
    
    nome = response.json()
    response.close()
    if id is None:
        return None
    else:
        for n in nome['data']:
            if n['key'] == key:
                opcoes = n['options']
                for opcao in opcoes:
                    if int(id) == opcao['id']:
                        return opcao['label'] 

def trataFloat(dado, campo):
    if dado[chaves_inversas[campo]] is None:
        return None
    else: 
        return float(dado[chaves_inversas[campo]])

def trataStatus(dado, campo):
    if dado[chaves_inversas['status']] == '3':
        return 'cliente_ativo'
    else: return 'cliente_inativo'

def trataClass(dado, campo, campo2):
    if dado[campo] is None:
        c1 = 0
    else:
        c1 = int(dado[campo])
    if dado[campo2] is None:
        c2 = 0
    else:
        c2 = int(dado[campo2])
    return str(max(c1, c2))

def trataRLP(dado):
    if dado is None:
        return None
    elif dado == '137':
        return 'sim'
    else: return 'não'
    
def MontaDicionario(dado):
    dicio = {"user":{'user_fields':{}}}
    dicio['user']['user_fields']['telefone'] = trataTelefone(dado, '657af87f9622875cde313deb4d10ad274ca6aa04')
    dicio['user']['user_fields']['cliente_ultima_atualizacao'] = datetime.datetime.now().isoformat()
    dicio['user']['user_fields']['cliente_desde'] = dado[chaves_inversas['cliente_desde']]
    dicio['user']['user_fields']['sencon_ultimo_credito'] = dado[chaves_inversas['sencon_ultimo_credito']]
    dicio['user']['user_fields']['nome_cliente'] = dado[chaves_inversas['nome_cliente']]
    dicio['user']['user_fields']['email_xp'] = dado[chaves_inversas['email']][0]['value']
    dicio['user']['user_fields']['cliente_atendimento_alocacao'] = retornaUser(dado[chaves_inversas['cliente_atendimento_alocacao']])
    dicio['user']['user_fields']['cliente_atendimento_banker'] = retornaUser(dado[chaves_inversas['cliente_atendimento_banker']])
    dicio['user']['user_fields']['cliente_atendimento_private'] = retornaUser(dado[chaves_inversas['cliente_atendimento_private']])
    dicio['user']['user_fields']['cliente_atendimento_rv'] = retornaUser(dado[chaves_inversas['cliente_atendimento_rv']])
    dicio['user']['user_fields']['cliente_assessor'] = retornaUser(dado[chaves_inversas['cliente_assessor']])
    dicio['user']['user_fields']['cliente_captado_por'] = retornaUser(dado[chaves_inversas['cliente_captado_por']])
    dicio['user']['user_fields']['cliente_campanha_atual'] = retornaCampo(chaves_inversas['cliente_campanha_atual'], dado[chaves_inversas['cliente_campanha_atual']])
    dicio['user']['user_fields']['cliente_lead'] = retornaCampo(chaves_inversas['cliente_lead'], dado[chaves_inversas['cliente_lead']])
    dicio['user']['user_fields']['corretagem_ultimo_mes'] = dado[chaves_inversas['corretagem_ultimo_mes']]
    dicio['user']['user_fields']['cpf_cnpj'] = dado[chaves_inversas['cpf_cnpj']]
    dicio['user']['user_fields']['multiplas_contas'] = dado[chaves_inversas['multiplas_contas']]
    dicio['user']['user_fields']['patrimnio_declarado'] = trataFloat(dado, 'patrimnio_declarado')
    dicio['user']['user_fields']['patrimnio_xp'] = trataFloat(dado, 'patrimnio_xp')
    dicio['user']['user_fields']['saldo_em_'] = trataFloat(dado, 'saldo_em_')
    dicio['user']['user_fields']['status'] = trataStatus(dado, 'status')
    dicio['user']['user_fields']['cliente_perfil_do_cliente'] = perfil_dict[dado[chaves_inversas['cliente_perfil_do_cliente']]]
    dicio['user']['user_fields']['sencon_beneficio'] = simnao[dado[chaves_inversas['sencon_beneficio']]]
    dicio['user']['user_fields']['nivel_classificacao'] = 'nivel_' + trataClass(dado, '9011d0f0a699759b313f5245877fc704926ab064','754d3639b9705d33a4b664ddab5466026597ef60')
    dicio['user']['user_fields']['whatsapp'] = dado[chaves_inversas['whatsapp']]
    dicio['user']['user_fields']['cod_cliente'] =  dado[chaves_inversas['cod_cliente']]
    dicio['user']['user_fields']['telefone'] = trataTelefone(dado, '657af87f9622875cde313deb4d10ad274ca6aa04')
    dicio['user']['user_fields']['rd_rlp_ativo'] = trataRLP(dado[chaves_inversas['rd_rlp_ativo']])
    dicio['user']['user_fields']['contas_duplicadas_pergunta'] = 'não_cd'
    return json.dumps(dicio)
    

def getIdFromEmailZendesk(email):
    base_url = 'https://bsinvestimentos.zendesk.com/'
    headers = {"Content-Type": "application/json"}
    params = {'role': 'end-user'}
    r = httpx.get(base_url + f'/api/v2/search?query=email:{email}', auth=('gustavo.garcia@bsinvestimentos.com.br', 'blu3st4r'), headers=headers, params=params, timeout=None)
    
    try:
        id = r.json()['results'][0]['id']
        return id
    except:
        print(email, 'nao encontrado')
        return None
   
if __name__=='__main__':
    flask_app.run()
