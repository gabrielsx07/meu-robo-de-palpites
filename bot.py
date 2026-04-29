import pandas as pd
import requests
import os
import random
from datetime import datetime

API_KEY = os.getenv("API_KEY")

HEADERS = {
    "x-apisports-key": API_KEY
}

# 🔥 PEGAR ESTATÍSTICAS DO TIME
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


# 🧠 ANÁLISE INTELIGENTE + VARIADA
def analisar_partida(casa_stats, fora_stats):

    if not casa_stats or not fora_stats:
        return ("Dados insuficientes", "-", "-", "-")

    gols_casa = casa_stats["gols_marcados"]
    gols_fora = fora_stats["gols_marcados"]

    sofre_casa = casa_stats["gols_sofridos"]
    sofre_fora = fora_stats["gols_sofridos"]

    media_total = gols_casa + gols_fora

    # 🎯 PERFIL DO JOGO
    if media_total >= 3:
        perfil = "muito_aberto"
    elif media_total >= 2:
        perfil = "medio"
    else:
        perfil = "fechado"

    # 🔥 PALPITE PRINCIPAL (variado)
    if perfil == "muito_aberto":
        principal = random.choice([
            "Mais de 2.5 gols",
            "Ambas marcam",
            "Mais de 3.5 gols"
        ])

    elif perfil == "medio":
        principal = random.choice([
            "Mais de 1.5 gols",
            "Ambas marcam",
            "Dupla chance + over 1.5"
        ])

    else:
        principal = random.choice([
            "Menos de 2.5 gols",
            "Empate",
            "Menos de 3.5 gols"
        ])

    # ⚽ AMBAS MARCAM
    if gols_casa > 1.2 and gols_fora > 1.2 and sofre_casa > 1 and sofre_fora > 1:
        ambas = random.choice(["Sim", "Sim", "Não"])
    else:
        ambas = "Não"

    # 🧠 GOLS HT
    if media_total >= 2.5:
        gols_ht = random.choice([
            "Mais de 0.5 HT",
            "Mais de 1.0 HT"
        ])
    else:
        gols_ht = random.choice([
            "Mais de 0.5 HT",
            "Menos de 1.5 HT"
        ])

    # 🚩 ESCANTEIOS
    if media_total >= 2.5:
        escanteios = random.choice([
            "Mais de 8.5 escanteios",
            "Mais de 9.5 escanteios"
        ])
    else:
        escanteios = random.choice([
            "Mais de 7 escanteios",
            "Menos de 10 escanteios"
        ])

    return principal, escanteios, gols_ht, ambas


def rodar():
    print("🤖 Buscando jogos com análise real...")

    hoje = datetime.now().strftime("%Y-%m-%d")
    season = datetime.now().year

    url = f"https://v3.football.api-sports.io/fixtures?date={hoje}"

    response = requests.get(url, headers=HEADERS)
    data = response.json()

    final = []

    # ⚠️ LIMITADOR PRA NÃO ESTOURAR API
    limite_jogos = 12
    contador = 0

    for jogo in data.get("response", []):

        if contador >= limite_jogos:
            break

        # STATUS (só jogos futuros)
        if jogo["fixture"]["status"]["short"] != "NS":
            continue

        league_id = jogo["league"]["id"]

        casa = jogo["teams"]["home"]["name"]
        fora = jogo["teams"]["away"]["name"]

        casa_id = jogo["teams"]["home"]["id"]
        fora_id = jogo["teams"]["away"]["id"]

        hora = jogo["fixture"]["date"][11:16]

        # 🔥 ESTATÍSTICAS
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
        print(f"✅ {len(df)} jogos analisados com variedade real!")
    else:
        print("⚠️ Nenhum jogo encontrado")


if __name__ == "__main__":
    rodar()
