import requests
import pandas as pd

# SUSTITUA PELO SEU TOKEN QUE CHEGOU NO E-MAIL
API_KEY = "32b69413e640444281575ad643191426" 
URL = "https://api.football-data.org/v4/matches"

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
            
            # LÓGICA DO ROBÔ
            # Ex: Se o jogo for Real Betis vs Real Madrid (que está na sua tela)
            # O robô vai sugerir X2 porque o Real Madrid é favorito.
            palpite_cd = "X2" if "Real Madrid" in fora or "Leipzig" in casa else "12"
            
            lista_palpites.append({
                "Confronto": f"{casa} vs {fora}",
                "Chance Dupla": palpite_cd,
                "Gols": "Over 1.5",
                "Escanteios": "8.5+"
            })
            
        # Cria o arquivo que o site vai ler
        df = pd.DataFrame(lista_palpites)
        df.to_csv("palpites.csv", index=False)
        print("✅ Arquivo 'palpites.csv' gerado com sucesso!")
    else:
        print(f"❌ Erro na API: {response.status_code}")

gerar_palpites()