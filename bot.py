import pandas as pd
import requests
from datetime import datetime
import pytz
import os

# Chave vinda dos Secrets do GitHub
API_KEY = os.getenv('API_FOOTBALL_KEY')

# Ligas principais para garantir bons dados
LIGAS = [71, 2, 140, 39, 61, 135, 78, 72, 73, 40, 307, 141, 143, 94, 253, 135, 79, 1, 3, 13, 11]

def rodar():
    fuso = pytz.timezone('America/Sao_Paulo')
    hoje = datetime.now(fuso).strftime('%Y-%m-%d')
    headers = {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': API_KEY}
    
    final = []
    print(f"--- INICIANDO ANÁLISE PRO: {hoje} ---")

    for liga in LIGAS:
        for ano in [2026, 2025]:
            url = f"https://v3.football.api-sports.io/fixtures?date={hoje}&league={liga}&season={ano}"
            try:
                r = requests.get(url, headers=headers, timeout=15).json()
                jogos = r.get('response', [])
                if not jogos: continue

                for j in jogos:
                    status = j['fixture']['status']['short']
                    if status not in ['NS', 'TBD']: continue

                    f_id = j['fixture']['id']
                    
                    # BUSCA PREVISÃO DETALHADA (Predictions)
                    url_p = f"https://v3.football.api-sports.io/predictions?fixture={f_id}"
                    res_p = requests.get(url_p, headers=headers).json()
                    p = res_p['response'][0] if res_p.get('response') else {}

                    palpite_final = "Mais de 1.5 Gols" # Padrão de segurança

                    if p:
                        # 1. Lógica de Escanteios (Corners)
                        comparacao_cantos = p['comparison'].get('corners', {}).get('home', '50%')
                        if float(comparacao_cantos.replace('%','')) > 60:
                            palpite_final = "Over 8.5 Cantos (Jogo)"
                        elif float(comparacao_cantos.replace('%','')) > 55:
                            palpite_final = "Cantos HT (Over 3.5)"
                        
                        # 2. Lógica de Gols e Tempos
                        elif p['predictions']['goals']['home'] and "-" in str(p['predictions']['goals']['home']):
                            palpite_final = "Gol no 1º Tempo"
                        
                        elif p['comparison']['poisson']['home'] > p['comparison']['poisson']['away']:
                            palpite_final = f"Vencer um dos Tempos: {j['teams']['home']['name']}"
                        
                        elif p['comparison']['att']['home'] > "70%":
                            palpite_final = "Mais de 1.5 Gols Equipe Casa"

                    hora = datetime.fromisoformat(j['fixture']['date'].replace('Z', '+00:00')).astimezone(fuso).strftime('%H:%M')
                    
                    final.append({
                        'Hora': hora,
                        'Liga': j['league']['name'],
                        'TimeCasa': j['teams']['home']['name'],
                        'LogoCasa': j['teams']['home']['logo'],
                        'TimeFora': j['teams']['away']['name'],
                        'LogoFora': j['teams']['away']['logo'],
                        'Palpite': palpite_final
                    })
                break 
            except: continue

    if final:
        pd.DataFrame(final).sort_values('Hora').to_csv('palpites.csv', index=False)
        print(f"✅ {len(final)} palpites detalhados gerados!")

if __name__ == "__main__":
    rodar()
