import pandas as pd
import requests
from datetime import datetime
import pytz

def buscar_jogos_vips():
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

        # Só jogos que não acabaram
        status_permitidos = ['TBD', 'NS', '1H', 'HT', '2H', 'ET', 'BT', 'LIVE']

        for item in jogos:
            fixture = item.get('fixture', {})
            if fixture.get('status', {}).get('short') not in status_permitidos:
                continue

            data_iso = fixture.get('date')
            data_obj = datetime.fromisoformat(data_iso.replace('Z', '+00:00'))
            hora_bra = data_obj.astimezone(fuso).strftime('%H:%M')
            
            # Lógica de Palpite Detalhado (Exemplos)
            liga = item.get('league', {}).get('name', '')
            palpite = "Escanteios: Over 8.5"
            if "Série A" in liga:
                palpite = "Ambas Marcam: Sim"
            elif item.get('teams', {}).get('home', {}).get('winner'):
                palpite = "Vitoria Casa / +1.5 Gols"

            lista_final.append({
                'Horário': hora_bra,
                'Competição': liga,
                'TimeCasa': item['teams']['home']['name'],
                'LogoCasa': item['teams']['home']['logo'],
                'TimeFora': item['teams']['away']['name'],
                'LogoFora': item['teams']['away']['logo'],
                'Palpite': palpite,
                'Odd': "1.80",
                'Status': fixture.get('status', {}).get('long')
            })

        if lista_final:
            df = pd.DataFrame(lista_final)
            df.to_csv('palpites.csv', index=False)
            print("✅ CSV Atualizado com sucesso!")
        else:
            print("ℹ️ Nenhum jogo ativo encontrado.")

    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    buscar_jogos_vips()
