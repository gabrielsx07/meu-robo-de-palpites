import pandas as pd
import requests
from datetime import datetime
import pytz

def buscar_jogos_profissionais():
    # 1. Configurações de Data e Fuso de Brasília
    fuso = pytz.timezone('America/Sao_Paulo')
    hoje = datetime.now(fuso).strftime('%Y-%m-%d')
    print(f"⚽ Buscando jogos de hoje ({hoje}) com a API oficial...")

    # 2. Configurações da API com a sua chave
    url = "https://v3.football.api-sports.io/fixtures"
    headers = {
        'x-rapidapi-host': "v3.football.api-sports.io",
        'x-rapidapi-key': "b4533c0123994fd0a1a0d3a9d125d5ed" # Sua chave da foto
    }
    
    # Buscamos todos os jogos da data de hoje
    params = {'date': hoje}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=20)
        
        if response.status_code == 200:
            dados = response.json()
            jogos = dados.get('response', [])
            
            if not jogos:
                print("⚠️ A API não retornou jogos para hoje. Verifique se há rodadas hoje.")
                return

            lista_final = []
            for item in jogos:
                fixture = item.get('fixture', {})
                league = item.get('league', {})
                teams = item.get('teams', {})
                goals = item.get('goals', {})
                status = fixture.get('status', {})

                lista_final.append({
                    'Horario_BR': fixture.get('date'),
                    'Liga': f"{league.get('country')} - {league.get('name')}",
                    'Casa': teams.get('home', {}).get('name'),
                    'Fora': teams.get('away', {}).get('name'),
                    'Placar': f"{goals.get('home')} x {goals.get('away')}",
                    'Status': status.get('long'), # Ex: 'Match Finished', 'In Play', 'Not Started'
                    'Minutos': status.get('elapsed') # Tempo de jogo se estiver rolando
                })

            # 3. Gera o arquivo CSV
            df = pd.DataFrame(lista_final)
            df.to_csv('palpites.csv', index=False)
            print(f"✅ Sucesso! {len(lista_final)} jogos salvos no arquivo 'palpites.csv'.")
        else:
            print(f"❌ Erro na API: Status {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"❌ Falha no robô: {e}")

if __name__ == "__main__":
    buscar_jogos_profissionais()
