import pandas as pd
import requests
from datetime import datetime
import pytz
import random

def gerar_analise_unica(item):
    time_casa = item['teams']['home']['name']
    time_fora = item['teams']['away']['name']
    liga = item['league']['name']
    
    # Criamos uma lista de opções para o robô escolher
    # Cada uma com uma odd base diferente para não ficar tudo igual
    opcoes = [
        {"p": f"Over 0.5 Gols no 1º Tempo", "o": round(random.uniform(1.45, 1.68), 2)},
        {"p": f"Over 4.5 Cantos: {time_casa}", "o": round(random.uniform(1.75, 2.10), 2)},
        {"p": f"Vencer um dos Tempos: {time_casa}", "o": round(random.uniform(1.60, 1.95), 2)},
        {"p": f"Over 3.5 Cantos no 1º Tempo", "o": round(random.uniform(1.80, 2.20), 2)},
        {"p": f"Ambas Marcam: Sim", "o": round(random.uniform(1.70, 2.05), 2)},
        {"p": f"Handicap +1.5 {time_fora}", "o": round(random.uniform(1.50, 1.85), 2)},
        {"p": f"Over 1.5 Gols: {time_casa}", "o": round(random.uniform(1.65, 2.15), 2)}
    ]
    
    # Escolhe um palpite aleatório da lista acima
    escolha = random.choice(opcoes)
    return escolha["p"], escolha["o"]

def buscar_jogos_vips():
    fuso = pytz.timezone('America/Sao_Paulo')
    hoje = datetime.now(fuso).strftime('%Y-%m-%d')
    minha_chave = "b4533c0123994fd0a1a0d3a9d125d5ed" # <--- NÃO ESQUECE A CHAVE
    
    url = "https://v3.football.api-sports.io/fixtures"
    headers = {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': minha_chave}
    params = {'date': hoje}

    # IDs: Brasileirão A (71), B (72), Premier (39), Arábia (307), etc.
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

            # Gera o palpite e a odd única para ESTE jogo
            palpite, odd = gerar_analise_unica(item)

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
                'Odd': str(odd), # Agora é um número quebrado
                'Status': fixture['status']['long']
            })

        if lista_final:
            # Mistura a lista para os palpites não ficarem em blocos iguais
            random.shuffle(lista_final) 
            df = pd.DataFrame(lista_final).sort_values(by='Hora')
            df.to_csv('palpites.csv', index=False)
            print("✅ Site atualizado com odds e mercados variados!")

    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    buscar_jogos_vips()
