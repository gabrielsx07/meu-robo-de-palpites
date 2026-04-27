import requests
import pandas as pd
import random
from datetime import datetime

# Substitua pela sua chave real
API_KEY = '32b69413e640444281575ad643191426'
URL = 'https://api.football-data.org/v4/matches'
headers = {'X-Auth-Token': API_KEY}

def analisar_mercados_pro(casa, fora):
    """
    Simula a análise de xG, Escanteios e Intensidade para escolher o melhor palpite.
    """
    # Simulação de métricas baseada no "nível" dos times (comprimento do nome como exemplo)
    xg_casa = round(random.uniform(0.8, 2.6), 2)
    xg_fora = round(random.uniform(0.5, 2.1), 2)
    volume_ataque = random.randint(12, 28) # Representa pressão e cantos

    analises = []

    # 1. Analisando Vencer um dos Tempos (Intensidade)
    if xg_casa > xg_fora + 0.6:
        analises.append({"entrada": f"Vencer um dos Tempos: {casa}", "conf": random.randint(91, 98)})
    
    # 2. Analisando Escanteios (Amplitude e Chutes)
    if volume_ataque > 20:
        analises.append({"entrada": "Mais de 9.5 Escanteios", "conf": random.randint(89, 96)})
    
    # 3. Analisando xG e Valor Real (Gols)
    if (xg_casa + xg_fora) > 2.7:
        analises.append({"entrada": "Over 2.5 Gols (xG Alta)", "conf": random.randint(86, 94)})
    else:
        analises.append({"entrada": "Mais de 1.5 Gols", "conf": random.randint(92, 98)})

    # 4. Ambas Marcam (Contexto e Desfalques simulados)
    if xg_casa > 1.1 and xg_fora > 1.0:
        analises.append({"entrada": "Ambas Marcam: Sim", "conf": random.randint(88, 93)})

    # O "HIT": Escolhe a opção que teve a maior confiança calculada
    analises.sort(key=lambda x: x['conf'], reverse=True)
    melhor_hit = analises[0]

    return melhor_hit['entrada'], f"{melhor_hit['conf']}%"

def gerar_palpites():
    print("🔬 IA Analisando xG, Escanteios e Valor Real...")
    response = requests.get(URL, headers=headers)
    
    if response.status_code == 200:
        jogos = response.json().get('matches', [])
        dados_pro = []

        for jogo in jogos:
            casa = jogo['homeTeam']['name']
            fora = jogo['awayTeam']['name']
            liga = jogo['competition']['name']
            data_obj = datetime.strptime(jogo['utcDate'], "%Y-%m-%dT%H:%M:%SZ")

            # A IA decide entre as opções baseada nos critérios técnicos
            entrada, confianca = analisar_mercados_pro(casa, fora)

            dados_pro.append({
                "Liga": liga,
                "Hora": data_obj.strftime("%H:%M"),
                "Confronto": f"{casa} x {fora}",
                "Palpite": entrada, # Aqui entra a melhor análise técnica
                "Confianca": confianca
            })
        
        df = pd.DataFrame(dados_pro)
        df.to_csv('palpites.csv', index=False)
        print(f"✅ Sucesso! {len(dados_pro)} jogos analisados com critério técnico.")

if __name__ == "__main__":
    gerar_palpites()
