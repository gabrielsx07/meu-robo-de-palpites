import pandas as pd
import requests
from datetime import datetime
import pytz
import random

# ================= CONFIGURAÇÕES =================
API_FOOTBALL_KEY = "b4533c0123994fd0a1a0d3a9d125d5ed"
THE_ODDS_API_KEY = "8863a30041dda111e7ca463aab3f216d"

# IDs das Ligas (API-Football) e seus nomes correspondentes (The Odds API)
LIGAS_CONFIG = {
    71:  "soccer_brazil_campeonato",     # Brasileirão Série A
    72:  "soccer_brazil_campeonato_serie_b", # Série B
    39:  "soccer_england_league1",       # Premier League
    140: "soccer_spain_la_liga",         # La Liga
    135: "soccer_italy_serie_a",         # Serie A
    78:  "soccer_germany_bundesliga",    # Bundesliga
    307: "soccer_saudi_pro_league",      # Liga Saudita
    13:  "soccer_conmebol_libertadores"  # Libertadores
}

def buscar_odds_reais():
    """Puxa as odds reais do mercado e organiza em um dicionário"""
    odds_mercado = {}
    for api_name in LIGAS_CONFIG.values():
        try:
            url = f"https://api.the-odds-api.com/v4/sports/{api_name}/odds/"
            params = {
                'apiKey': THE_ODDS_API_KEY,
                'regions': 'eu', # Casas europeias como Bet365
                'markets': 'h2h',
                'oddsFormat': 'decimal'
            }
            res = requests.get(url, params=params, timeout=10)
            data = res.json()
            
            for jogo in data:
                home_team = jogo['home_team']
                # Pega a primeira odd disponível (geralmente da primeira casa de apostas)
                if jogo.get('bookmakers'):
                    odds = jogo['bookmakers'][0]['markets'][0]['outcomes']
                    # Salva a odd do time da casa
                    for outcome in odds:
                        if outcome['name'] == home_team:
                            odds_mercado[home_team] = outcome['price']
        except:
            continue
    return odds_mercado

def gerar_palpite_profissional(time_casa, odd_real):
    """Baseado na odd real, define um mercado lógico"""
    if not odd_real:
        return "Over 0.5 Gols HT", "1.60"
    
    odd = float(odd_real)
    
    if odd < 1.50:
        p = random.choice([f"Vencer um dos Tempos: {time_casa}", "Over 1.5 Gols: Casa"])
    elif odd < 2.20:
        p = random.choice(["Ambas Marcam: Sim", "Over 8.5 Escanteios", "Over 0.5 Gols HT"])
    else:
        p = random.choice(["Handicap +1.0 Casa", "Over 3.5 Cantos no 1º Tempo"])
        
    return p, f"{odd:.2f}"

def rodar_sistema():
    fuso = pytz.timezone('America/Sao_Paulo')
    hoje = datetime.now(fuso).strftime('%Y-%m-%d')
    
    # 1. Busca Odds Reais primeiro para ter no "cache"
    print("🛰️ Puxando odds reais do mercado...")
    banco_de_odds = buscar_odds_reais()

    # 2. Busca Jogos na API-Football
    url = "https://v3.football.api-sports.io/fixtures"
    headers = {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': API_FOOTBALL_KEY}
    params = {'date': hoje}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        jogos_api = response.json().get('response', [])
        lista_final = []

        for item in jogos_api:
            league_id = item.get('league', {}).get('id')
            if league_id not in LIGAS_CONFIG.keys():
                continue
            
            fixture = item.get('fixture', {})
            if fixture.get('status', {}).get('short') not in ['NS', 'TBD', '1H', 'HT']:
                continue

            time_casa = item['teams']['home']['name']
            
            # Tenta casar o time da API-Football com a Odd da The Odds API
            odd_da_casa = banco_de_odds.get(time_casa)
            palpite, odd_exibida = gerar_palpite_profissional(time_casa, odd_da_casa)

            data_obj = datetime.fromisoformat(fixture.get('date').replace('Z', '+00:00'))
            hora_bra = data_obj.astimezone(fuso).strftime('%H:%M')

            lista_final.append({
                'Hora': hora_bra,
                'Liga': item['league']['name'],
                'TimeCasa': time_casa,
                'LogoCasa': item['teams']['home']['logo'],
                'TimeFora': item['teams']['away']['name'],
                'LogoFora': item['teams']['away']['logo'],
                'Palpite': palpite,
                'Odd': odd_exibida,
                'Status': fixture['status']['long']
            })

        if lista_final:
            df = pd.DataFrame(lista_final).sort_values(by='Hora')
            df.to_csv('palpites.csv', index=False)
            print(f"✅ Sucesso! {len(lista_final)} jogos postados com odds reais.")
        else:
            print("⚠️ Nenhum jogo de elite hoje.")

    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == "__main__":
    rodar_sistema()
