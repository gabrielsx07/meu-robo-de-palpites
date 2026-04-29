import pandas as pd
import requests
from datetime import datetime

API_KEY = "c721770110cd0d4f1a4157704895ffef"

def analisar_partida(casa, fora):
    favoritos = [
        'Flamengo', 'Palmeiras', 'Real Madrid', 'Manchester City',
        'Barcelona', 'Bayern', 'Liverpool', 'PSG'
    ]

    if any(fav.lower() in casa.lower() for fav in favoritos):
        return f"VENCER UM DOS TEMPOS: {casa}"
    elif any(fav.lower() in fora.lower() for fav in favoritos):
        return f"VENCER UM DOS TEMPOS: {fora}"
    else:
        return "MAIS DE 1.5 GOLS NO JOGO"

def rodar():
    print("🤖 Buscando jogos via API-Football...")

    hoje = datetime.now().strftime("%Y-%m-%d")

    url = f"https://v3.football.api-sports.io/fixtures?date={hoje}"

    headers = {
        "x-apisports-key": API_KEY
    }

    response = requests.get(url, headers=headers)
    data = response.json()

    final = []

    if "response" not in data:
        print("❌ Erro na API")
        return

    for jogo in data["response"]:
        casa = jogo["teams"]["home"]["name"]
        fora = jogo["teams"]["away"]["name"]
        liga = jogo["league"]["name"]
        hora = jogo["fixture"]["date"][11:16]

        palpite = analisar_partida(casa, fora)

        final.append({
            'Hora': hora,
            'Liga': liga,
            'TimeCasa': casa,
            'LogoCasa': jogo["teams"]["home"]["logo"],
            'TimeFora': fora,
            'LogoFora': jogo["teams"]["away"]["logo"],
            'Palpite': palpite
        })

    if final:
        df = pd.DataFrame(final).drop_duplicates()
        df.to_csv('palpites.csv', index=False)
        print(f"✅ {len(df)} jogos salvos!")
    else:
        print("⚠️ Nenhum jogo encontrado")

if __name__ == "__main__":
    rodar()
