import pandas as pd
import requests
from datetime import datetime
import pytz
import os

API_KEY = os.getenv('API_FOOTBALL_KEY')

def rodar():
    fuso = pytz.timezone('America/Sao_Paulo')
    agora = datetime.now(fuso)
    hoje = agora.strftime('%Y-%m-%d')
    
    headers = {
        'x-rapidapi-host': "v3.football.api-sports.io",
        'x-rapidapi-key': API_KEY
    }
    
    final = []
    print(f"Buscando jogos ativos no mundo todo para hoje ({hoje})...")

    # Puxa TODOS os jogos do dia de uma vez só (consome apenas 1 requisição)
    url = f"https://v3.football.api-sports.io/fixtures?date={hoje}"
    
    try:
        r = requests.get(url, headers=headers, timeout=25).json()
        
        # Verifica se a API retornou erro de limite
        if r.get('errors'):
            print(f"⚠️ Erro da API: {r['errors']}")
            return

        jogos = r.get('response', [])
        print(f"Total de jogos encontrados no mundo hoje: {len(jogos)}")

        for j in jogos:
            status = j['fixture']['status']['short']
            # NS = Não começou, 1H/2H = Em andamento, HT = Intervalo
            if status not in ['NS', 'TBD', '1H', 'HT', '2H']: 
                continue
            
            # Converte a hora do jogo para o nosso fuso
            dt_jogo = datetime.fromisoformat(j['fixture']['date'].replace('Z', '+00:00')).astimezone(fuso)
            
            # Se o jogo já acabou (FT) ou foi cancelado, pula
            if status == 'FT' or status == 'CANCL': 
                continue

            # Lógica de Palpite Detalhado (Baseado no tipo de campeonato)
            nome_liga = j['league']['name'].lower()
            
            if "cup" in nome_liga or "copa" in nome_liga:
                palpite = "Mais de 0.5 Gols HT"
            elif "u20" in nome_liga or "u21" in nome_liga:
                palpite = "Escanteios: Over 9.5"
            elif "women" in nome_liga:
                palpite = "Vencer um dos Tempos"
            else:
                palpite = "Over 1.5 Gols / Cantos"

            final.append({
                'Hora': dt_jogo.strftime('%H:%M'),
                'Liga': j['league']['name'],
                'TimeCasa': j['teams']['home']['name'],
                'LogoCasa': j['teams']['home']['logo'],
                'TimeFora': j['teams']['away']['name'],
                'LogoFora': j['teams']['away']['logo'],
                'Palpite': palpite
            })

    except Exception as e:
        print(f"Erro na execução: {e}")

    if final:
        # Ordena por horário e pega os 30 jogos mais próximos/atuais
        df = pd.DataFrame(final).sort_values('Hora')
        df.head(30).to_csv('palpites.csv', index=False)
        print(f"✅ SUCESSO: {len(df.head(30))} palpites postados no site!")
    else:
        print("⚠️ Nenhum jogo pendente encontrado para hoje no mundo.")

if __name__ == "__main__":
    rodar()
