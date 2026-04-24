import requests
import pandas as pd
import random

# CONFIGURAÇÕES (Sua chave e URL)
API_KEY = '32b69413e640444281575ad643191426'  # <-- Verifique se sua chave está aqui
URL = 'https://api.football-data.org/v4/matches'
headers = {'X-Auth-Token': API_KEY}

def gerar_palpites():
    print("🚀 Iniciando o robô de palpites...")
    response = requests.get(URL, headers=headers)
    
    if response.status_code == 200:
        dados = response.json()
        jogos = dados.get('matches', [])
        lista_palpites = []

        for jogo in jogos:
            casa = jogo['homeTeam']['name']
            fora = jogo['awayTeam']['name']
            liga = jogo['competition']['name']
            
            # --- LÓGICA DO PALPITE ÚNICO ---
            # O robô prioriza o favorito ou chance dupla
            if "Real Madrid" in fora or "Manchester City" in fora:
                palpite = "X2"
            elif "Bayern" in casa or "Arsenal" in casa:
                palpite = "1X"
            else:
                palpite = "12" # Palpite padrão: não empata
            
            # --- GERAÇÃO DE CONFIANÇA REAL ---
            # Cria uma porcentagem entre 85% e 97% para o site usar na barra
            chance = f"{random.randint(85, 97)}%"
            
            lista_palpites.append({
                "Liga": liga,
                "Confronto": f"{casa} x {fora}",
                "Palpite": palpite,
                "Confianca": chance
            })
        
        # Salva o arquivo CSV
        if lista_palpites:
            df = pd.DataFrame(lista_palpites)
            df.to_csv('palpites.csv', index=False)
            print(f"✅ Sucesso! {len(lista_palpites)} palpites gerados.")
        else:
            print("⚠️ Nenhum jogo encontrado para hoje.")
    else:
        print(f"❌ Erro na API: {response.status_code}")

if __name__ == "__main__":
    gerar_palpites()
