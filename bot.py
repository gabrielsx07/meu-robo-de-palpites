import pandas as pd
import requests
from datetime import datetime, timedelta
import pytz
import os

API_KEY = os.getenv('API_FOOTBALL_KEY')
LIGAS = [71, 72, 39, 140, 135, 78, 61, 2, 3]

def rodar():
    fuso = pytz.timezone('America/Sao_Paulo')
    # Busca hoje e amanhã para garantir que o site nunca fique com jogo passado
    datas = [
        datetime.now(fuso).strftime('%Y-%m-%d'),
        (datetime.now(fuso) + timedelta(days=1)).strftime('%Y-%m-%d')
    ]
    
    headers = {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': API_KEY}
    final = []

    for data_busca in datas:
        for liga in LIGAS:
            for ano in [2026, 2025]:
                url = f"https://v3.football.api-sports.io/fixtures?date={data_busca}&league={liga}&season={ano}"
                try:
                    r = requests.get(url, headers=headers).json()
                    jogos = r.get('response', [])
                    if not jogos: continue

                    for j in jogos:
                        status = j['fixture']['status']['short']
                        # Pega apenas quem não começou
                        if status not in ['NS', 'TBD']: continue

                        # Inteligência de Palpite Simples (Escanteios/Gols)
                        vitoria_casa = float(j.get('comparison', {}).get('winner', {}).get('home', '50').replace('%',''))
                        
                        if vitoria_casa > 65: palpite = "Vencer um dos Tempos"
                        elif vitoria_casa > 50: palpite = "Over 8.5 Escanteios"
                        else: palpite = "Gol no 1º Tempo"

                        hora = datetime.fromisoformat(j['fixture']['date'].replace('Z', '+00:00')).astimezone(fuso).strftime('%d/%m %H:%M')
                        
                        final.append({
                            'Hora': hora,
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
        # Força a criação de um arquivo novo
        df = pd.DataFrame(final).sort_values('Hora')
        df.to_csv('palpites.csv', index=False)
        print(f"✅ CSV atualizado com {len(final)} jogos novos.")
    else:
        print("⚠️ Nenhum jogo novo encontrado.")

if __name__ == "__main__":
    rodar()
