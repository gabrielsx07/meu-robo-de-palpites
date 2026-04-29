import pandas as pd
import requests
import os
from datetime import datetime

API_KEY = os.getenv("API_KEY")

HEADERS = {
    "x-apisports-key": API_KEY
}

# 🔥 BUSCAR ESTATÍSTICA DO TIME
def get_stats(team_id, league_id, season):
    url = f"https://v3.football.api-sports.io/teams/statistics?league={league_id}&season={season}&team={team_id}"
    
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        data = res.json()

        if not data.get("response"):
            return None

        stats = data["response"]

        gols_marcados = float(stats["goals"]["for"]["average"]["total"])
        gols_sofridos = float(stats["goals"]["against"]["average"]["total"])

        return {
            "gols_marcados": gols_marcados,
            "gols_sofridos": gols_sofridos
        }

    except:
        return None


# 🧠 ANÁLISE REAL
def analisar_partida(casa_stats, fora_stats):

    if not casa_stats or not fora_stats:
        return ("Dados insuficientes", "-", "-", "-")

    media_total = casa_stats["gols_marcados"] + fora_stats["gols_marcados"]

    # 🎯 PALPITE PRINCIPAL
    if media_total >= 2.8:
        principal = "Mais de 2.5 gols"
    elif media_total >= 2.2:
        principal = "Mais de 1.5 gols"
    else:
        principal = "Menos de 2.5 gols"

    # ⚽ GOLS HT
    if media_total >= 2.5:
        gols_ht = "Mais de 0.5 HT"
    else:
        gols_ht = "Menos de 1.5 HT"

    # 🔁 AMBAS MARCAM
    if casa_stats["gols_marcados"] > 1.2 and fora_stats["gols_marcados"] > 1.2:
        ambas = "Sim"
    else:
        ambas = "Não"

    # 🚩 ESCANTEIOS (simulado com base ofensiva)
    if media_total >= 2.5:
        escanteios = "Mais de 9 escanteios"
    else:
        escanteios = "Mais de 7 escanteios"

    return principal, escanteios, gols_ht, ambas


def rodar():
    print("🤖 Buscando jogos com estatística real...")

    hoje = datetime.now().strftime("%Y-%m-%d")
    season = datetime.now().year

    url = f"https://v3.football.api-sports.io/fixtures?date={hoje}"

    response = requests.get(url, headers=HEADERS)
    data = response.json()

    final = []

    # ⚠️ LIMITE PRA NÃO ESTOURAR API
    limite_jogos = 10
    contador = 0

    for jogo in data.get("response", []):

        if contador >= limite_jogos:
            break

        # STATUS
        if jogo["fixture"]["status"]["short"] != "NS":
            continue

        league_id = jogo["league"]["id"]

        # TIMES
        casa = jogo["teams"]["home"]["name"]
        fora = jogo["teams"]["away"]["name"]

        casa_id = jogo["teams"]["home"]["id"]
        fora_id = jogo["teams"]["away"]["id"]

        hora = jogo["fixture"]["date"][11:16]

        # 🔥 PEGAR ESTATÍSTICAS
        casa_stats = get_stats(casa_id, league_id, season)
        fora_stats = get_stats(fora_id, league_id, season)

        principal, escanteios, gols_ht, ambas = analisar_partida(casa_stats, fora_stats)

        final.append({
            'Hora': hora,
            'Liga': jogo["league"]["name"],
            'TimeCasa': casa,
            'LogoCasa': jogo["teams"]["home"]["logo"],
            'TimeFora': fora,
            'LogoFora': jogo["teams"]["away"]["logo"],

            'Palpite Principal': principal,
            'Escanteios': escanteios,
            'Gols HT': gols_ht,
            'Ambas Marcam': ambas
        })

        contador += 1

    if final:
        df = pd.DataFrame(final).drop_duplicates()
        df.to_csv('palpites.csv', index=False)
        print(f"✅ {len(df)} jogos analisados com estatística real!")
    else:
        print("⚠️ Nenhum jogo encontrado")


if __name__ == "__main__":
    rodar()
