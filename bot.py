import pandas as pd
import requests
from datetime import datetime, timedelta
import pytz
import os

API_KEY = os.getenv('API_FOOTBALL_KEY')

# ADICIONEI: MLS (253), Libertadores (13), Sul-Americana (11), Japão (98) e México (262)
LIGAS = [71, 2, 140, 39, 61, 135, 78, 72, 73, 40, 307, 141, 143, 94, 253, 135, 79, 1, 3, 13, 11, 98, 262]

def rodar():
    fuso = pytz.timezone('America/Sao_Paulo')
    agora = datetime.now(fuso)
    hoje = agora.strftime('%Y-%m-%d')
    amanha = (agora + timedelta(days=1)).strftime('%Y-%m-%d')
    
    headers = {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': API_KEY}
    final = []

    # Busca hoje e amanhã para garantir volume
    for data_f in [hoje, amanha]:
        for liga in LIGAS:
            for ano in [2026, 2025]:
                url = f"https://v3.football.api-sports.io/fixtures?date={data_f}&league={liga}&season={ano}"
                try:
                    r = requests.get(url, headers=headers, timeout=15).json()
                    jogos = r.get('response', [])
                    if not jogos: continue

                    for j in jogos:
                        status = j['fixture']['status']['short']
                        if status not in ['NS', 'TBD', '1H', 'HT', '2H']: continue
                        
                        dt_jogo = datetime.fromisoformat(j['fixture']['date'].replace('Z', '+00:00')).astimezone(fuso)
                        
                        # Só ignora se o jogo já ACABOU (FT)
                        if status == 'FT': continue

                        # Lógica de Palpite Detalhado
                        # Usando a "Chance de Vitória" da API para decidir
                        home_win = j.get('comparison', {}).get('winner', {}).get('home', '50%').replace('%','')
                        home_win = float(home_win) if home_win else 50.0

                        if home_win > 60:
                            palpite = "Vencer um dos Tempos"
                        elif home_win > 45:
                            palpite = "Cantos: Over 8.5"
                        else:
                            palpite = "Gol no 1º Tempo"

                        final.append({
                            'Hora': dt_jogo.strftime('%d/%m %H:%M'),
                            'Liga': j['league']['name'],
                            'TimeCasa': j['teams']['home']['name'],
                            'LogoCasa': j['teams']['home']['logo'],
                            'TimeFora': j['teams']['away']['name'],
                            'LogoFora': j['teams']['away']['logo'],
                            'Palpite': palpite
                        })
                    break
                except: continue

    if final:
        df = pd.DataFrame(final).sort_values('Hora')
        df.to_csv('palpites.csv', index=False)
        print(f"✅ Sucesso: {len(final)} jogos encontrados!")
    else:
        pd.DataFrame([{'Hora': '--:--', 'Liga': 'Sistema', 'TimeCasa': 'Buscando', 'LogoCasa': '', 'TimeFora': 'Jogos Noturnos', 'LogoFora': '', 'Palpite': 'Aguarde'}]).to_csv('palpites.csv', index=False)

if __name__ == "__main__":
    rodar()
