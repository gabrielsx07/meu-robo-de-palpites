import pandas as pd
import requests
import os
from datetime import datetime

API_KEY = os.getenv('API_FOOTBALL_KEY')

def rodar():
    headers = {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': API_KEY}
    
    # TESTE 1: Tenta buscar as ligas disponíveis (Pra ver se a chave funciona)
    print("Testando conexão com a API...")
    teste_conexao = requests.get("https://v3.football.api-sports.io/status", headers=headers).json()
    print(f"Status da Chave: {teste_conexao}")

    # TESTE 2: Busca QUALQUER jogo de hoje (Live ou agendado) de todas as ligas
    hoje = datetime.now().strftime('%Y-%m-%d')
    url = f"https://v3.football.api-sports.io/fixtures?date={hoje}"
    
    final = []
    try:
        r = requests.get(url, headers=headers).json()
        jogos = r.get('response', [])
        
        if not jogos:
            print("API não retornou nenhum jogo no mundo hoje. Isso é erro de chave.")
        else:
            print(f"Sucesso! Achei {len(jogos)} jogos no mundo.")
            for j in jogos[:15]: # Pega os 15 primeiros só pra encher o site
                final.append({
                    'Hora': j['fixture']['date'][11:16],
                    'Liga': j['league']['name'],
                    'TimeCasa': j['teams']['home']['name'],
                    'LogoCasa': j['teams']['home']['logo'],
                    'TimeFora': j['teams']['away']['name'],
                    'LogoFora': j['teams']['away']['logo'],
                    'Palpite': "Análise VIP",
                    'Odd': "1.90"
                })
    except Exception as e:
        print(f"Erro fatal: {e}")

    if final:
        pd.DataFrame(final).to_csv('palpites.csv', index=False)
    else:
        # Se falhar, ele CRIA dados falsos só para você ver se o SITE está lendo o CSV
        dados_fake = [{
            'Hora': '12:00', 'Liga': 'Erro de Chave', 'TimeCasa': 'Chave API', 
            'LogoCasa': '', 'TimeFora': 'Invalida', 'LogoFora': '', 
            'Palpite': 'Verificar Secrets', 'Odd': '0.00'
        }]
        pd.DataFrame(dados_fake).to_csv('palpites.csv', index=False)

if __name__ == "__main__":
    rodar()
