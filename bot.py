import pandas as pd
import requests
from datetime import datetime
import pytz

# 1. Configura o fuso horário de Brasília
fuso = pytz.timezone('America/Sao_Paulo')
hoje = datetime.now(fuso).strftime('%Y-%m-%d')

def buscar_palpites():
    print(f"⚽ Buscando jogos para a data: {hoje}")
    
    # URL do Oddspedia (Exemplo de partidas de futebol)
    url = "https://oddspedia.com/api/v1/getMatches?sport=football&language=br" 
    
    # Headers são ESSENCIAIS para o site não te bloquear na hora
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://oddspedia.com/br/futebol'
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        
        # Se a API deles retornar JSON (comum em sites modernos)
        if response.status_code == 200:
            dados = response.json()
            # Aqui você filtraria os jogos dentro do JSON 'dados'
            # Vamos criar uma lista de exemplo baseada no que o robô deve processar
            jogos_encontrados = []
            
            # --- Lógica de extração (Simulação para teste) ---
            # Se você tiver a estrutura do JSON, mapeamos aqui. 
            # Por enquanto, vou gerar 2 jogos reais para você ver o arquivo salvando.
            jogos_encontrados = [
                {'Data': hoje, 'Time Casa': 'Time A', 'Time Fora': 'Time B', 'Palpite': 'Vitoria Casa'},
                {'Data': hoje, 'Time Casa': 'Time C', 'Time Fora': 'Time D', 'Palpite': 'Empate'}
            ]
            
            if not jogos_encontrados:
                print("⚠ O site respondeu, mas não havia jogos nos critérios.")
                return

            # 2. Salva em CSV
            df = pd.DataFrame(jogos_encontrados)
            df.to_csv('palpites.csv', index=False)
            print(f"✅ {len(jogos_encontrados)} palpites gerados no arquivo palpites.csv!")
            
        else:
            print(f"❌ Erro de conexão: Status {response.status_code}")

    except Exception as e:
        print(f"❌ Falha crítica no robô: {e}")

if __name__ == "__main__":
    buscar_palpites()
