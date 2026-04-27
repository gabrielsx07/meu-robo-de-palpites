import pandas as pd
import requests
from datetime import datetime
import pytz

def buscar_jogos_reais():
    # 1. Configura fuso de Brasília para pegar o dia certo
    fuso = pytz.timezone('America/Sao_Paulo')
    hoje = datetime.now(fuso).strftime('%Y-%m-%d')
    print(f"⚽ Buscando jogos reais para: {hoje}")

    # Fonte de dados aberta (Jogos Internacionais e Principais Ligas)
    url = "https://www.thesportsdb.com/api/v1/json/3/eventsday.php"
    params = {'d': hoje, 's': 'Soccer'}

    try:
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            dados = response.json()
            eventos = dados.get('events')

            if not eventos:
                print(f"⚠️ Sem jogos registrados para {hoje} nesta fonte.")
                # Cria um arquivo vazio para não dar erro no commit
                df = pd.DataFrame([{'Aviso': 'Sem jogos para hoje'}])
                df.to_csv('palpites.csv', index=False)
                return

            lista_final = []
            for jogo in eventos:
                lista_final.append({
                    'Horario': jogo.get('strTime'),
                    'Liga': jogo.get('strLeague'),
                    'Evento': jogo.get('strEvent'),
                    'Status': jogo.get('strStatus')
                })

            # 2. Salva o CSV
            df = pd.DataFrame(lista_final)
            df.to_csv('palpites.csv', index=False)
            print(f"✅ Sucesso! {len(lista_final)} jogos encontrados.")

        else:
            print(f"❌ Erro no site: {response.status_code}")

    except Exception as e:
        print(f"❌ Falha técnica: {e}")

if __name__ == "__main__":
    buscar_jogos_reais()
