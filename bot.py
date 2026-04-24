import requests
import pandas as pd
import random
from datetime import datetime

API_KEY = '32b69413e640444281575ad643191426'
URL = 'https://api.football-data.org/v4/matches'
headers = {'X-Auth-Token': API_KEY}

def gerar_palpites():
    response = requests.get(URL, headers=headers)
    if response.status_code == 200:
        jogos = response.json().get('matches', [])
        lista_palpites = []

        for jogo in jogos:
            data_utc = jogo['utcDate']
            data_obj = datetime.strptime(data_utc, "%Y-%m-%dT%H:%M:%SZ")
            
            casa = jogo['homeTeam']['name']
            fora = jogo['awayTeam']['name']
            
            # --- LÓGICA DE ENTRADAS VARIADAS ---
            opcoes_vitoria = [f"Vitória {casa}", f"Vitória {fora}", "Empate"]
            opcoes_gols = ["Over 1.5", "Over 2.5", "Ambas Marcam"]
            opcoes_cantos = ["+8.5 Escanteios", "+9.5 Escanteios", "+10.5 Escanteios"]
            opcoes_dupla = ["1X", "X2", "12"]

            lista_palpites.append({
                "Dia": data_obj.strftime("%d/%m"),
                "Hora": data_obj.strftime("%H:%M"),
                "Confronto": f"{casa} vs {fora}",
                "Vencedor": random.choice(opcoes_vitoria),
                "Dupla": random.choice(opcoes_dupla),
                "Gols": random.choice(opcoes_gols),
                "Escanteios": random.choice(opcoes_cantos),
                "Confianca": f"{random.randint(86, 98)}%" # Fica fixo no CSV
            })
        
        df = pd.DataFrame(lista_palpites)
        df.to_csv('palpites.csv', index=False)
        print("✅ Dados detalhados salvos com sucesso!")

if __name__ == "__main__":
    gerar_palpites()
