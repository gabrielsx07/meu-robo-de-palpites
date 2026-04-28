import pandas as pd
import requests
from datetime import datetime
import pytz
import random
from thefuzz import fuzz # Biblioteca para comparar nomes parecidos

# ================= CONFIGURAÇÕES =================
API_FOOTBALL_KEY = "b4533c0123994fd0a1a0d3a9d125d5ed"
THE_ODDS_API_KEY = "8863a30041dda111e7ca463aab3f216d"

# IDs das Ligas (API-Football)
LIGAS_CONFIG = {
    71: "soccer_brazil_campeonato", 39: "soccer_england_league1", 
    307: "soccer_saudi_pro_league", 140: "soccer_spain_la_liga",
    135: "soccer_italy_serie_a", 78: "soccer_germany_bundesliga"
}

def buscar_odd_no_cache(time_api_football, cache_odds):
    """Procura a odd usando comparação por semelhança de nome"""
    melhor_score = 0
    odd_encontrada = None
    
    for nome_odds_api, preco in cache_odds.items():
        # Calcula a semelhança entre os nomes (0 a 100)
        score = fuzz.token_sort_ratio(time_api_football.lower(), nome_odds_api.lower())
        if score > 75 and score > melhor_score:
            melhor_score = score
            odd_encontrada = preco
            
    return odd_encontrada

def gerar_palpite_variado(time_casa, prob_casa):
    """Sorteia mercados diferentes para não ficar tudo igual"""
    p = float(prob_casa) if prob_casa else 50
    
    mercados = [
        f"Over 0.5 Gols no 1º Tempo",
        f"Vencer um dos tempos: {time_casa}",
        f"Over 4.5 Cantos: {time_casa}",
        f"Ambas Marcam: Sim",
        f"Over 8.5 Escanteios no Jogo",
        f"Over 3.5 Cantos no 1º Tempo"
    ]
    # Escolhe um mercado aleatório da lista
    return random.choice(mercados)

def rodar_sistema():
    fuso = pytz.timezone('America/Sao_Paulo')
    hoje = datetime.now(fuso).strftime('%Y-%m-%d')
    
    # 1. Puxar Odds Reais e guardar no cache
    odds_cache = {}
    for liga_slug in LIGAS_CONFIG.values():
        try:
            url_odds = f"https://api.the-odds-api.com/v4/sports/{liga_slug}/odds/?apiKey={THE_ODDS_API_KEY}&regions=eu&markets=h2h"
            res = requests.get(url_odds, timeout=10).json()
            for jogo in res:
                home = jogo['home_team']
                if jogo.get('bookmakers'):
                    # Pega a odd do time da casa na primeira casa disponível
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
            if item.get('league', {}).get('id') not in LIGAS_CONFIG.keys(): continue
            fixture = item.get('fixture', {})
            if fixture.get('status', {}).get('short') not in ['NS', 'TBD', '1H', 'HT']: continue

            time_casa = item['teams']['home']['name']
            prob_casa = item.get('comparison', {}).get('winner', {}).get('home', "50").replace('%','')
            
            # Tenta buscar a odd com o comparador inteligente
            odd_real = buscar_odd_no_cache(time_casa, odds_cache)
            
            # Se não achou a odd real, calcula uma baseada na probabilidade
            if not odd_real:
                odd_final = round(100 / (float(prob_casa) + 10), 2) if float(prob_casa) > 20 else 1.95
            else:
                odd_final = odd_real

            palpite = gerar_palpite_variado(time_casa, prob_casa)
            
            data_obj = datetime.fromisoformat(fixture.get('date').replace('Z', '+00:00'))
            hora_bra = data_obj.astimezone(fuso).strftime('%H:%M')

            lista_final.append({
                'Hora': hora_bra, 'Liga': item['league']['name'],
                'TimeCasa': time_casa, 'LogoCasa': item['teams']['home']['logo'],
                'TimeFora': item['teams']['away']['name'], 'LogoFora': item['teams']['away']['logo'],
                'Palpite': palpite, 'Odd': str(odd_final), 'Status': fixture['status']['long']
            })

        if lista_final:
            df = pd.DataFrame(lista_final).sort_values(by='Hora')
            df.to_csv('palpites.csv', index=False)
            print("✅ Sistema rodado com comparador inteligente de nomes!")

    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    rodar_sistema()
