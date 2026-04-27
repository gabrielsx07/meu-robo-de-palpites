import pandas as pd
import requests
from datetime import datetime
import pytz

def buscar_jogos_focados():
    fuso = pytz.timezone('America/Sao_Paulo')
    hoje = datetime.now(fuso).strftime('%Y-%m-%d')
    print(f"⚽ Buscando jogos focados para: {hoje}")

    url = "https://v3.football.api-sports.io/fixtures"
    minha_chave = "SUA_CHAVE_AQUI" # <--- COLE SUA CHAVE AQUI
    
    headers = {
        'x-rapidapi-host': "v3.football.api-sports.io",
        'x-rapidapi-key': minha_chave
    }

    # IDs das Ligas que você pediu:
    # 71: Brasileirão A, 72: Série B, 13: Champions, 11: Sudamericana, 
    # 1: World Cup, 307: Arábia, 253: MLS, 2: UCL, 3: Europa League...
    ligas_foco = [71, 72, 13, 11, 10, 307, 253, 39, 140, 61, 78, 135] 
    
    jogos_final = []

    # A API permite buscar por data. Vamos filtrar os resultados no código
    params = {'date': hoje}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=20)
        if response.status_code == 200:
            dados = response.json()
            todos_jogos = dados.get('response', [])

            for item in todos_jogos:
                league_id = item.get('league', {}).get('id')
                
                # Só adiciona se estiver nas ligas que você quer
                if league_id in ligas_foco:
                    fixture = item.get('fixture', {})
                    teams = item.get('teams', {})
                    goals = item.get('goals', {})
                    
                    # Converte a hora UTC para Brasília
                    hora_utc = datetime.fromisoformat(fixture.get('date').replace('Z', '+00:00'))
                    hora_br = hora_utc.astimezone(fuso).strftime('%H:%M')

                    jogos_final.append({
                        'Horário': hora_br,
                        'Liga': item.get('league', {}).get('name'),
                        'País': item.get('league', {}).get('country'),
                        'Mandante': teams.get('home', {}).get('name'),
                        'Visitante': teams.get('away', {}).get('name'),
                        'Placar': f"{goals.get('home') if goals.get('home') is not None else ''} x {goals.get('away') if goals.get('away') is not None else ''}",
                        'Status': fixture.get('status', {}).get('short')
                    })

            if not jogos_final:
                print("⚠ Nenhuma partida das ligas escolhidas para hoje.")
                return

            df = pd.DataFrame(jogos_final)
            # Ordena por horário para facilitar a leitura
            df = df.sort_values(by='Horário')
            df.to_csv('palpites.csv', index=False)
            print(f"✅ {len(jogos_final)} jogos importantes salvos com sucesso!")
        else:
            print(f"❌ Erro API: {response.status_code}")

    except Exception as e:
        print(f"❌ Erro no robô: {e}")

if __name__ == "__main__":
    buscar_jogos_focados()
