import pandas as pd
import requests
from datetime import datetime
import pytz

def buscar_jogos_elite():
    fuso = pytz.timezone('America/Sao_Paulo')
    hoje = datetime.now(fuso).strftime('%Y-%m-%d')
    
    url = "https://v3.football.api-sports.io/fixtures"
    minha_chave = "b4533c0123994fd0a1a0d3a9d125d5ed" # <--- COLOQUE SUA CHAVE AQUI
    
    headers = {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': minha_chave}
    params = {'date': hoje}

    # LISTA DE IDs DAS LIGAS QUE IMPORTAM (Pode adicionar mais se quiser)
    # 71 = Brasileirão A, 72 = Brasileirão B, 13 = Liberta, 39 = Premier League
    # 140 = La Liga, 135 = Serie A (Itália), 78 = Bundesliga, 61 = Ligue 1
    # 2 = Champions League, 3 = Europa League
    ligas_vips = [71, 72, 13, 39, 140, 135, 78, 61, 2, 3]

    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        dados = response.json()
        jogos = dados.get('response', [])
        lista_final = []

        for item in jogos:
            liga_id = item.get('league', {}).get('id')
            
            # FILTRO PESADO: Se a liga não estiver na nossa lista VIP, o robô ignora
            if liga_id not in ligas_vips:
                continue

            fixture = item.get('fixture', {})
            # Ignora jogos que já terminaram
            if fixture.get('status', {}).get('short') in ['FT', 'AET', 'PEN']:
                continue

            data_obj = datetime.fromisoformat(fixture.get('date').replace('Z', '+00:00'))
            hora_bra = data_obj.astimezone(fuso).strftime('%H:%M')

            lista_final.append({
                'Hora': hora_bra,
                'Liga': item['league']['name'],
                'TimeCasa': item['teams']['home']['name'],
                'LogoCasa': item['teams']['home']['logo'],
                'TimeFora': item['teams']['away']['name'],
                'LogoFora': item['teams']['away']['logo'],
                'Palpite': "Análise: Over 1.5 Gols", # Aqui entra sua lógica de estudo
                'Odd': "1.75",
                'Status': fixture['status']['long']
            })

        if lista_final:
            df = pd.DataFrame(lista_final)
            df = df.sort_values(by='Hora') # Organiza por horário
            df.to_csv('palpites.csv', index=False)
            print(f"✅ Sucesso! {len(lista_final)} jogos de elite encontrados.")
        else:
            # Cria CSV vazio se não tiver jogo importante hoje para não quebrar o site
            pd.DataFrame(columns=['Hora','Liga','TimeCasa','LogoCasa','TimeFora','LogoFora','Palpite','Odd','Status']).to_csv('palpites.csv', index=False)
            print("ℹ️ Nenhuma liga VIP com jogos hoje.")

    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    buscar_jogos_elite()
