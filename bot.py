import pandas as pd
import requests
import os
from datetime import datetime

API_KEY = os.getenv("API_KEY")

def analisar_partida(casa, fora):
    favoritos = [
        'Flamengo', 'Palmeiras', 'Real Madrid', 'Manchester City',
        'Barcelona', 'Bayern', 'Liverpool', 'PSG',
        'Arsenal', 'Inter', 'Milan', 'Juventus'
    ]

    casa_forte = any(fav.lower() in casa.lower() for fav in favoritos)
    fora_forte = any(fav.lower() in fora.lower() for fav in favoritos)

    # Palpite principal
    if casa_forte and fora_forte:
        principal = "Mais de 2.5 gols + Ambas marcam"
    elif casa_forte:
        principal = f"{casa} marca + Mais de 1.5 gols"
    elif fora_forte:
        principal = f"{fora} marca + Mais de 1.5 gols"
    else:
        principal = "Mais de 1.5 gols"

    # Palpites adicionais
    escanteios = "Mais de 8 escanteios"
    gols_ht = "Mais de 0.5 gol no 1º tempo"
    ambas = "Sim"

    return principal, escanteios, gols_ht, ambas


def rodar():
    print("🤖 Buscando jogos...")

    hoje = datetime.now().strftime("%Y-%m-%d")

    url = f"https://v3.football.api-sports.io/fixtures?date={hoje}"

    headers = {
        "x-apisports-key": API_KEY
    }

    response = requests.get(url, headers=headers)
    data = response.json()

    final = []

    ligas_permitidas = [
        ("Brazil", "Serie A"),
        ("Brazil", "Serie B"),

        ("England", "Premier League"),
        ("England", "Championship"),

        ("Spain", "La Liga"),
        ("Spain", "Segunda Division"),

        ("Italy", "Serie A"),
        ("Italy", "Serie B"),

        ("Germany", "Bundesliga"),
        ("Germany", "2. Bundesliga"),

        ("France", "Ligue 1"),
        ("France", "Ligue 2"),

        ("World", "UEFA Champions League"),
        ("World", "UEFA Europa League"),

        ("USA", "Major League Soccer"),

        ("Saudi Arabia", "Pro League"),

        ("World", "CONMEBOL Libertadores"),
        ("World", "CONMEBOL Sudamericana"),

        ("Argentina", "Liga Profesional Argentina"),
        ("Chile", "Primera Division"),
        ("Colombia", "Primera A")
    ]

    for jogo in data.get("response", []):

        # STATUS (só jogos futuros)
        if jogo["fixture"]["status"]["short"] != "NS":
            continue

        # LIGA
        pais = jogo["league"]["country"]
        liga = jogo["league"]["name"]

        if (pais, liga) not in ligas_permitidas:
            continue

        # HORÁRIO (entre 10h e 23h)
        hora_str = jogo["fixture"]["date"][11:13]
        hora_int = int(hora_str)

        if hora_int < 10 or hora_int > 23:
            continue

        # TIMES
        casa = jogo["teams"]["home"]["name"]
        fora = jogo["teams"]["away"]["name"]
        hora = jogo["fixture"]["date"][11:16]

        # PALPITES
        principal, escanteios, gols_ht, ambas = analisar_partida(casa, fora)

        final.append({
            'Hora': hora,
            'Liga': liga,
            'TimeCasa': casa,
            'LogoCasa': jogo["teams"]["home"]["logo"],
            'TimeFora': fora,
            'LogoFora': jogo["teams"]["away"]["logo"],

            'Palpite Principal': principal,
            'Escanteios': escanteios,
            'Gols HT': gols_ht,
            'Ambas Marcam': ambas
        })

    if final:
        df = pd.DataFrame(final).drop_duplicates()
        df.to_csv('palpites.csv', index=False)
        print(f"✅ {len(df)} jogos salvos!")
    else:
        print("⚠️ Nenhum jogo encontrado")


if __name__ == "__main__":
    rodar()
