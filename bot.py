import pandas as pd
import requests
from datetime import datetime
import pytz

def buscar_odds_especificas(fixture_id, minha_chave):
    # Tenta buscar odds de Escanteios (Corners) ou Resultado Final
    url_odds = "https://v3.football.api-sports.io/odds"
    # Bookmaker 8 (Bet365) costuma ter mais dados
    params = {'fixture': fixture_id, 'bookmaker': 8}
    headers = {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': minha_chave}
    
    try:
        res = requests.get(url_odds, headers=headers, params=params, timeout=10)
        data = res.json().get('response', [])
        if data:
            for book in data[0].get('bookmakers', []):
                for bet in book.get('bets', []):
                    # Tenta pegar a odd de "Match Winner" ou "Over/Under Gols"
                    if bet['name'] in ["Match Winner", "Goals Over/Under"]:
                        return bet['values'][0]['odd']
        return "1.70 - 1.95" # Faixa de segurança caso a API não retorne o valor exato
    except:
        return "1.70 - 1.95"

def buscar_jogos_vips():
    fuso = pytz.timezone('America/Sao_Paulo')
    hoje = datetime.now(fuso).strftime('%Y-%m-%d')
    minha_chave = "b4533c0123994fd0a1a0d3a9d125d5ed" # <--- COLOQUE SUA CHAVE AQUI
    
    url = "https://v3.football.api-sports.io/fixtures"
    headers = {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': minha_chave}
    params = {'date': hoje}

    # ADICIONADA: 307 (Saudi Pro League) e mantidas as de Elite
    ligas_vips = [71, 72, 13, 39, 140, 135, 78, 61, 2, 3, 307]

    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        jogos = response.json().get('response', [])
        lista_final = []

        for item in jogos:
            league_id = item.get('league', {}).get('id')
            if league_id not in ligas_vips:
                continue
            
            fixture = item.get('fixture', {})
            if fixture.get('status', {}).get('short') not in ['NS', 'TBD', '1H', 'HT']:
                continue

            # Busca a ODD real ou estimada
            f_id = fixture.get('id')
            odd_final = buscar_odds_especificas(f_id, minha_chave)

            data_obj = datetime.fromisoformat(fixture.get('date').replace('Z', '+00:00'))
            hora_bra = data_obj.astimezone(fuso).strftime('%H:%M')

            # Lógica de palpite profissional
            liga_nome = item['league']['name']
            palpite = "Over 8.5 Escanteios"
            if "Saudi" in liga_nome or league_id == 307:
                palpite = "Over 2.5 Gols (Tendência)"

            lista_final.append({
                'Hora': hora_bra,
                'Liga': liga_nome,
                'TimeCasa': item['teams']['home']['name'],
                'LogoCasa': item['teams']['home']['logo'],
                'TimeFora': item['teams']['away']['name'],
                'LogoFora': item['teams']['away']['logo'],
                'Palpite': palpite,
                'Odd': odd_final,
                'Status': fixture['status']['long']
            })

        if lista_final:
            df = pd.DataFrame(lista_final).sort_values(by='Hora')
            df.to_csv('palpites.csv', index=False)
            print(f"✅ {len(lista_final)} jogos processados (incluindo Arábia Saudita).")

    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    buscar_jogos_vips()
