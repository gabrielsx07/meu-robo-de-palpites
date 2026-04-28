import pandas as pd
import requests
from datetime import datetime
import pytz
from thefuzz import fuzz

# ================= CONFIGURAÇÕES =================
API_FOOTBALL_KEY = "b4533c0123994fd0a1a0d3a9d125d5ed"
THE_ODDS_API_KEY = "8863a30041dda111e7ca463aab3f216d"

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

def buscar_odd_real_estrita(time_api, cache_odds):
    """Retorna a odd apenas se houver alto grau de certeza no nome"""
    melhor_score = 0
    odd_selecionada = None
    
    for nome_ext, valor_odd in cache_odds.items():
        # Comparação de strings para evitar erros entre "Real Madrid" e "Real Madrid CF"
        score = fuzz.token_sort_ratio(time_api.lower(), nome_ext.lower())
        if score > 85: # Score alto = certeza de que é o mesmo time
            return valor_odd
    return None

def rodar_sistema():
    fuso = pytz.timezone('America/Sao_Paulo')
    hoje = datetime.now(fuso).strftime('%Y-%m-%d')
    
    # 1. PEGAR ODDS REAIS (THE ODDS API)
    odds_reais_hoje = {}
    for slug in LIGAS_CONFIG.values():
        try:
            # Puxando odds da Bet365/Pinnacle na região europeia/brasil
            url = f"https://api.the-odds-api.com/v4/sports/{slug}/odds/?apiKey={THE_ODDS_API_KEY}&regions=eu&markets=h2h&bookmakers=bet365,pinnacle"
            res = requests.get(url, timeout=10).json()
            
            for jogo in res:
                home_name = jogo['home_team']
                # Pega a odd do primeiro bookmaker disponível na lista
                if jogo.get('bookmakers'):
                    outcomes = jogo['bookmakers'][0]['markets'][0]['outcomes']
                    for out in outcomes:
                        if out['name'] == home_name:
                            odds_reais_hoje[home_name] = out['price']
        except: continue

    # 2. PEGAR JOGOS (API-FOOTBALL)
    url_football = "https://v3.football.api-sports.io/fixtures"
    headers = {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': API_FOOTBALL_KEY}
    params = {'date': hoje}

    try:
        response = requests.get(url_football, headers=headers, params=params).json()
        jogos = response.get('response', [])
        lista_final = []

        for item in jogos:
            l_id = item['league']['id']
            if l_id not in LIGAS_CONFIG: continue
            
            status = item['fixture']['status']['short']
            if status not in ['NS', 'TBD']: continue

            time_casa = item['teams']['home']['name']
            
            # Tenta encontrar a odd real no cache
            odd_verificada = buscar_odd_real_estrita(time_casa, odds_reais_hoje)

            # SÓ ADICIONA SE A ODD FOR ENCONTRADA (GARANTE PRECISÃO)
            if odd_verificada:
                # Lógica de Palpite baseada na ODD REAL (Matemática pura)
                if odd_verificada < 1.45:
                    palpite = f"Vencer um dos tempos: {time_casa}"
                elif odd_verificada < 2.00:
                    palpite = "Over 0.5 Gols HT"
                else:
                    palpite = "Ambas Marcam: Sim"

                hora = datetime.fromisoformat(item['fixture']['date'].replace('Z', '+00:00')).astimezone(fuso).strftime('%H:%M')

                lista_final.append({
                    'Hora': hora, 'Liga': item['league']['name'],
                    'TimeCasa': time_casa, 'LogoCasa': item['teams']['home']['logo'],
                    'TimeFora': item['teams']['away']['name'], 'LogoFora': item['teams']['away']['logo'],
                    'Palpite': palpite, 'Odd': str(odd_verificada)
                })

        if lista_final:
            pd.DataFrame(lista_final).sort_values('Hora').to_csv('palpites.csv', index=False)
            print(f"✅ {len(lista_final)} jogos com odds REAIS Bet365/Pinnacle.")
        else:
            print("❌ Nenhuma odd real pôde ser sincronizada no momento.")

    except Exception as e: print(f"❌ Erro: {e}")

if __name__ == "__main__":
    rodar_sistema()
