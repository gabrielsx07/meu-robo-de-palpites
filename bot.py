import pandas as pd
import requests
from datetime import datetime
import pytz
import os

API_KEY = os.getenv('API_FOOTBALL_KEY')
# Principais Ligas
LIGAS = [71, 2, 140, 39, 61, 135, 78, 72, 73, 40, 307, 141, 143, 94, 253, 135, 79, 1, 3, 13, 11]

def rodar():
    # Define o fuso horário de Brasília
    fuso_br = pytz.timezone('America/Sao_Paulo')
    agora_br = datetime.now(fuso_br)
    hoje_br = agora_br.strftime('%Y-%m-%d')
    
    headers = {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': API_KEY}
    
    final = []
    print(f"--- BUSCANDO JOGOS QUE COMEÇAM A PARTIR DE: {agora_br.strftime('%H:%M')} ---")

    for liga in LIGAS:
        for ano in [2026, 2025]:
            url = f"https://v3.football.api-sports.io/fixtures?date={hoje_br}&league={liga}&season={ano}"
            try:
                r = requests.get(url, headers=headers).json()
                jogos = r.get('response', [])
                if not jogos: continue

                for j in jogos:
                    # 1. FILTRO DE HORÁRIO: Só pega jogo que ainda não começou
                    status = j['fixture']['status']['short']
                    if status not in ['NS', 'TBD']: continue

                    # 2. CONVERTE HORÁRIO DO JOGO PARA BRASÍLIA
                    data_jogo = datetime.fromisoformat(j['fixture']['date'].replace('Z', '+00:00')).astimezone(fuso_br)
                    
                    # Se o jogo já passou do horário atual, ignora
                    if data_jogo < agora_br: continue

                    f_id = j['fixture']['id']
                    
                    # 3. BUSCA PREVISÕES DETALHADAS (CANTOS/GOLS)
                    url_p = f"https://v3.football.api-sports.io/predictions?fixture={f_id}"
                    res_p = requests.get(url_p, headers=headers).json()
                    
                    palpite_final = "Mais de 1.5 Gols" # Padrão
                    
                    if res_p.get('response'):
                        p = res_p['response'][0]
                        
                        # Lógica para Escanteios
                        cantos_home = float(p['comparison']['corners']['home'].replace('%','')) if p['comparison']['corners']['home'] else 0
                        # Lógica para Gols no 1º Tempo
                        prob_gols = p['predictions']['goals']['home']
                        
                        opcoes = []
                        if cantos_home > 60:
                            opcoes.append("Over 8.5 Cantos")
                            opcoes.append("Cantos HT (1º Tempo)")
                        
                        if p['comparison']['att']['home'] and float(p['comparison']['att']['home'].replace('%','')) > 65:
                            opcoes.append(f"Vencer um dos Tempos")
                        
                        if p['predictions']['win_or_draw']:
                            opcoes.append("Gol no 1º Tempo")
                        
                        # Seleciona o palpite mais forte da lista
                        palpite_final = opcoes[0] if opcoes else "Mais de 1.5 Gols"

                    final.append({
                        'Hora': data_jogo.strftime('%H:%M'),
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
        # Ordena para os jogos mais próximos aparecerem primeiro
        df = pd.DataFrame(final).sort_values('Hora')
        df.to_csv('palpites.csv', index=False)
        print(f"✅ Sucesso: {len(final)} jogos futuros encontrados.")
    else:
        # Caso não tenha mais jogos hoje, busca os de amanhã
        print("⚠️ Sem jogos restantes para hoje. O robô buscará os de amanhã na próxima execução.")

if __name__ == "__main__":
    rodar()
