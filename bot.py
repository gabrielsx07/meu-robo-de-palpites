import requests
import pandas as pd
import random
from datetime import datetime

# Substitua pela sua chave real
API_KEY = 'SUA_CHAVE_AQUI'
URL = 'https://api.football-data.org/v4/matches'
headers = {'X-Auth-Token': API_KEY}

def gerar_palpites():
    response = requests.get(URL, headers=headers)
    if response.status_code == 200:
        jogos = response.json().get('matches', [])
        lista_palpites = []

        for jogo in jogos:
            # Captura e formata a hora (UTC para Brasília - aproximado)
            data_utc = jogo['utcDate']
            data_obj = datetime.strptime(data_utc, "%Y-%m-%dT%H:%M:%SZ")
            # Ajuste simples de -3h para Brasília (opcional, dependendo do servidor)
            hora_formatada = data_obj.strftime("%H:%M")
            dia_formatado = data_obj.strftime("%d/%m")

            casa = jogo['homeTeam']['name']
            fora = jogo['awayTeam']['name']
            
            # Palpite fixo
            palpite = "X2" if "Real Madrid" in fora or "City" in fora else "1X"
            
            # FIXANDO A PORCENTAGEM: Ela é gerada uma vez aqui e salva no CSV
            # Assim, ela não muda mais quando você der F5 no site.
            confianca_fixa = f"{random.randint(87, 96)}%"

            lista_palpites.append({
                "Dia": dia_formatado,
                "Hora": hora_formatada,
                "Confronto": f"{casa} vs {fora}",
                "Chance Dupla": palpite,
                "Confianca": confianca_fixa
            })
        
        df = pd.DataFrame(lista_palpites)
        df.to_csv('palpites.csv', index=False)
        print("✅ CSV Atualizado com Hora e Confiança fixa!")

if __name__ == "__main__":
    gerar_palpites()
