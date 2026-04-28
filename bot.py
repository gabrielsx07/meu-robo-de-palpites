import pandas as pd
import requests
from datetime import datetime
import pytz

# ================= CONFIGURAÇÕES =================
API_KEY = "SUA_CHAVE_API_FOOTBALL_AQUI"
LIGAS_IDS = [71, 72, 39, 307, 140, 141, 135, 78, 61, 62, 73, 40, 143, 94, 253, 79, 2, 1, 13, 11, 3]

def buscar_banco_de_odds(liga_id):
    """Puxa todas as odds da liga de uma vez para economizar e ser preciso"""
    url = "https://v3.football.api-sports.io/odds"
    headers = {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': API_KEY}
    params = {'league': liga_id, 'season': 2026} # Garante a temporada atual
    
    odds_dict = {}
    try:
        res = requests.get(url, headers=headers, params=params, timeout=15).json()
        for item in res.get('response', []):
            f_id = item['fixture']['id']
            # Tenta pegar a odd do mercado 'Match Winner' (id: 1)
            for bookmaker in item.get('bookmakers', []):
                for market in bookmaker.get('markets', []):
                    if market['id'] == 1:
                        # Pega a odd do time da casa (Vitoria 1)
                        odd_val = market['outcomes'][0]['value']
                        odds_dict[f_id] = odd_val
                        break
                if f_id in odds_dict: break # Se achou em uma casa, pula para o próximo jogo
    except:
        pass
    return odds_dict

def rodar_sistema():
    fuso = pytz.timezone('America/Sao_Paulo')
    hoje = datetime.now(fuso).strftime('%Y-%m-%d')
    url_fixtures = "https://v3.football.api-sports.io/fixtures"
    headers = {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': API_KEY}
    
    lista_final = []

    for liga in LIGAS_IDS:
        # 1. Puxa as odds da liga toda primeiro
        print(f"Buscando odds para a liga {liga}...")
        banco_odds = buscar_banco_de_odds(liga)
        
        # 2. Puxa os detalhes dos jogos
        params = {'date': hoje, 'league': liga}
        try:
            response = requests.get(url_fixtures, headers=headers, params=params).json()
            jogos = response.get('response', [])
            
            for item in jogos:
                f_id = item['fixture']['id']
                status = item['fixture']['status']['short']
                
                if status not in ['NS', 'TBD', '1H', 'HT']: continue

                # Pega a odd real do nosso banco
                odd_real = banco_odds.get(f_id)
                
                # SE NÃO TIVER ODD REAL, vamos usar a probabilidade da API para calcular
                # uma odd honesta (em vez de 1.67 fixo)
                if not odd_real:
                    prob_casa = item.get('comparison', {}).get('winner', {}).get('home', '50').replace('%','')
                    odd_real = round(100 / (float(prob_casa) + 5), 2) if float(prob_casa) > 10 else 2.10

                val_odd = float(odd_real)
                time_casa = item['teams']['home']['name']

                # Palpites baseados na odd real
                if val_odd < 1.55:
                    palpite = f"Vencer: {time_casa}"
                elif val_odd < 1.95:
                    palpite = "Over 0.5 Gols HT"
                elif val_odd < 2.40:
                    palpite = "Ambas Marcam: Sim"
                else:
                    palpite = "Handicap +1.0 Casa"

                hora = datetime.fromisoformat(item['fixture']['date'].replace('Z', '+00:00')).astimezone(fuso).strftime('%H:%M')

                lista_final.append({
                    'Hora': hora,
                    'Liga': item['league']['name'],
                    'TimeCasa': time_casa,
                    'LogoCasa': item['teams']['home']['logo'],
                    'TimeFora': item['teams']['away']['name'],
                    'LogoFora': item['teams']['away']['logo'],
                    'Palpite': palpite,
                    'Odd': str(val_odd)
                })
        except: continue

    if lista_final:
        df = pd.DataFrame(lista_final).sort_values('Hora')
        df.to_csv('palpites.csv', index=False)
        print(f"✅ Feito! {len(lista_final)} jogos com odds sincronizadas.")

if __name__ == "__main__":
    rodar_sistema()
