import pandas as pd
import requests
from datetime import datetime
import pytz
import os

API_KEY = os.getenv('API_FOOTBALL_KEY')

# Ligas que você quer no site
LIGAS = [71, 72, 39, 140, 135, 78, 61, 2, 3]

def rodar():
    fuso = pytz.timezone('America/Sao_Paulo')
    hoje = datetime.now(fuso).strftime('%Y-%m-%d')
    headers = {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': API_KEY}
    
    final = []
    print(f"--- GERANDO PALPITES REAIS PARA {hoje} ---")

    for liga in LIGAS:
        for ano in [2026, 2025]:
            url = f"https://v3.football.api-sports.io/fixtures?date={hoje}&league={liga}&season={ano}"
            try:
                r = requests.get(url, headers=headers, timeout=15).json()
                jogos = r.get('response', [])
                if not jogos: continue

                for j in jogos:
                    status = j['fixture']['status']['short']
                    # Só pega jogo que não começou (NS) ou está no intervalo (HT)
                    if status not in ['NS', 'TBD', 'HT']: continue

                    f_id = j['fixture']['id']
                    
                    # TENTA PEGAR ODD REAL, SE NÃO TIVER, CALCULA PELA PROBABILIDADE
                    odd_final = None
                    try:
                        url_o = f"https://v3.football.api-sports.io/odds?fixture={f_id}"
                        res_o = requests.get(url_o, headers=headers).json()
                        odd_final = res_o['response'][0]['bookmakers'][0]['markets'][0]['outcomes'][0]['value']
                    except:
                        # Cálculo inteligente: probabilidade da API + margem
                        prob = float(j.get('comparison', {}).get('winner', {}).get('home', '50').replace('%',''))
                        odd_final = round(100 / (prob + 3), 2)

                    hora = datetime.fromisoformat(j['fixture']['date'].replace('Z', '+00:00')).astimezone(fuso).strftime('%H:%M')
                    
                    # Define palpite baseado na força da Odd
                    val_odd = float(odd_final)
                    if val_odd < 1.65: palpite = "Vitória Casa"
                    elif val_odd < 2.05: palpite = "Over 0.5 Gols HT"
                    else: palpite = "Ambas Marcam: Sim"

                    final.append({
                        'Hora': hora,
                        'Liga': j['league']['name'],
                        'TimeCasa': j['teams']['home']['name'],
                        'LogoCasa': j['teams']['home']['logo'],
                        'TimeFora': j['teams']['away']['name'],
                        'LogoFora': j['teams']['away']['logo'],
                        'Palpite': palpite,
                        'Odd': str(val_odd)
                    })
                break
            except: continue

    if final:
        pd.DataFrame(final).sort_values('Hora').to_csv('palpites.csv', index=False)
        print(f"✅ SUCESSO: {len(final)} palpites reais postados!")
    else:
        print("⚠️ Sem jogos para as ligas selecionadas no momento.")

if __name__ == "__main__":
    rodar()
