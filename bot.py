import pandas as pd
import requests
from datetime import datetime
import pytz

def buscar_e_salvar():
    fuso = pytz.timezone('America/Sao_Paulo')
    hoje = datetime.now(fuso).strftime('%Y-%m-%d')
    
    url = "https://v3.football.api-sports.io/fixtures"
    minha_chave = "b4533c0123994fd0a1a0d3a9d125d5ed" # <--- COLE SUA CHAVE AQUI
    
    headers = {
        'x-rapidapi-host': "v3.football.api-sports.io",
        'x-rapidapi-key': minha_chave
    }
    
    params = {'date': hoje}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        dados = response.json()
        jogos = dados.get('response', [])
        
        lista_final = []
        # Filtro para remover jogos que já terminaram
        status_excluir = ['FT', 'AET', 'PEN', 'PST', 'CANC', 'ABD']

        for item in jogos:
            fixture = item.get('fixture', {})
            status_atual = fixture.get('status', {}).get('short')
            
            if status_atual in status_excluir:
                continue

            # Ajuste de Horário
            data_iso = fixture.get('date')
            data_obj = datetime.fromisoformat(data_iso.replace('Z', '+00:00'))
            hora_bra = data_obj.astimezone(fuso).strftime('%H:%M')

            # DEFINIÇÃO DOS NOMES DAS COLUNAS (Exatamente como o index.html pede)
            lista_final.append({
                'Hora': hora_bra,
                'Liga': item['league']['name'],
                'TimeCasa': item['teams']['home']['name'],
                'LogoCasa': item['teams']['home']['logo'],
                'TimeFora': item['teams']['away']['name'],
                'LogoFora': item['teams']['away']['logo'],
                'Palpite': "Escanteios: Over 8.5", 
                'Odd': "1.80",
                'Status': fixture['status']['long']
            })

        if lista_final:
            df = pd.DataFrame(lista_final)
            # SALVANDO O CSV COM OS NOMES CORRETOS
            df.to_csv('palpites.csv', index=False, encoding='utf-8')
            print("✅ Sucesso: palpites.csv atualizado com nomes corretos!")
        else:
            print("⚠️ Nenhum jogo pendente para hoje.")

    except Exception as e:
        print(f"❌ Erro ao processar: {e}")

if __name__ == "__main__":
    buscar_e_salvar()
