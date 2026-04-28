import pandas as pd
import requests
from datetime import datetime, timedelta
import pytz
import os

API_KEY = os.getenv('API_FOOTBALL_KEY')
# Ligas principais para não dar erro de limite
LIGAS = [71, 2, 140, 39, 61, 135, 78, 72, 73, 40, 307, 141, 143, 94, 253, 135, 79, 1, 3, 13, 11]

def rodar():
    fuso = pytz.timezone('America/Sao_Paulo')
    agora = datetime.now(fuso)
    
    # Busca hoje e amanhã para garantir que sempre tenha jogo na tela
    datas = [agora.strftime('%Y-%m-%d'), (agora + timedelta(days=1)).strftime('%Y-%m-%d')]
    
    headers = {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': API_KEY}
    final = []

    print(f"Limpando e buscando novos jogos...")

    for data_busca in datas:
        for liga in LIGAS:
            for ano in [2026, 2025]:
                url = f"https://v3.football.api-sports.io/fixtures?date={data_busca}&league={liga}&season={ano}"
                try:
                    r = requests.get(url, headers=headers, timeout=15).json()
                    jogos = r.get('response', [])
                    if not jogos: continue

                    for j in jogos:
                        status = j['fixture']['status']['short']
                        if status not in ['NS', 'TBD']: continue # Só quem não começou
                        
                        # Palpites Detalhados baseados na força do time
                        forca_casa = float(j.get('comparison', {}).get('winner', {}).get('home', '50').replace('%',''))
                        
                        if forca_casa > 70: palpite = "Vencer um dos Tempos"
                        elif forca_casa > 55: palpite = "Escanteios: Over 8.5"
                        elif forca_casa > 40: palpite = "Gol no 1º Tempo"
                        else: palpite = "Mais de 1.5 Gols"

                        data_jogo = datetime.fromisoformat(j['fixture']['date'].replace('Z', '+00:00')).astimezone(fuso)
                        
                        # Se for jogo de hoje e já passou, pula
                        if data_busca == datas[0] and data_jogo < agora: continue

                        final.append({
                            'Hora': data_jogo.strftime('%d/%m %H:%M'),
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
        print(f"✅ {len(final)} jogos novos salvos!")
    else:
        # Se a API falhar, gera um aviso claro no CSV
        with open('palpites.csv', 'w') as f:
            f.write("Hora,Liga,TimeCasa,LogoCasa,TimeFora,LogoFora,Palpite\n")
            f.write(f"00:00,Aviso,Sem Jogos Disponiveis,,Tente Mais Tarde,,API Vazia")

if __name__ == "__main__":
    rodar()
