import pandas as pd
import requests
from datetime import datetime
import pytz

def realizar_estudo_tecnico(item):
    # Lógica de análise baseada em dados reais do jogo
    teams = item.get('teams', {})
    home_fav = teams.get('home', {}).get('winner')
    league_name = item.get('league', {}).get('name', '')

    if home_fav:
        return f"Vitória {teams['home']['name']} / +1.5 Gols", 1.72
    elif "Série A" in league_name or "Premier" in league_name:
        return "Ambas Marcam: Sim", 1.85
    else:
        return "Over 8.5 Escanteios", 1.60

def buscar_jogos_reais():
    fuso = pytz.timezone('America/Sao_Paulo')
    hoje = datetime.now(fuso).strftime('%Y-%m-%d')
    
    url = "https://v3.football.api-sports.io/fixtures"
    minha_chave = "b4533c0123994fd0a1a0d3a9d125d5ed" # <--- COLOCA A TUA CHAVE AQUI
    
    headers = {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': minha_chave}
    
    # Filtramos apenas as ligas mais importantes para evitar "jogos fantasma"
    # Podes adicionar mais IDs de ligas se quiseres
    ligas_importantes = [13, 61, 71, 39, 140, 94, 135, 78] # Liberta, Brasileirão, Premier, La Liga, etc.
    
    params = {'date': hoje}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        dados = response.json()
        jogos = dados.get('response', [])
        lista_final = []

        for item in jogos:
            fixture = item.get('fixture', {})
            league = item.get('league', {})
            
            # FILTRO 1: Apenas ligas conhecidas (opcional, podes comentar se quiseres todos os jogos)
            # if league.get('id') not in ligas_importantes: continue

            # FILTRO 2: Apenas jogos que ainda não começaram ou estão no início
            if fixture.get('status', {}).get('short') not in ['NS', 'TBD', '1H', 'HT']:
                continue

            # Estudo do palpite
            palpite, odd = realizar_estudo_tecnico(item)

            data_obj = datetime.fromisoformat(fixture.get('date').replace('Z', '+00:00'))
            hora_bra = data_obj.astimezone(fuso).strftime('%H:%M')

            lista_final.append({
                'Hora': hora_bra,
                'Liga': league.get('name'),
                'TimeCasa': item['teams']['home']['name'],
                'LogoCasa': item['teams']['home']['logo'],
                'TimeFora': item['teams']['away']['name'],
                'LogoFora': item['teams']['away']['logo'],
                'Palpite': palpite,
                'Odd': odd,
                'Status': fixture['status']['long']
            })

        if lista_final:
            df = pd.DataFrame(lista_final)
            # Ordenar por hora para ficar organizado
            df = df.sort_values(by='Hora')
            df.to_csv('palpites.csv', index=False)
            print(f"✅ {len(lista_final)} jogos reais processados.")
        else:
            # Se não houver jogos, cria um CSV vazio para não dar erro no site
            pd.DataFrame(columns=['Hora','Liga','TimeCasa','LogoCasa','TimeFora','LogoFora','Palpite','Odd','Status']).to_csv('palpites.csv', index=False)

    except Exception as e:
        print(f"❌ Erro ao filtrar jogos: {e}")

if __name__ == "__main__":
    buscar_jogos_reais()
