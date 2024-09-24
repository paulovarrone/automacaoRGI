
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import os
import math
from datetime import datetime
from pytz import timezone


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


navegador = webdriver.Chrome(options=chrome_options)

time.sleep(2)


navegador.get('https://oficioeletronico.com.br/Instituicoes/Consultas?page=1')


time.sleep(5)

filtro = navegador.find_element(By.NAME, 'filterStatus')
filtro.click()
time.sleep(1)
respondido = navegador.find_element(By.XPATH, '//*[@id="filterStatus"]/option[3]')
respondido.click()
time.sleep(1)
filtrar = navegador.find_element(By.XPATH, '//*[@id="main"]/div[2]/ul/li[1]/button')
filtrar.click()

time.sleep(2)


qtd_itens_element = navegador.find_element(By.XPATH, '//*[@id="main"]/div[5]/div/div/span[1]/p[1]')
qtd_itens = qtd_itens_element.text.strip()
index = qtd_itens.find(' ')
qtd = qtd_itens[:index]
qtd = math.ceil(int(qtd) / 10)

for numero in range(1, qtd + 1):
    time.sleep(2)
    navegador.get(f'https://oficioeletronico.com.br/Instituicoes/Consultas?page={numero}')

    for tr in range(1, 11):
        time.sleep(2)
        
        abrir_pagina = navegador.find_element(By.XPATH, f'//*[@id="main"]/div[5]/table/tbody/tr[{tr}]/td[1]/a')  
        abrir_pagina.click()
    
        time.sleep(2)

        anexos = navegador.find_element(By.NAME, 'btnPanelAnexos')
        anexos.click()

        time.sleep(2)
        
        label = [' Protocolo', ' Cartório', ' Subdistrito', ' CEP', ' Via', ' Endereço', ' Número', ' Complemento', ' Número Ofício', ' Número Contribuinte(IPTU)', ' Observações']
        
        label_banco = ['protocolo', 'cartorio', 'subdistrito', 'cep', 'via', 'endereco', 'numero', 'complemento', 'numero_oficio', 'numero_contribuinte_iptu', 'observacoes']
        
        lista_infos = {}

        for index, itens in enumerate(label):
            info = navegador.find_element(By.XPATH, f"//label[contains(text(), '{itens}')]/following-sibling::span").text
            lista_infos[label_banco[index]] = info
            # lista_infos.append({itens.strip().lower(): info})
        

        label_banco2 = ['nome_anexo', 'formato']
        tds_com_texto = navegador.find_elements(By.XPATH, "//div[contains(@class, 'list-wrap')]//td[string-length(normalize-space()) > 2]")

        for index, td in enumerate(tds_com_texto):
            # lista_infos.append({td.text.strip().lower(): td.text.strip()})
            lista_infos[label_banco2[index]] = td.text.strip()
        
        lista_infos['created_at'] = datetime.now(timezone('Brazil/East'))
        
        print(lista_infos)

        

        time.sleep(2)


        baixar = navegador.find_element(By.CSS_SELECTOR, "a[title='Download']")
        baixar.click()

        time.sleep(2)
        navegador.back()


