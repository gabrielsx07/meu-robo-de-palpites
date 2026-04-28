import pandas as pd
import requests
from datetime import datetime
import pytz
import os
from thefuzz import fuzz

# CONFIGURAÇÃO DE CHAVES (Garanta que estão nos Secrets do GitHub)
API_FOOTBALL_KEY = os.getenv('API_FOOTBALL_KEY')
THE_ODDS_KEY = os.getenv('THE_ODDS_KEY')

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

def rodar():
    fuso = pytz.timezone('America/Sao_Paulo')
    hoje = datetime.now(fuso).strftime('%Y-%m-%d')
    headers_fb = {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': API_FOOTBALL_KEY}
    
    # 1. BUSCAR ODDS REAIS NO THE ODDS API (Primeira Fonte)
    odds_mercado = {}
    print("Buscando odds reais no The Odds API...")
    for slug in LIGAS_CONFIG.values():
        try:
            url = f"https://api.the-odds-api.com/v4/sports/{slug}/odds/?apiKey={THE_ODDS_KEY}&regions=eu&markets=h2h&bookmakers=bet365"
            res = requests.get(url, timeout=15).json()
            for jogo in res:
                home = jogo['home_team']
                if jogo.get('bookmakers'):
                    # Pega a odd da Bet365
                    preco = jogo['bookmakers'][0]['markets'][0]['outcomes'][0]['price']
                    odds_mercado[home] = preco
        except: continue

    # 2. BUSCAR JOGOS NA API-FOOTBALL (Segunda Fonte)
    final = []
    for liga_id in LIGAS_CONFIG.keys():
        # Testa temporadas 2026 e 2025
        for ano in [2026, 2025]:
            url_fb = f"https://v3.football.api-sports.io/fixtures?date={hoje}&league={liga_id}&season={ano}"
            try:
                res_fb = requests.get(url_fb, headers=headers_fb).json()
                jogos = res_fb.get('response', [])
                if not jogos: continue

                for j in jogos:
                    status = j['fixture']['status']['short']
                    if status not in ['NS', 'TBD', '1H', 'HT']: continue

                    time_casa = j['teams']['home']['name']
                    odd_final = None

                    # CRUZAMENTO: Tenta achar a odd exata pelo nome do time (Fuzzy Match)
                    for nome_ext, valor in odds_mercado.items():
                        if fuzz.token_sort_ratio(time_casa.lower(), nome_ext.lower()) > 80:
                            odd_final = valor
                            break
                    
                    # Se não achou na The Odds API, tenta buscar a odd na própria API-Football (Terceira Fonte/Validação)
                    if not odd_final:
                        try:
                            f_id = j['fixture']['id']
                            url_o = f"https://v3.football.api-sports.io/odds?fixture={f_id}&bookmaker=8"
                            res_o = requests.get(url_o, headers=headers_fb).json()
                            odd_final = res_o['response'][0]['bookmakers'][0]['markets'][0]['outcomes'][0]['value']
                        except: pass

                    # SÓ ADICIONA SE TIVER ODD REAL (Para garantir a precisão que você quer)
                    if odd_final:
                        val_odd = float(odd_final)
                        hora = datetime.fromisoformat(j['fixture']['date'].replace('Z', '+00:00')).astimezone(fuso).strftime('%H:%M')
                        
                        # Palpite baseado na Odd Real
                        palpite = "Casa para Vencer" if val_odd < 1.60 else "Over 0.5 Gols HT" if val_odd < 2.10 else "Ambas Marcam"

                        final.append({
                            'Hora': hora,
                            'Liga': j['league']['name'],
                            'TimeCasa': time_casa,
                            'LogoCasa': j['teams']['home']['logo'],
                            'TimeFora': j['teams']['away']['name'],
                            'LogoFora': j['teams']['away']['logo'],
                            'Palpite': palpite,
                            'Odd': str(val_odd)
                        })
                break # Sai do loop de temporada se achou jogos
            except: continue

    if final:
        pd.DataFrame(final).sort_values('Hora').to_csv('palpites.csv', index=False)
        print(f"✅ SUCESSO: {len(final)} jogos sincronizados com as duas APIs.")
    else:
        print("❌ NENHUMA ODD REAL ENCONTRADA. Verifique as chaves ou se os jogos já começaram.")

if __name__ == "__main__":
    rodar()
