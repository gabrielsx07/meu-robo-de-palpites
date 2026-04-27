import pandas as pd
import requests
from datetime import datetime
import pytz

def buscar_jogos_profissionais():
    # 1. Configura fuso de Brasília e data de hoje
    fuso = pytz.timezone('America/Sao_Paulo')
    agora = datetime.now(fuso)
    hoje = agora.strftime('%Y-%m-%d')
    
    print(f"⚽ Iniciando busca: {agora.strftime('%d/%m/%Y %H:%M:%S')}")

    # 2. Configurações da API (Plano Grátis: 100 requisições por dia)
    url = "https://v3.football.api-sports.io/fixtures"
    minha_chave = "b4533c0123994fd0a1a0d3a9d125d5ed" # <--- Cole sua chave aqui
    
    headers = {
        'x-rapidapi-host': "v3.football.api-sports.io",
        'x-rapidapi-key': minha_chave
    }
    
    # Parâmetros para pegar jogos de HOJE
    params = {'date': hoje}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=20)
        
        if response.status_code == 200:
            dados = response.json()
            jogos = dados.get('response', [])
            
            if not jogos:
                print(f"⚠ Nenhum jogo encontrado para {hoje}.")
                return

            lista_final = []
            for item in jogos:
                fixture = item.get('fixture', {})
                league = item.get('league', {})
                teams = item.get('teams', {})
                goals = item.get('goals', {})

                # Converte a hora UTC para Brasília
                data_utc = datetime.fromisoformat(fixture.get('date').replace('Z', '+00:00'))
                data_br = data_utc.astimezone(fuso)

                lista_final.append({
                    'Horario_BR': data_br.strftime('%H:%M'),
                    'Liga': f"{league.get('country')} - {league.get('name')}",
                    'Mandante': teams.get('home', {}).get('name'),
                    'Visitante': teams.get('away', {}).get('name'),
                    'Placar': f"{goals.get('home') if goals.get('home') is not None else ''} x {goals.get('away') if goals.get('away') is not None else ''}",
                    'Status': fixture.get('status', {}).get('long')
                })

            # 3. Gera o arquivo CSV
            df = pd.DataFrame(lista_final)
            # Ordena pelos jogos que vão começar agora
            df = df.sort_values(by='Horario_BR')
            df.to_csv('palpites.csv', index=False)
            
            print(f"✅ Sucesso! {len(lista_final)} jogos salvos no arquivo 'palpites.csv'.")
        else:
            print(f"❌ Erro na API: Status {response.status_code}")

    except Exception as e:
        print(f"❌ Erro no script: {e}")

if __name__ == "__main__":
    buscar_jogos_profissionais()
