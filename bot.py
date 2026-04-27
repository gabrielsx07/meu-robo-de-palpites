import pandas as pd
import requests
from datetime import datetime
import pytz
import random

def gerar_palpite_inteligente(item):
    home = item['teams']['home']['name']
    away = item['teams']['away']['name']
    
    # Lista de opções para o robô variar
    opcoes_gols = [f"Over 1.5 Gols", f"Ambas Marcam: Sim", f"+0.5 Gols no 1º Tempo"]
    opcoes_cantos = [f"Over 8.5 Escanteios", f"Escanteios: {home} mais de 4.5", "Over 9.5 Cantos"]
    
    # Lógica baseada no favorito da API
    if item['teams']['home'].get('winner'):
        return f"Vitória {home} / +1.5 Gols", "1.75"
    elif item['teams']['away'].get('winner'):
        return f"Handicap +1 {away}", "1.88"
    
    # Se não houver favorito claro, sorteia entre gols e cantos para variar o site
    escolha = random.choice(["gols", "cantos"])
    if escolha == "gols":
        return random.choice(opcoes_gols), str(round(random.uniform(1.60, 2.10), 2))
    else:
        return random.choice(opcoes_cantos), str(round(random.uniform(1.70, 2.25), 2))

def buscar():
    fuso = pytz.timezone('America/Sao_Paulo')
    hoje = datetime.now(fuso).strftime('%Y-%m-%d')
    
    url = "https://v3.football.api-sports.io/fixtures"
    minha_chave = "b4533c0123994fd0a1a0d3a9d125d5ed" # <--- COLOQUE SUA CHAVE AQUI
    
    headers = {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': minha_chave}
    params = {'date': hoje}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        jogos = response.json().get('response', [])
        
        lista_final = []
        for item in jogos:
            fixture = item.get('fixture', {})
            # Filtro rigoroso: apenas jogos que não começaram ou estão rolando
            if fixture.get('status', {}).get('short') in ['FT', 'AET', 'PEN', 'PST', 'CANC']:
                continue

            hora_bra = datetime.fromisoformat(fixture['date'].replace('Z', '+00:00')).astimezone(fuso).strftime('%H:%M')

            # CHAMA A LOGICA DE VARIACAO
            palpite_texto, odd_valor = gerar_palpite_inteligente(item)

            lista_final.append({
                'Hora': hora_bra,
                'Liga': item['league']['name'],
                'TimeCasa': item['teams']['home']['name'],
                'LogoCasa': item['teams']['home']['logo'],
                'TimeFora': item['teams']['away']['name'],
                'LogoFora': item['teams']['away']['logo'],
                'Palpite': palpite_texto,
                'Odd': odd_valor,
                'Status': fixture['status']['long']
            })

        if lista_final:
            df = pd.DataFrame(lista_final)
            df.to_csv('palpites.csv', index=False)
            print(f"✅ {len(lista_final)} jogos processados com palpites variados!")
        else:
            print("⚠️ Nenhum jogo pendente para hoje.")

    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    buscar()
