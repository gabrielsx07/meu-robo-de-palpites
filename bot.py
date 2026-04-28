import pandas as pd
import requests
from datetime import datetime
import pytz
import os
from thefuzz import fuzz

# ================= CONFIGURAÇÕES =================
# O código agora busca as chaves que você colocou nos Secrets do GitHub
API_FOOTBALL_KEY = os.getenv('API_FOOTBALL_KEY')
THE_ODDS_KEY = os.getenv('THE_ODDS_KEY')

# Suas ligas favoritas
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
    # ... adicione outras aqui se quiser
}

def rodar():
    fuso = pytz.timezone('America/Sao_Paulo')
    hoje = datetime.now(fuso).strftime('%Y-%m-%d')
    headers_fb = {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': API_FOOTBALL_KEY}
    
    # 1. BUSCA ODDS REAIS NA BET365 (via The Odds API)
    odds_cache = {}
    print("Buscando odds reais...")
    for slug in LIGAS_CONFIG.values():
        try:
            url = f"https://api.the-odds-api.com/v4/sports/{slug}/odds/?apiKey={THE_ODDS_KEY}&regions=eu&markets=h2h&bookmakers=bet365"
            res = requests.get(url, timeout=15).json()
            for jogo in res:
                home_name = jogo['home_team']
                if jogo.get('bookmakers'):
                    # Pega a odd da vitória do time da casa na Bet365
                    odds_cache[home_name] = jogo['bookmakers'][0]['markets'][0]['outcomes'][0]['price']
        except: continue

    # 2. BUSCA DADOS DO JOGO NA API-FOOTBALL
    lista_final = []
    for liga_id in LIGAS_CONFIG.keys():
        # Tenta temporada 2026 e 2025 (para cobrir Champions e Brasileirão)
        for ano in [2026, 2025]:
            url_fb = f"https://v3.football.api-sports.io/fixtures?date={hoje}&league={liga_id}&season={ano}"
            try:
                res_fb = requests.get(url_fb, headers=headers_fb).json()
                jogos = res_fb.get('response', [])
                if not jogos: continue

                for item in jogos:
                    status = item['fixture']['status']['short']
                    # Pega apenas jogos que não começaram ou estão no começo
                    if status not in ['NS', 'TBD', '1H', 'HT']: continue

                    time_casa = item['teams']['home']['name']
                    odd_real = None

                    # Sincroniza a odd real da Bet365 com o jogo da API-Football
                    for nome_ext, valor_odd in odds_cache.items():
                        # Usamos 'fuzzy matching' para ignorar diferenças de nome (ex: "PSG" vs "Paris Saint Germain")
                        if fuzz.token_sort_ratio(time_casa.lower(), nome_ext.lower()) > 80:
                            odd_real = valor_odd
                            break
                    
                    # SÓ ADICIONA SE A ODD FOR ENCONTRADA (Para garantir a precisão)
                    if odd_real:
                        # Palpites inteligentes baseados na odd real
                        val = float(odd_real)
                        if val < 1.60:
                            palpite = f"Vencer um dos tempos: {time_casa}"
                        elif val < 2.00:
                            palpite = "Over 0.5 Gols HT"
                        else:
                            palpite = "Ambas Marcam: Sim"

                        hora = datetime.fromisoformat(item['fixture']['date'].replace('Z', '+00:00')).astimezone(fuso).strftime('%H:%M')

                        lista_final.append({
                            'Hora': hora,
                            'Liga': item['league']['name'],
                            'TimeCasa': time_casa,
                            'LogoCasa': item['teams']['home']['logo'],
                            'TimeFora': item['teams']['away']['name'],
                            'LogoFora': item['teams']['away']['logo'],
                            'Palpite': palpite,
                            'Odd': str(odd_real)
                        })
                break
            except: continue

    # 3. SALVA O CSV PARA O SITE
    if lista_final:
        pd.DataFrame(lista_final).sort_values('Hora').to_csv('palpites.csv', index=False)
        print(f"✅ SUCESSO: {len(lista_final)} jogos com odds reais gerados.")
    else:
        print("⚠️ AVISO: Nenhum jogo com odd real foi encontrado hoje.")

if __name__ == "__main__":
    rodar()
