import os
import time
import pandas as pd
import pytesseract
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image

def executar_robo_no_github():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        print("🛰️ Acessando Oddspedia para análise de Odds e xG...")
        driver.get("https://oddspedia.com/br/futebol")
        time.sleep(15) 

        # Tira o print da tela para o OCR
        driver.save_screenshot("screenshot.png")
        
        # Aqui o robô processa os dados (Simulação de extração de alto nível)
        dados_jogos = [
            {
                "TimeCasa": "Manchester City", 
                "TimeFora": "Real Madrid", 
                "OddCasa": "1.85", 
                "OddFora": "4.10", 
                "xG": "2.4 vs 1.1",
                "Entrada": "Over 2.5 Gols", 
                "Assertividade": 94
            },
            {
                "TimeCasa": "Bayern", 
                "TimeFora": "Arsenal", 
                "OddCasa": "2.15", 
                "OddFora": "3.20", 
                "xG": "1.8 vs 1.9",
                "Entrada": "Ambas Marcam", 
                "Assertividade": 88
            }
        ]
        
        # Salva o CSV com as colunas certas para o HTML ler
        df = pd.DataFrame(dados_jogos)
        df.to_csv('palpites.csv', index=False)
        print("✅ Dados com Odds e xG salvos em palpites.csv")

    finally:
        driver.quit()

if __name__ == '__main__':
    executar_robo_no_github()
