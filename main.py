import requests
from rammer_utils.utils.log import init_root_logger
from superlogica_chamadas_API.preparo_condominio import PreparoCondominio
import logging
import csv

init_root_logger()
logger = logging.getLogger(__name__)

post_headers = {
    "Content-Type" : "application/x-www-form-urlencoded",
    "app_token" : "abcaac41-b011-4dad-bf94-d078eb4e3cc2",
    "access_token" : "10c4f4d3-894b-480b-a84e-fade81415b7c"
}

get_header = {
    'Content-Type': 'application/json',
    'app_token': 'abcaac41-b011-4dad-bf94-d078eb4e3cc2',
    'access_token': '10c4f4d3-894b-480b-a84e-fade81415b7c'    
}


def ler_codigo_csv(caminho_arquivo, coluna_codigo):
    with open(caminho_arquivo, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        return [linha[coluna_codigo] for linha in reader]


def adicionar_cond_no_grupo_implantacao(id_sl):

    url = f'https://admin109683.superlogica.net/condor/atual/condominios/adicionargrupo?grupos[0][ST_GRUPO_CG]=Condomínio em implantação&grupos[0][ID_GRUPO_CG]=43&ID_CONDOMINIO_COND={id_sl}&ID_FORNECEDOR=&FL_TIPO_CG='

    response = requests.post(
        url=url,
        headers= post_headers
    )

    if response.status_code != 200:
        return None

    data = response.json()

    return data


def remover_conds_no_grupo_implantacao(lista_ids_para_serem_removidos):

    
    url_get = "https://api.superlogica.net/v2/condor/condominiogrupos/index?somenteGruposComCondominios=1"
    
    
    response = requests.get(
        url= url_get,
        headers=get_header
    )
    
    data = response.json()

    lista_total = []
    for grupo in data:
        if grupo.get('id_grupo_cg') == "43":
            lista_total.append(grupo.get("lista_condominios"))

    lista_total = lista_total[0].split(',')

    lista_final = set(lista_total) - set(lista_ids_para_serem_removidos)

    url_post = f'https://admin109683.superlogica.net/condor/atual/condominios/adicionarcondominios?id=0'

    data = {
        "ID_GRUPO_CG": 43,
        "condominios[0][ID_CONDOMINIO_COND]": list(lista_final)
    }


    response = requests.post(
        url=url_post,
        headers= post_headers,
        data=data
    )

    if response.status_code != 200:
        return None

    data = response.json()

    return data



def get_all_condominios():
    condominios = []
    page = 1

    logger.info("Iniciando busca de todos os condomínios")

    while True:
        url = f'https://api.superlogica.net/v2/condor/condominios/get?id=-1&somenteCondominiosAtivos=1&ignorarCondominioModelo=1&apenasColunasPrincipais=1&apenasDadosDoPlanoDeContas=0&comDataFechamento=1&itensPorPagina=50&pagina={page}'
        response = requests.get(url, headers=get_header)

        if response.status_code != 200:
            logger.error(f"Erro ao acessar a API: {response.status_code}")
            break

        data = response.json()
        condominios.extend(data)

        logger.info(f"Página {page} processada. {len(data)} condomínios encontrados.")

        if len(data) < 50:
            break

        page += 1

    logger.info(f"Busca de condomínios concluída. Total de {len(condominios)} condomínios.")

    tuplas_codigo_id = []

    for cond in condominios:
            tuplas_codigo_id.append((cond.get("st_label_cond") ,cond.get('id_condominio_cond')))

    return tuplas_codigo_id

def get_id_sl(codigo):

    url = f"https://servidor-webapp.estasa.net:8085/apisqlserver/get_id_sl/{codigo}"

    response = requests.get(
        url=url,
        verify=False
    )
    data = response.json()

    return data


def main():

    # Exemplo de uso
    list_remove = []
    list_no_remove = []
    codigos_remove = ler_codigo_csv("remover_do_grupo.csv", "codigo")
    if codigos_remove:
        logger.info(f"Començando a remover os condominio {codigos_remove} do grupo de saldo de importação")

    id_sl_remove = []
    for codigo in codigos_remove:
        id_sl_remove.append(get_id_sl(codigo))    
    
    remove = remover_conds_no_grupo_implantacao(id_sl_remove)
    if remove:
        list_remove.append(codigo)
        logger.info("condominios removidos com sucesso")
    else:
        list_no_remove.append(codigo)


    list_add = []
    list_no_add = []
    codigos_add = ler_codigo_csv("inserir_no_grupo.csv", "codigo")
    if codigos_add:
        logger.info(f"Començando a adicionar os condominio {codigos_add} ao grupo de saldo de importação")

        for codigo in codigos_add:
            id_sl = get_id_sl(codigo)
            add = adicionar_cond_no_grupo_implantacao(id_sl)
            if add:
                logger.info(f"{codigo} adicionado ao grupo de saldo de implantação")
                list_add.append(codigo)
            else:
                list_no_add.append(codigo)



    

main()
