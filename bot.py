import pandas as pd
import requests
from datetime import datetime
import pytz
import os

# Pega a chave do cofre do GitHub
API_KEY = os.getenv('API_FOOTBALL_KEY')

# Ligas variadas para garantir volume de jogos
LIGAS = [71, 2, 140, 39, 61, 135, 78, 72, 73, 40, 307, 141, 143, 94, 253, 135, 79, 1, 3, 13, 11]

def rodar():
    fuso = pytz.timezone('America/Sao_Paulo')
    hoje = datetime.now(fuso).strftime('%Y-%m-%d')
    headers = {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': API_KEY}
    
    dados_concluidos = []
    print(f"Buscando jogos para: {hoje}")

    for liga in LIGAS:
        # Testa temporadas 2026 e 2025
        for ano in [2026, 2025]:
            url = f"https://v3.football.api-sports.io/fixtures?date={hoje}&league={liga}&season={ano}"
            try:
                r = requests.get(url, headers=headers, timeout=20).json()
                jogos = r.get('response', [])
                if not jogos: continue

                for j in jogos:
                    f_id = j['fixture']['id']
                    status = j['fixture']['status']['short']
                    if status not in ['NS', 'TBD', '1H', 'HT']: continue

                    # Tenta pegar a ODD real
                    odd_val = "1.85" # Valor base
                    try:
                        url_o = f"https://v3.football.api-sports.io/odds?fixture={f_id}"
                        res_o = requests.get(url_o, headers=headers).json()
                        odd_val = res_o['response'][0]['bookmakers'][0]['markets'][0]['outcomes'][0]['value']
                    except:
                        # Se falhar a odd, calcula pela probabilidade
                        prob = float(j.get('comparison', {}).get('winner', {}).get('home', '50').replace('%',''))
                        odd_val = round(100 / (prob + 2), 2)

                    hora = datetime.fromisoformat(j['fixture']['date'].replace('Z', '+00:00')).astimezone(fuso).strftime('%H:%M')
                    
                    dados_concluidos.append([
                        hora,
                        j['league']['name'],
                        j['teams']['home']['name'],
                        j['teams']['home']['logo'],
                        j['teams']['away']['name'],
                        j['teams']['away']['logo'],
                        "Vitória Casa" if float(odd_val) < 1.80 else "Ambas Marcam",
                        str(odd_val)
                    ])
                break 
            except: continue

    # CRUCIAL: Criar o DataFrame com colunas certas e forçar o salvamento
    if dados_concluidos:
        df = pd.DataFrame(dados_concluidos, columns=['Hora', 'Liga', 'TimeCasa', 'LogoCasa', 'TimeFora', 'LogoFora', 'Palpite', 'Odd'])
        df.to_csv('palpites.csv', index=False, encoding='utf-8')
        print(f"✅ SUCESSO: {len(dados_concluidos)} jogos salvos no CSV!")
    else:
        # Cria um CSV vazio mas com cabeçalho para não quebrar o site
        df = pd.DataFrame(columns=['Hora', 'Liga', 'TimeCasa', 'LogoCasa', 'TimeFora', 'LogoFora', 'Palpite', 'Odd'])
        df.to_csv('palpites.csv', index=False)
        print("⚠️ Nenhum jogo encontrado hoje.")

if __name__ == "__main__":
    rodar()
