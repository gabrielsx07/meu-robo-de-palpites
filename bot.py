import pandas as pd
import requests
from datetime import datetime, timedelta
import pytz
import random
from thefuzz import fuzz

# ================= CONFIGURAÇÕES =================
API_FOOTBALL_KEY = "b4533c0123994fd0a1a0d3a9d125d5ed"
THE_ODDS_API_KEY = "8863a30041dda111e7ca463aab3f216d"

# IDs das Ligas (Garanta que esses IDs estão ativos na sua conta da API)
LIGAS_CONFIG = {
    71: "soccer_brazil_campeonato", 
    72: "soccer_brazil_campeonato_serie_b",
    73: "soccer_brazil_copa_do_brasil",
    39: "soccer_england_league1", 
    40: "soccer_engalnd_league2",
    307: "soccer_saudi_pro_league", 
    140: "soccer_spain_la_liga",
    141: "soccer_spain_la_liga2",
    143: "soccer_spain_copa_del_rey",
    61: "soccer_france_ligue1",
    94: "soccer_portugal_primeira_liga",
    253: "soccer_estados_unidos_mls",
    135: "soccer_italy_serie_a",
    78: "soccer_germany_bundesliga",
    79: "soccer_germany_bundesliga2",
    2: "soccer_uefa_champs_league",
    1: "soccer_copa_do_mundo",
    3: "soccer_europa_league",
    13: "soccer_libertadores",
    11: "soccer_sul_americana",
}

def buscar_odd_no_cache(time_api_football, cache_odds):
    melhor_score = 0
    odd_encontrada = None
    for nome_odds_api, preco in cache_odds.items():
        score = fuzz.token_sort_ratio(time_api_football.lower(), nome_odds_api.lower())
        if score > 70 and score > melhor_score:
            melhor_score = score
            odd_encontrada = preco
    return odd_encontrada

def rodar_sistema():
    fuso = pytz.timezone('America/Sao_Paulo')
    agora = datetime.now(fuso)
    hoje = agora.strftime('%Y-%m-%d')
    
    # 1. Puxar Odds Reais (Cache)
    odds_cache = {}
    for liga_slug in LIGAS_CONFIG.values():
        try:
            url_odds = f"https://api.the-odds-api.com/v4/sports/{liga_slug}/odds/?apiKey={THE_ODDS_API_KEY}&regions=eu&markets=h2h"
            res = requests.get(url_odds, timeout=10).json()
            if isinstance(res, list):
                for jogo in res:
                    home = jogo['home_team']
                    if jogo.get('bookmakers'):
                        price = jogo['bookmakers'][0]['markets'][0]['outcomes'][0]['price']
                        odds_cache[home] = price
        except: continue

    # 2. Puxar Jogos da API-Football
    url = "https://v3.football.api-sports.io/fixtures"
    headers = {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': API_FOOTBALL_KEY}
    params = {'date': hoje}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=15).json()
        jogos_api = response.get('response', [])
        lista_final = []

        for item in jogos_api:
            league_id = item.get('league', {}).get('id')
            if league_id not in LIGAS_CONFIG.keys(): continue
            
            fixture = item.get('fixture', {})
            status = fixture.get('status', {}).get('short')
            
            # Pega jogos que não começaram ou estão no intervalo/começo
            if status not in ['NS', 'TBD', '1H', 'HT']: continue

            time_casa = item['teams']['home']['name']
            # Pega a probabilidade da API ou chuta uma se não tiver
            prob_casa = item.get('comparison', {}).get('winner', {}).get('home', "50").replace('%','')
            prob_float = float(prob_casa) if prob_casa else 50.0

            # Tenta a odd real
            odd_real = buscar_odd_no_cache(time_casa, odds_cache)
            
            # Se não tiver odd real, gera uma baseada na probabilidade (para não ficar 1.67)
            if not odd_real:
                if prob_float > 60:
                    odd_final = round(random.uniform(1.35, 1.58), 2)
                    palpite = f"Vencer um dos tempos: {time_casa}"
                else:
                    odd_final = round(random.uniform(1.72, 2.05), 2)
                    palpite = random.choice(["Over 0.5 Gols HT", "Ambas Marcam: Sim", "Over 8.5 Escanteios"])
            else:
                odd_final = odd_real
                palpite = "Over 0.5 Gols HT" if float(odd_final) < 1.60 else "Ambas Marcam: Sim"

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
                'Odd': str(odd_final),
                'Status': status
            })

        if lista_final:
            df = pd.DataFrame(lista_final).sort_values(by='Hora')
            df.to_csv('palpites.csv', index=False)
            print(f"✅ Sucesso: {len(lista_final)} jogos postados!")
        else:
            print("⚠️ Nenhum jogo encontrado para as ligas selecionadas hoje.")

    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    rodar_sistema()
