import pandas as pd
import requests
from datetime import datetime
import pytz
import random

def gerar_analise_vip(item):
    league = item.get('league', {}).get('name', '')
    home = item.get('teams', {}).get('home', {}).get('name', '')
    away = item.get('teams', {}).get('away', {}).get('name', '')
    
    # Lista de palpites detalhados para o robô escolher e variar
    opcoes = [
        f"Escanteios: Over 8.5 no jogo",
        f"Gols: +0.5 no 1º Tempo",
        f"Ambas Marcam: Sim",
        f"Vencedor: {home} ou Empate",
        f"Escanteios: {home} mais de 4.5",
        f"Gols: Over 1.5 no total",
        f"1º Tempo: Empate ou {away}"
    ]
    
    # Lógica inteligente: Se for liga de elite, foca em gols/ambas
    if "Série A" in league or "Premier League" in league:
        palpite = random.choice([opcoes[1], opcoes[2], opcoes[5]])
    # Se for jogo com favorito claro
    elif item.get('teams', {}).get('home', {}).get('winner'):
        palpite = f"Vitória {home} / Over 1.5 Gols"
    # Padrão: Escanteios ou Gols no 1º tempo
    else:
        palpite = random.choice([opcoes[0], opcoes[1], opcoes[4]])
        
    return palpite

def buscar_jogos_completos():
    fuso = pytz.timezone('America/Sao_Paulo')
    hoje = datetime.now(fuso).strftime('%Y-%m-%d')
    
    url = "https://v3.football.api-sports.io/fixtures"
    minha_chave = "b4533c0123994fd0a1a0d3a9d125d5ed" # COLOQUE SUA CHAVE AQUI
    
    headers = {
        'x-rapidapi-host': "v3.football.api-sports.io",
        'x-rapidapi-key': minha_chave
    }
    
    params = {'date': hoje}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        if response.status_code == 200:
            dados = response.json()
            jogos = dados.get('response', [])
            
            lista_final = []
            # Status para remover (jogos encerrados)
            status_remover = ['FT', 'AET', 'PEN', 'PST', 'CANC', 'ABD']

            for item in jogos:
                fixture = item.get('fixture', {})
                if fixture.get('status', {}).get('short') in status_remover:
                    continue

                # Ajuste de Horário
                data_iso = fixture.get('date')
                data_obj = datetime.fromisoformat(data_iso.replace('Z', '+00:00'))
                hora_bra = data_obj.astimezone(fuso).strftime('%H:%M')

                # Gera o palpite detalhado usando a nova função
                analise = gerar_analise_vip(item)

                lista_final.append({
                    'Horário': hora_bra,
                    'Competição': item.get('league', {}).get('name'),
                    'Partida': f"{item['teams']['home']['name']} x {item['teams']['away']['name']}",
                    'Palpite Detalhado': analise,
                    'Situação': fixture.get('status', {}).get('long')
                })

            if lista_final:
                df = pd.DataFrame(lista_final)
                df = df.sort_values(by='Horário')
                df.to_csv('palpites.csv', index=False)
                print(f"✅ {len(lista_final)} análises VIP geradas!")
            else:
                pd.DataFrame(columns=['Horário','Competição','Partida','Palpite Detalhado','Situação']).to_csv('palpites.csv', index=False)

    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    buscar_jogos_completos()
