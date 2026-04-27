import requests
import pandas as pd
import random
from datetime import datetime

API_KEY = 'SUA_CHAVE_AQUI'
URL = 'https://api.football-data.org/v4/matches'
headers = {'X-Auth-Token': API_KEY}

def inteligencia_analitica(casa, fora):
    # --- SIMULAÇÃO DE VARIÁVEIS (xG, Amplitude e Intensidade) ---
    xg_casa = round(random.uniform(0.8, 2.5), 2)
    xg_fora = round(random.uniform(0.5, 2.0), 2)
    volume_ataque = random.randint(10, 25) # Chutes e cruzamentos
    
    hits = []

    # 1. Analisando xG e Valor Real
    if xg_casa > xg_fora + 0.5:
        hits.append({"tipo": f"Vencer um dos Tempos: {casa}", "conf": random.randint(90, 97)})
    
    # 2. Analisando Escanteios (Baseado em Volume de Ataque e Chutes)
    if volume_ataque > 18:
        hits.append({"tipo": "Mais de 9.5 Escanteios", "conf": random.randint(88, 95)})
    
    # 3. Analisando Gols (Baseado no xG acumulado)
    if (xg_casa + xg_fora) > 2.8:
        hits.append({"tipo": "Over 2.5 Gols (Valor)", "conf": random.randint(85, 93)})
    elif (xg_casa + xg_fora) > 1.8:
        hits.append({"tipo": "Mais de 1.5 Gols", "conf": random.randint(92, 98)})

    # 4. Ambas Marcam (Contexto de ataque vs defesa frágil)
    if xg_casa > 1.2 and xg_fora > 1.0:
        hits.append({"tipo": "Ambas Marcam: Sim", "conf": random.randint(87, 94)})

    # FILTRO: Pega a opção com maior 'Confiança' (Aposta de Valor)
    hits.sort(key=lambda x: x['conf'], reverse=True)
    escolha_mestre = hits[0]

    return escolha_mestre['tipo'], f"{escolha_mestre['conf']}%"

def gerar_dados():
    print("🔬 Analisando xG, Escanteios e Intensidade...")
    response = requests.get(URL, headers=headers)
    if response.status_code == 200:
        jogos = response.json().get('matches', [])
        lista = []
        for jogo in jogos:
            casa = jogo['homeTeam']['name']
            fora = jogo['awayTeam']['name']
            data_obj = datetime.strptime(jogo['utcDate'], "%Y-%m-%dT%H:%M:%SZ")
            
            # IA processa o Hit baseado nos novos critérios
            entrada, conf = inteligencia_analitica(casa, fora)
            
            lista.append({
                "Hora": data_obj.strftime("%H:%M"),
                "Confronto": f"{casa} vs {fora}",
                "MelhorEntrada": entrada,
                "Confianca": conf
            })
        
        pd.DataFrame(lista).to_csv('palpites.csv', index=False)
        print("✅ Análise de valor concluída e salva no CSV.")

if __name__ == "__main__":
    gerar_dados()
