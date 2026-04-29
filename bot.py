import pandas as pd
import requests
import os
from datetime import datetime

API_KEY = os.getenv("API_KEY")

def analisar_partida(casa, fora):
    ligas_permitidas = [
    # Brasil
    ("Brazil", "Serie A"),
    ("Brazil", "Serie B"),

    # Inglaterra
    ("England", "Premier League"),
    ("England", "Championship"),

    # Espanha
    ("Spain", "La Liga"),
    ("Spain", "Segunda Division"),

    # Itália
    ("Italy", "Serie A"),
    ("Italy", "Serie B"),

    # Alemanha
    ("Germany", "Bundesliga"),
    ("Germany", "2. Bundesliga"),

    # França
    ("France", "Ligue 1"),
    ("France", "Ligue 2"),

    # Europa
    ("World", "UEFA Champions League"),
    ("World", "UEFA Europa League"),

    # EUA
    ("USA", "Major League Soccer"),

    # Arábia Saudita
    ("Saudi Arabia", "Pro League"),

    # América do Sul
    ("World", "CONMEBOL Libertadores"),
    ("World", "CONMEBOL Sudamericana"),

    # Argentina
    ("Argentina", "Liga Profesional Argentina"),

    # Chile
    ("Chile", "Primera Division"),

    # Colômbia
    ("Colombia", "Primera A")
]

    if any(fav.lower() in casa.lower() for fav in favoritos):
        return f"VENCER UM DOS TEMPOS: {casa}"
    elif any(fav.lower() in fora.lower() for fav in favoritos):
        return f"VENCER UM DOS TEMPOS: {fora}"
    else:
        return "MAIS DE 1.5 GOLS NO JOGO"

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

    for jogo in data.get("response", []):
       # STATUS (só jogos futuros)
    if jogo["fixture"]["status"]["short"] != "NS":
    continue

       # LIGA
       pais = jogo["league"]["country"]
       liga = jogo["league"]["name"]

    if (pais, liga) not in ligas_permitidas:
    continue

       # HORÁRIO (opcional)
       hora_str = jogo["fixture"]["date"][11:13]
       hora_int = int(hora_str)

    if hora_int < 10 or hora_int > 23:
    continue

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
