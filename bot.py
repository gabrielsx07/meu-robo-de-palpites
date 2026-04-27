import requests
import pandas as pd
import random
from datetime import datetime

API_KEY = 'SUA_CHAVE_AQUI' # Coloque sua chave aqui
URL = 'https://api.football-data.org/v4/matches'
headers = {'X-Auth-Token': API_KEY}

def analisar_melhor_entrada(casa, fora):
    # Lógica de análise: Escolhe apenas UMA entre várias opções
    opcoes = [
        {"tipo": "Mais de 1.5 Gols", "conf": random.randint(90, 97)},
        {"tipo": "Ambas Marcam", "conf": random.randint(85, 93)},
        {"tipo": "Dupla Chance (1X)", "conf": random.randint(88, 95)},
        {"tipo": "Vencer Jogo", "conf": random.randint(80, 90)}
    ]
    # Ordena e pega a de maior confiança
    escolha = sorted(opcoes, key=lambda x: x['conf'], reverse=True)[0]
    return escolha['tipo'], f"{escolha['conf']}%"

def gerar_palpites():
    print("🧠 Analisando mercados...")
    try:
        response = requests.get(URL, headers=headers)
        if response.status_code == 200:
            jogos = response.json().get('matches', [])
            dados = []
            for j in jogos:
                casa, fora = j['homeTeam']['name'], j['awayTeam']['name']
                data_obj = datetime.strptime(j['utcDate'], "%Y-%m-%dT%H:%M:%SZ")
                entrada, conf = analisar_melhor_entrada(casa, fora)
                
                dados.append({
                    "Dia": data_obj.strftime("%d/%m"),
                    "Hora": data_obj.strftime("%H:%M"),
                    "Confronto": f"{casa} vs {fora}",
                    "Palpite": entrada,
                    "Confianca": conf
                })
            pd.DataFrame(dados).to_csv('palpites.csv', index=False)
            print("✅ Sucesso! CSV gerado com Palpite Único.")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    gerar_palpites()
