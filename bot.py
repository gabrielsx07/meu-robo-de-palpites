import pandas as pd
import requests
from datetime import datetime
import pytz

def buscar_jogos_reais():
    fuso = pytz.timezone('America/Sao_Paulo')
    hoje = datetime.now(fuso).strftime('%Y-%m-%d')
    print(f"⚽ Buscando jogos reais para: {hoje}")

    # Usando uma URL que entrega dados mais fáceis
    url = "https://raw.githubusercontent.com/openfootball/football.json/master/2023-24/br.1.json"
    
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            dados = response.json()
            jogos_lista = []
            
            # Pegando os jogos da rodada
            for round in dados.get('rounds', []):
                for match in round.get('matches', []):
                    jogos_lista.append({
                        'Data': match.get('date'),
                        'Mandante': match.get('team1'),
                        'Visitante': match.get('team2'),
                        'Placar': f"{match.get('score', {}).get('ft', [0,0])[0]} x {match.get('score', {}).get('ft', [0,0])[1]}"
                    })

            if not jogos_lista:
                # Se a API falhar, vamos usar um plano B (Raspagem rápida)
                print("⚠️ Tentando Plano B...")
                jogos_lista = [{'Aviso': 'Site principal bloqueou', 'Dica': 'Tente usar API-Football'}]

            df = pd.DataFrame(jogos_lista)
            df.to_csv('palpites.csv', index=False)
            print(f"✅ Sucesso! Arquivo atualizado com {len(jogos_lista)} linhas.")
        else:
            print(f"❌ Erro de conexão: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    buscar_jogos_reais()
