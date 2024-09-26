from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import os
import math
from datetime import datetime
from pytz import timezone
from pymongo import MongoClient
import gridfs
import sys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

if 'HTTP_PROXY' in os.environ:
    del os.environ['HTTP_PROXY']
if 'HTTPS_PROXY' in os.environ:
    del os.environ['HTTPS_PROXY']



chrome_profile_path = r"C:\Users\3470622\AppData\Local\Google\Chrome\User Data"
profile_directory = "Default"
chrome_options = Options()
chrome_options.add_argument(f"user-data-dir={chrome_profile_path}")
chrome_options.add_argument(f"--profile-directory={profile_directory}")

chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--remote-debugging-port=9222")

client = MongoClient('mongodb:ip do servidor')
db = client['rgi']
collection = db['teste_rgi']
fs = gridfs.GridFS(db)

collection.create_index("created_at", expireAfterSeconds=40 * 24 * 60 * 60)

navegador = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)


navegador.get('https://oficioeletronico.com.br/Instituicoes/Consultas?page=1')

def awaitElement(by: str = By.ID, value: str | None = None, time: int = 10):
    return WebDriverWait(navegador, time).until(EC.presence_of_element_located((by, value)))

def awaitElements(by: str = By.ID, value: str | None = None, time: int = 10):
    return WebDriverWait(navegador, time).until(EC.presence_of_all_elements_located((by, value)))

filtro = awaitElement(By.NAME, 'filterStatus')
# filtro = awaitElement(By.NAME, 'filterStatus')
filtro.click()
# time.sleep(1)
respondido = awaitElement(By.XPATH, '//*[@id="filterStatus"]/option[3]')
respondido.click()
# time.sleep(1)
filtrar = awaitElement(By.XPATH, '//*[@id="main"]/div[2]/ul/li[1]/button')
filtrar.click()

time.sleep(1)


qtd_itens_element = awaitElement(By.XPATH, '//*[@id="main"]/div[5]/div/div/span[1]/p[2]')
qtd_itens = qtd_itens_element.text.strip().split(' ')
# index = qtd_itens.find(' ')
print(qtd_itens)

qtd = int(qtd_itens[-1])
print(qtd)
# qtd = math.ceil(int(qtd) / 10)

for numero in range(1, qtd + 1):
    # time.sleep(2)
    navegador.get(f'https://oficioeletronico.com.br/Instituicoes/Consultas?page={numero}')

     
    for tr in range(1, 11):
        
        varrer_protocolo = awaitElement(By.XPATH, f'//*[@id="main"]/div[5]/table/tbody/tr[{tr}]/td[2]')
        texto_protocolo = varrer_protocolo.text.strip()
        documento_encontrado = collection.find_one({'Protocolo': texto_protocolo})

        if documento_encontrado is None:
            print(f"Protocolo {texto_protocolo} não existe no banco, SENDO BAIXADO.")
                    
            abrir_pagina = awaitElement(By.XPATH, f'//*[@id="main"]/div[5]/table/tbody/tr[{tr}]/td[1]/a')  
            abrir_pagina.click()
        
            # time.sleep(2)

            anexos = awaitElement(By.NAME, 'btnPanelAnexos')
            anexos.click()

            # time.sleep(2)
            
            # label = [' Protocolo', ' Cartório', ' Subdistrito', ' CEP', ' Via', ' Endereço', ' Número', ' Complemento', ' Número Ofício', ' Número Contribuinte(IPTU)', ' Observações']
            
            # label_banco = ['protocolo', 'cartorio', 'subdistrito', 'cep', 'via', 'endereco', 'numero', 'complemento', 'numero_oficio', 'numero_contribuinte_iptu', 'observacoes']
            
            lista_infos = {}

            # for index, itens in enumerate(label):
            #     info = awaitElement(By.XPATH, f"//label[contains(text(), '{itens}')]/following-sibling::span").text
            #     lista_infos[label_banco[index]] = info

            dados = navegador.find_element(By.ID, value='Dados')
            campos = dados.find_elements(By.TAG_NAME, value='label')

            # [print(i.text) for i in dados]
            for i in campos:
                lista_infos[i.text.strip()] = i.find_element(By.XPATH,'following-sibling::span[1]').text.strip() 
            
            label_banco2 = ['Nome Anexo', 'Formato']
            try:
                tds_com_texto = awaitElements(By.XPATH, "//div[contains(@class, 'list-wrap')]//td[string-length(normalize-space()) > 2]", 2)

                # for index, td in enumerate(tds_com_texto):
                #     lista_infos[label_banco2[index]] = td.text.strip()
                for index, td in enumerate(tds_com_texto):
                    if index < len(label_banco2):
                        lista_infos[label_banco2[index]] = td.text.strip()
                    else:
                        print(f"Índice {index} fora do alcance de label_banco2, valor ignorado.")

            except Exception:
                print(Exception)

            lista_infos['Data de Criação'] = datetime.now(timezone('Brazil/East'))
            
            print(lista_infos)

            if '' in lista_infos:
                del lista_infos['']
            
            # Inserir informações no MongoDB
            doc_id = collection.insert_one(lista_infos).inserted_id

            # time.sleep(2)

            try:
                baixar = awaitElement(By.CSS_SELECTOR, "a[title='Download']", 2)
                baixar.click()
                time.sleep(2)
                lista_infos['Tem Anexo'] = True
            except Exception:
                lista_infos['Tem Anexo'] = False
                print(Exception)


            # time.sleep(2)
            navegador.back()
        else:
            print("DOCUMENTO JA EXISTE, PULANDO DOWNLOAD")

