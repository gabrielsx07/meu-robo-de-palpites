import pandas as pd
import requests
from datetime import datetime
import pytz
import os

# Pega a chave do Cofre (Secrets)
API_KEY = os.getenv('API_FOOTBALL_KEY')

# Ligas que trazem os melhores palpites
LIGAS = [71, 2, 140, 39, 61, 135, 78, 72, 73, 40, 307, 141, 143, 94, 253, 135, 79, 1, 3, 13, 11]

def rodar():
    fuso = pytz.timezone('America/Sao_Paulo')
    hoje = datetime.now(fuso).strftime('%Y-%m-%d')
    headers = {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': API_KEY}
    
    final = []
    print(f"--- ANALISANDO JOGOS PARA {hoje} ---")

    for liga in LIGAS:
        for ano in [2026, 2025]:
            url = f"https://v3.football.api-sports.io/fixtures?date={hoje}&league={liga}&season={ano}"
            try:
                r = requests.get(url, headers=headers, timeout=15).json()
                jogos = r.get('response', [])
                if not jogos: continue

                for j in jogos:
                    status = j['fixture']['status']['short']
                    # Só pega jogos que ainda vão começar
                    if status not in ['NS', 'TBD']: continue

                    f_id = j['fixture']['id']
                    
                    # 1. BUSCA ODD REAL
                    odd_val = None
                    try:
                        url_o = f"https://v3.football.api-sports.io/odds?fixture={f_id}"
                        res_o = requests.get(url_o, headers=headers).json()
                        # Tenta pegar a odd da vitória do time da casa
                        odd_val = res_o['response'][0]['bookmakers'][0]['markets'][0]['outcomes'][0]['value']
                    except:
                        # Se não tiver odd na API ainda, calcula uma baseada na força do time
                        prob = float(j.get('comparison', {}).get('winner', {}).get('home', '50').replace('%',''))
                        odd_val = round(100 / (prob + 3), 2)

                    # 2. INTELIGÊNCIA DE PALPITE
                    val = float(odd_val)
                    if val < 1.60:
                        palpite = "Vencer um dos Tempos"
                    elif val < 1.95:
                        palpite = "Casa Vence ou Empate"
                    elif val < 2.30:
                        palpite = "Over 1.5 Gols"
                    else:
                        palpite = "Ambas Marcam: Sim"

                    hora = datetime.fromisoformat(j['fixture']['date'].replace('Z', '+00:00')).astimezone(fuso).strftime('%H:%M')
                    
                    final.append({
                        'Hora': hora,
                        'Liga': j['league']['name'],
                        'TimeCasa': j['teams']['home']['name'],
                        'LogoCasa': j['teams']['home']['logo'],
                        'TimeFora': j['teams']['away']['name'],
                        'LogoFora': j['teams']['away']['logo'],
                        'Palpite': palpite,
                        'Odd': str(val)
                    })
                break 
            except: continue

    if final:
        # Salva e ordena por horário
        pd.DataFrame(final).sort_values('Hora').to_csv('palpites.csv', index=False)
        print(f"✅ SUCESSO: {len(final)} palpites inteligentes gerados!")
    else:
        print("⚠️ Nenhum jogo encontrado para hoje nas ligas selecionadas.")

if __name__ == "__main__":
    rodar()
