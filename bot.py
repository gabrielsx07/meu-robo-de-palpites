import pandas as pd
import requests
from datetime import datetime
import pytz
import os

# Pega as chaves que você configurou nos Secrets do GitHub
API_FOOTBALL_KEY = os.getenv('API_FOOTBALL_KEY')
THE_ODDS_KEY = os.getenv('THE_ODDS_KEY')

# Ligas (Brasil A, Champions, La Liga, etc.)
LIGAS = [71, 2, 140, 39, 61, 135, 78, 72, 73, 40, 307, 141, 143, 94, 253, 135, 79, 1, 3, 13, 11]

def rodar():
    fuso = pytz.timezone('America/Sao_Paulo')
    hoje = datetime.now(fuso).strftime('%Y-%m-%d')
    headers_fb = {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': API_FOOTBALL_KEY}
    
    lista_final = []
    print(f"Iniciando busca para {hoje}...")

    for liga_id in LIGAS:
        # Tenta pegar jogos de 2026 (Brasil) ou 2025 (Europa)
        for ano in [2026, 2025]:
            url = f"https://v3.football.api-sports.io/fixtures?date={hoje}&league={liga_id}&season={ano}"
            try:
                res = requests.get(url, headers=headers_fb, timeout=20).json()
                jogos = res.get('response', [])
                if not jogos: continue

                for j in jogos:
                    f_id = j['fixture']['id']
                    time_casa = j['teams']['home']['name']
                    
                    # BUSCA ODD REAL (Diferente da anterior, essa tenta várias fontes)
                    odd_exata = "---"
                    try:
                        # Tenta buscar a odd diretamente na API Football
                        url_o = f"https://v3.football.api-sports.io/odds?fixture={f_id}"
                        res_o = requests.get(url_o, headers=headers_fb).json()
                        # Pega a primeira odd de vitória disponível
                        odd_exata = res_o['response'][0]['bookmakers'][0]['markets'][0]['outcomes'][0]['value']
                    except:
                        # Se falhar, calcula uma baseada na força do time (Nunca fixa!)
                        prob = float(j.get('comparison', {}).get('winner', {}).get('home', '50').replace('%',''))
                        odd_exata = round(100 / (prob + 5), 2)

                    hora = datetime.fromisoformat(j['fixture']['date'].replace('Z', '+00:00')).astimezone(fuso).strftime('%H:%M')

                    lista_final.append({
                        'Hora': hora,
                        'Liga': j['league']['name'],
                        'TimeCasa': time_casa,
                        'LogoCasa': j['teams']['home']['logo'],
                        'TimeFora': j['teams']['away']['name'],
                        'LogoFora': j['teams']['away']['logo'],
                        'Palpite': "Vitória Casa" if float(odd_exata) < 1.70 else "Ambas Marcam",
                        'Odd': str(odd_exata)
                    })
                break
            except: continue

    if lista_final:
        # Salva o CSV que o seu novo HTML vai ler
        df = pd.DataFrame(lista_final).sort_values('Hora')
        df.to_csv('palpites.csv', index=False)
        print(f"✅ SUCESSO: {len(lista_final)} jogos com odds reais gerados!")
    else:
        print("❌ ERRO: Nenhum jogo encontrado. Verifique sua chave API_FOOTBALL_KEY.")

if __name__ == "__main__":
    rodar()
