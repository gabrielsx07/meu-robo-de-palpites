import pandas as pd
import requests
from datetime import datetime
import pytz

def buscar_jogos_vips():
    fuso = pytz.timezone('America/Sao_Paulo')
    hoje = datetime.now(fuso).strftime('%Y-%m-%d')
    
    url = "https://v3.football.api-sports.io/fixtures"
    minha_chave = "b4533c0123994fd0a1a0d3a9d125d5ed" # <--- COLOQUE SUA CHAVE AQUI
    
    headers = {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': minha_chave}
    params = {'date': hoje}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        jogos = response.json().get('response', [])
        lista_final = []

        # Filtro de status: só aceita jogos que não acabaram
        status_permitidos = ['TBD', 'NS', '1H', 'HT', '2H', 'ET', 'BT', 'LIVE']

        for item in jogos:
            fixture = item.get('fixture', {})
            if fixture.get('status', {}).get('short') not in status_permitidos:
                continue

            data_obj = datetime.fromisoformat(fixture.get('date').replace('Z', '+00:00'))
            hora_bra = data_obj.astimezone(fuso).strftime('%H:%M')
            
            # Lógica de Palpite Detalhado
            palpite = "Escanteios: Over 8.5"
            if item.get('teams', {}).get('home', {}).get('winner'):
                palpite = "Vitória Casa / +1.5 Gols"
            elif "Série A" in item.get('league', {}).get('name'):
                palpite = "Ambas Marcam / 1º Tempo +0.5 Gols"

            lista_final.append({
                'Hora': hora_bra,
                'Liga': item.get('league', {}).get('name'),
                'TimeCasa': item['teams']['home']['name'],
                'LogoCasa': item['teams']['home']['logo'],
                'TimeFora': item['teams']['away']['name'],
                'LogoFora': item['teams']['away']['logo'],
                'Palpite': palpite,
                'Odd': "1.85", # Valor simulado (API gratuita limita Odds reais)
                'Status': fixture.get('status', {}).get('long')
            })

        df = pd.DataFrame(lista_final)
        df.to_csv('palpites.csv', index=False)
        print("✅ CSV Atualizado!")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    buscar_jogos_vips()
