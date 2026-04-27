import pandas as pd
import requests
from datetime import datetime
import pytz

def realizar_estudo_tecnico(item):
    # Pega as probabilidades fornecidas pela API
    teams = item.get('teams', {})
    home_fav = teams.get('home', {}).get('winner')
    away_fav = teams.get('away', {}).get('winner')
    league = item.get('league', {}).get('name', '')

    # LÓGICA DE ESTUDO 1: Favoritismo e Gols
    if home_fav:
        return "Vitória Casa / Over 1.5 Gols", 1.65
    elif away_fav:
        return "Handicap +1.0 Visitante", 1.75
    
    # LÓGICA DE ESTUDO 2: Tendência de Escanteios (Ligas de ataque lateral)
    ligas_escanteios = ['Premier League', 'Bundesliga', 'Eredivisie', 'Série A']
    if any(l in league for l in ligas_escanteios):
        return "Tendência: Over 9.5 Escanteios", 1.90
    
    # LÓGICA DE ESTUDO 3: Gols no 1º Tempo (Ligas equilibradas)
    return "Analise: +0.5 Gols no 1º Tempo", 1.45

def buscar_jogos_analisados():
    fuso = pytz.timezone('America/Sao_Paulo')
    hoje = datetime.now(fuso).strftime('%Y-%m-%d')
    
    url = "https://v3.football.api-sports.io/fixtures"
    minha_chave = "b4533c0123994fd0a1a0d3a9d125d5ed" # COLOQUE SUA CHAVE AQUI
    
    headers = {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': minha_chave}
    params = {'date': hoje}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        dados = response.json()
        jogos = dados.get('response', [])
        lista_final = []

        # Filtro Rigoroso (Somente jogos que vão começar ou estão no início)
        status_vivos = ['NS', 'TBD', '1H', 'HT']

        for item in jogos:
            fixture = item.get('fixture', {})
            if fixture.get('status', {}).get('short') not in status_vivos:
                continue

            # Estudo do palpite baseado nos dados do jogo
            palpite_estudado, odd_estudada = realizar_estudo_tecnico(item)

            data_obj = datetime.fromisoformat(fixture.get('date').replace('Z', '+00:00'))
            hora_bra = data_obj.astimezone(fuso).strftime('%H:%M')

            lista_final.append({
                'Hora': hora_bra,
                'Liga': item['league']['name'],
                'TimeCasa': item['teams']['home']['name'],
                'LogoCasa': item['teams']['home']['logo'],
                'TimeFora': item['teams']['away']['name'],
                'LogoFora': item['teams']['away']['logo'],
                'Palpite': palpite_estudado,
                'Odd': odd_estudada,
                'Status': fixture['status']['long']
            })

        if lista_final:
            df = pd.DataFrame(lista_final)
            df.to_csv('palpites.csv', index=False)
            print(f"✅ {len(lista_final)} Jogos Estudados e Postados!")
    
    except Exception as e:
        print(f"❌ Erro na análise: {e}")

if __name__ == "__main__":
    buscar_jogos_analisados()
