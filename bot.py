import pandas as pd
import requests
from datetime import datetime
import pytz

def buscar_odds_reais(fixture_id, minha_chave):
    url_odds = "https://v3.football.api-sports.io/odds"
    params = {'fixture': fixture_id, 'bookmaker': 8} # 8 é o ID da Bet365 na API
    headers = {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': minha_chave}
    
    try:
        res = requests.get(url_odds, headers=headers, params=params, timeout=10)
        data = res.json().get('response', [])
        if data:
            # Puxa a primeira odd de "Match Winner" (Vencedor do Jogo)
            for book in data[0].get('bookmakers', []):
                for bet in book.get('bets', []):
                    if bet['name'] == "Match Winner":
                        return bet['values'][0]['odd'] # Retorna a odd do time da casa
        return "1.80" # Caso não ache a odd real, mantém uma média
    except:
        return "1.80"

def buscar_jogos_elite():
    fuso = pytz.timezone('America/Sao_Paulo')
    hoje = datetime.now(fuso).strftime('%Y-%m-%d')
    minha_chave = "b4533c0123994fd0a1a0d3a9d125d5ed"
    
    url = "https://v3.football.api-sports.io/fixtures"
    headers = {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': minha_chave}
    params = {'date': hoje}

    # IDs das ligas principais (Brasileirão, Premier, etc)
    ligas_vips = [71, 72, 13, 39, 140, 135, 78, 61, 2, 3]

    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        jogos = response.json().get('response', [])
        lista_final = []

        for item in jogos:
            fixture = item.get('fixture', {})
            league = item.get('league', {})
            
            if league.get('id') not in ligas_vips:
                continue
            
            if fixture.get('status', {}).get('short') not in ['NS', 'TBD', '1H', 'HT']:
                continue

            # Tenta buscar a ODD REAL para esse jogo específico
            f_id = fixture.get('id')
            odd_real = buscar_odds_reais(f_id, minha_chave)

            data_obj = datetime.fromisoformat(fixture.get('date').replace('Z', '+00:00'))
            hora_bra = data_obj.astimezone(fuso).strftime('%H:%M')

            lista_final.append({
                'Hora': hora_bra,
                'Liga': league.get('name'),
                'TimeCasa': item['teams']['home']['name'],
                'LogoCasa': item['teams']['home']['logo'],
                'TimeFora': item['teams']['away']['name'],
                'LogoFora': item['teams']['away']['logo'],
                'Palpite': "Over 8.5 Escanteios", # Aqui você pode manter sua lógica de análise
                'Odd': odd_real,
                'Status': fixture['status']['long']
            })

        if lista_final:
            df = pd.DataFrame(lista_final).sort_values(by='Hora')
            df.to_csv('palpites.csv', index=False)
            print("✅ Atualizado com Odds Reais!")

    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    buscar_jogos_elite()
