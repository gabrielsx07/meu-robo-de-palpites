import pandas as pd
import requests
import os
from datetime import datetime

API_KEY = os.getenv("API_KEY")

HEADERS = {
    "x-apisports-key": API_KEY
}

# 🔥 BUSCAR ESTATÍSTICAS
def get_stats(team_id, league_id, season):
    url = f"https://v3.football.api-sports.io/teams/statistics?league={league_id}&season={season}&team={team_id}"
    
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        data = res.json()

        if not data.get("response"):
            return None

        stats = data["response"]

        return {
            "gols_marcados": float(stats["goals"]["for"]["average"]["total"]),
            "gols_sofridos": float(stats["goals"]["against"]["average"]["total"])
        }

    except:
        return None


# 🔥 PEGAR ODDS (OVER 2.5)
def get_odds(fixture_id):
    url = f"https://v3.football.api-sports.io/odds?fixture={fixture_id}"
    
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        data = res.json()

        if not data.get("response"):
            return None

        bookmakers = data["response"][0]["bookmakers"]

        for book in bookmakers:
            for bet in book["bets"]:
                if bet["name"] == "Goals Over/Under":
                    for value in bet["values"]:
                        if value["value"] == "Over 2.5":
                            return float(value["odd"])
    except:
        return None

    return None


# 🧠 VALOR
def tem_valor(prob_real, odd):
    prob_casa = 1 / odd
    return prob_real > prob_casa


# 🧠 ANÁLISE
def analisar_partida(casa_stats, fora_stats, odd):

    if not casa_stats or not fora_stats:
        return ("Dados insuficientes", "-", "-", "-", "Não")

    gols_casa = casa_stats["gols_marcados"]
    gols_fora = fora_stats["gols_marcados"]

    media_total = gols_casa + gols_fora

    prob_real = min(0.80, media_total / 4)

    if odd and tem_valor(prob_real, odd):
        principal = f"🔥 VALOR Over 2.5 (odd {odd})"
        valor = "Sim"
    else:
        if media_total >= 2.5:
            principal = "Mais de 2.5 gols"
        elif media_total >= 2:
            principal = "Mais de 1.5 gols"
        else:
            principal = "Menos de 2.5 gols"
        valor = "Não"

    gols_ht = "Mais de 0.5 HT" if media_total >= 2.2 else "Menos de 1.5 HT"
    ambas = "Sim" if gols_casa > 1.2 and gols_fora > 1.2 else "Não"
    escanteios = "Mais de 9 escanteios" if media_total >= 2.5 else "Mais de 7 escanteios"

    return principal, escanteios, gols_ht, ambas, valor


def rodar():
    print("🤖 Rodando bot com filtro + odds...")

    hoje = datetime.now().strftime("%Y-%m-%d")
    season = datetime.now().year

    url = f"https://v3.football.api-sports.io/fixtures?date={hoje}"

    response = requests.get(url, headers=HEADERS)
    data = response.json()

    final = []

    # 🔥 LIGAS PERMITIDAS
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

        ("USA", "Major League Soccer"),
        ("Saudi Arabia", "Pro League"),

        ("Argentina", "Liga Profesional Argentina"),
        ("Chile", "Primera Division"),
        ("Colombia", "Primera A")
    ]

    limite_jogos = 10
    contador = 0

    for jogo in data.get("response", []):

        if contador >= limite_jogos:
            break

        # STATUS
        if jogo["fixture"]["status"]["short"] != "NS":
            continue

        # TIPO (remove amistoso/copa aleatória)
        tipo = jogo["league"].get("type")
        
        if tipo != "League":
            continue
            
        pais = jogo["league"]["country"]
        liga = jogo["league"]["name"]

        if (pais, liga) not in ligas_permitidas:
            continue

        fixture_id = jogo["fixture"]["id"]
        league_id = jogo["league"]["id"]

        casa = jogo["teams"]["home"]["name"]
        fora = jogo["teams"]["away"]["name"]

        casa_id = jogo["teams"]["home"]["id"]
        fora_id = jogo["teams"]["away"]["id"]

        hora = jogo["fixture"]["date"][11:16]

        casa_stats = get_stats(casa_id, league_id, season)
        fora_stats = get_stats(fora_id, league_id, season)

        odd = get_odds(fixture_id)

        principal, escanteios, gols_ht, ambas, valor = analisar_partida(
            casa_stats, fora_stats, odd
        )

        final.append({
            'Hora': hora,
            'Liga': liga,
            'TimeCasa': casa,
            'TimeFora': fora,

            'Palpite Principal': principal,
            'Escanteios': escanteios,
            'Gols HT': gols_ht,
            'Ambas Marcam': ambas,
            'Tem Valor?': valor
        })

        contador += 1

    if final:
        df = pd.DataFrame(final).drop_duplicates()
        df.to_csv('palpites.csv', index=False)
        print(f"✅ {len(df)} jogos filtrados e analisados!")
    else:
        print("⚠️ Nenhum jogo encontrado")


if __name__ == "__main__":
    rodar()
