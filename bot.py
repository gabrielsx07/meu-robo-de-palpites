import pandas as pd
import requests
from datetime import datetime, timedelta
import pytz
import os

API_KEY = os.getenv('API_FOOTBALL_KEY')
# Lista ampliada de ligas para garantir que sempre tenha jogo
LIGAS = [71, 2, 140, 39, 61, 135, 78, 72, 73, 40, 307, 141, 143, 94, 253, 135, 79, 1, 3, 13, 11]

def rodar():
    fuso = pytz.timezone('America/Sao_Paulo')
    agora = datetime.now(fuso)
    
    # Busca o que resta de hoje e os jogos de amanhã
    datas_para_buscar = [
        agora.strftime('%Y-%m-%d'),
        (agora + timedelta(days=1)).strftime('%Y-%m-%d')
    ]
    
    headers = {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': API_KEY}
    final = []

    for data_f in datas_para_buscar:
        for liga in LIGAS:
            for ano in [2026, 2025]:
                url = f"https://v3.football.api-sports.io/fixtures?date={data_f}&league={liga}&season={ano}"
                try:
                    r = requests.get(url, headers=headers, timeout=15).json()
                    jogos = r.get('response', [])
                    if not jogos: continue

                    for j in jogos:
                        status = j['fixture']['status']['short']
                        if status not in ['NS', 'TBD']: continue
                        
                        # Horário do jogo
                        dt_jogo = datetime.fromisoformat(j['fixture']['date'].replace('Z', '+00:00')).astimezone(fuso)
                        
                        # Se for jogo de hoje e já passou, pula
                        if dt_jogo < agora: continue

                        # PALPITE DETALHADO (Gols e Cantos)
                        # Usando poisson/força para decidir o palpite
                        casa_f = j.get('comparison', {}).get('winner', {}).get('home', '50%').replace('%','')
                        casa_f = float(casa_f) if casa_f else 50.0

                        if casa_f > 65: palpite = "Vitória Casa / Cantos"
                        elif casa_f > 50: palpite = "Over 1.5 Gols / Cantos HT"
                        else: palpite = "Ambas Marcam ou Over 2.5"

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
        # Ordena por data e hora
        df = pd.DataFrame(final).sort_values('Hora')
        df.to_csv('palpites.csv', index=False)
        print(f"✅ Sucesso: {len(final)} palpites para hoje/amanhã salvos!")
    else:
        # Se mesmo assim não achar nada, cria uma linha de aviso
        pd.DataFrame([{'Hora': '--:--', 'Liga': 'Aviso', 'TimeCasa': 'Novos Jogos', 'LogoCasa': '', 'TimeFora': 'Sendo Analisados', 'LogoFora': '', 'Palpite': 'Aguarde Atualização'}]).to_csv('palpites.csv', index=False)

if __name__ == "__main__":
    rodar()
