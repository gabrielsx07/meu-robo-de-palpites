import pandas as pd
import requests
from datetime import datetime, timedelta
import pytz
import os

# Pega as chaves dos Secrets do GitHub
API_KEY = os.getenv('API_FOOTBALL_KEY')

# Ligas que mais geram dados na API
LIGAS = [71, 72, 39, 140, 135, 78, 61, 2, 3] 

def rodar():
    fuso = pytz.timezone('America/Sao_Paulo')
    # Busca 3 dias para garantir que o site tenha volume
    datas = [
        (datetime.now(fuso) + timedelta(days=i)).strftime('%Y-%m-%d')
        for i in range(3)
    ]
    
    headers = {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': API_KEY}
    final = []

    print(f"--- INICIANDO BUSCA BLINDADA ---")

    for data_busca in datas:
        for liga in LIGAS:
            # Testa temporadas 2026 (Brasil) e 2025 (Europa)
            for ano in [2026, 2025]:
                url = f"https://v3.football.api-sports.io/fixtures?date={data_busca}&league={liga}&season={ano}"
                try:
                    r = requests.get(url, headers=headers, timeout=15).json()
                    jogos = r.get('response', [])
                    if not jogos: continue

                    for j in jogos:
                        f_id = j['fixture']['id']
                        time_casa = j['teams']['home']['name']
                        
                        # Tenta pegar odd real, se falhar, calcula pela probabilidade
                        odd_val = None
                        try:
                            url_o = f"https://v3.football.api-sports.io/odds?fixture={f_id}"
                            res_o = requests.get(url_o, headers=headers, timeout=10).json()
                            odd_val = res_o['response'][0]['bookmakers'][0]['markets'][0]['outcomes'][0]['value']
                        except:
                            # Cálculo de backup caso a API de odds esteja lenta
                            prob = float(j.get('comparison', {}).get('winner', {}).get('home', '50').replace('%',''))
                            odd_val = round(100 / (prob + 2), 2)

                        hora_br = datetime.fromisoformat(j['fixture']['date'].replace('Z', '+00:00')).astimezone(fuso).strftime('%d/%m %H:%M')
                        
                        final.append({
                            'Hora': hora_br,
                            'Liga': j['league']['name'],
                            'TimeCasa': time_casa,
                            'LogoCasa': j['teams']['home']['logo'],
                            'TimeFora': j['teams']['away']['name'],
                            'LogoFora': j['teams']['away']['logo'],
                            'Palpite': "Casa Vence" if float(odd_val) < 1.80 else "Ambas Marcam",
                            'Odd': str(odd_val)
                        })
                    break # Se achou jogos no ano, pula pro próximo
                except Exception as e:
                    print(f"Erro na liga {liga}: {e}")
                    continue

    if final:
        df = pd.DataFrame(final).sort_values('Hora')
        df.to_csv('palpites.csv', index=False)
        print(f"✅ SUCESSO: {len(final)} palpites salvos no CSV!")
    else:
        # Se der tudo errado, ele gera uma linha fake só pra você saber que o robô está vivo
        pd.DataFrame([{'Hora': '00:00', 'Liga': 'Sistema', 'TimeCasa': 'Aguardando', 'LogoCasa': '', 'TimeFora': 'Novos Jogos', 'LogoFora': '', 'Palpite': 'Update', 'Odd': '1.00'}]).to_csv('palpites.csv', index=False)
        print("⚠️ Nenhum jogo real encontrado, arquivo de segurança gerado.")

if __name__ == "__main__":
    rodar()
