import pandas as pd
import requests
from datetime import datetime
import pytz
import os

API_KEY = os.getenv('API_FOOTBALL_KEY')
LIGAS = [71, 72, 39, 140, 135, 78, 61, 2, 3]

def rodar():
    fuso = pytz.timezone('America/Sao_Paulo')
    hoje = datetime.now(fuso).strftime('%Y-%m-%d')
    headers = {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': API_KEY}
    
    final = []
    print(f"--- GERANDO PALPITES DETALHADOS PARA {hoje} ---")

    for liga in LIGAS:
        for ano in [2026, 2025]:
            url = f"https://v3.football.api-sports.io/fixtures?date={hoje}&league={liga}&season={ano}"
            try:
                r = requests.get(url, headers=headers).json()
                jogos = r.get('response', [])
                if not jogos: continue

                for j in jogos:
                    f_id = j['fixture']['id']
                    
                    # BUSCA PREVISÃO DETALHADA DO JOGO
                    url_p = f"https://v3.football.api-sports.io/predictions?fixture={f_id}"
                    res_p = requests.get(url_p, headers=headers).json()
                    p = res_p['response'][0] if res_p.get('response') else {}

                    # Lógica de Palpites Detalhados
                    if p:
                        # Gols e Tempos
                        gols_previstos = p['goals']['home'] if p['goals']['home'] else "1.5"
                        escanteios = p['comparison']['corners']['home'] if p['comparison']['corners'] else "50%"
                        
                        # Criando uma lista de palpites para escolher o melhor
                        opcoes = []
                        if float(escanteios.replace('%','')) > 60:
                            opcoes.append(f"Mais de 8.5 Cantos")
                            opcoes.append(f"Cantos HT (Over 3.5)")
                        
                        if p['comparison']['poisson']['home'] > p['comparison']['poisson']['away']:
                            opcoes.append(f"Vencer um dos tempos: {j['teams']['home']['name']}")
                        
                        if p['predictions']['goals']['home'] and "-" in p['predictions']['goals']['home']:
                            opcoes.append("Gol no 1º Tempo")
                        
                        opcoes.append("Mais de 1.5 Gols") # Segurança
                        
                        palpite_final = opcoes[0] if opcoes else "Ambas Marcam"
                    else:
                        palpite_final = "Análise em Processamento"

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
        print("✅ Sucesso! Palpites detalhados gerados.")

if __name__ == "__main__":
    rodar()
