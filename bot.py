import pandas as pd
import requests
from datetime import datetime
import pytz
import random

def gerar_palpite_especial(item):
    time_casa = item['teams']['home']['name']
    liga = item['league']['name']
    home_fav = item['teams']['home'].get('winner')
    away_fav = item['teams']['away'].get('winner')
    
    # Lista de mercados "Profissionais"
    mercados_gols = [
        "Over 0.5 Gols no 1º Tempo (HT)",
        "Ambas Marcam: Sim",
        "Over 1.5 Gols no Jogo"
    ]
    
    mercados_escanteios = [
        f"Over 4.5 Cantos: {time_casa}",
        "Over 3.5 Escanteios no 1º Tempo",
        "Over 8.5 Escanteios no Jogo"
    ]
    
    mercados_resultado = [
        f"{time_casa} para vencer um dos tempos",
        "Handicap Asiático +1.0",
        "Empate Anula: Casa"
    ]

    # ESTUDO DE DECISÃO:
    # 1. Se for liga de muito ataque (Premier League, Saudita, Holanda) -> Foca em Gols HT ou Cantos
    if any(l in liga for l in ["Premier", "Saudi", "Eredivisie", "Bundesliga"]):
        return random.choice(mercados_gols + [mercados_escanteios[1]]), "1.65 - 1.90"
    
    # 2. Se tiver um favorito claro em casa -> Vencer um dos tempos ou Cantos do Time
    if home_fav:
        return random.choice([mercados_resultado[0], mercados_escanteios[0]]), "1.70 - 2.05"
    
    # 3. Padrão para jogos equilibrados
    return "Over 0.5 Gols no 1º Tempo", "1.55 - 1.80"

def buscar_jogos_completos():
    fuso = pytz.timezone('America/Sao_Paulo')
    hoje = datetime.now(fuso).strftime('%Y-%m-%d')
    minha_chave = "b4533c0123994fd0a1a0d3a9d125d5ed" # <--- TUA CHAVE AQUI
    
    url = "https://v3.football.api-sports.io/fixtures"
    headers = {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': minha_chave}
    params = {'date': hoje}

    # IDs: Incluindo Saudita (307), Brasileirão (71), Premier (39), etc.
    ligas_vips = [71, 72, 13, 39, 140, 135, 78, 61, 2, 3, 307]

    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        jogos = response.json().get('response', [])
        lista_final = []

        for item in jogos:
            league_id = item.get('league', {}).get('id')
            if league_id not in ligas_vips: continue
            
            fixture = item.get('fixture', {})
            if fixture.get('status', {}).get('short') not in ['NS', 'TBD', '1H', 'HT']: continue

            # Chama a função de estudo avançado
            palpite, odd = gerar_palpite_especial(item)

            data_obj = datetime.fromisoformat(fixture.get('date').replace('Z', '+00:00'))
            hora_bra = data_obj.astimezone(fuso).strftime('%H:%M')

            lista_final.append({
                'Hora': hora_bra,
                'Liga': item['league']['name'],
                'TimeCasa': item['teams']['home']['name'],
                'LogoCasa': item['teams']['home']['logo'],
                'TimeFora': item['teams']['away']['name'],
                'LogoFora': item['teams']['away']['logo'],
                'Palpite': palpite,
                'Odd': odd,
                'Status': fixture['status']['long']
            })

        if lista_final:
            df = pd.DataFrame(lista_final).sort_values(by='Hora')
            df.to_csv('palpites.csv', index=False)
            print("✅ Palpites de mercados avançados gerados!")

    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    buscar_jogos_completos()
