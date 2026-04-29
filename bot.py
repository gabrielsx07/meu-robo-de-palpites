import pandas as pd
import requests

def analisar_partida(casa, fora):
    favoritos = [
        'Flamengo', 'Palmeiras', 'Real Madrid', 'Man City',
        'Barcelona', 'Bayern', 'Liverpool', 'PSG'
    ]

    if any(fav.lower() in casa.lower() for fav in favoritos):
        return f"VENCER UM DOS TEMPOS: {casa}"
    elif any(fav.lower() in fora.lower() for fav in favoritos):
        return f"VENCER UM DOS TEMPOS: {fora}"
    else:
        return "MAIS DE 1.5 GOLS NO JOGO"

def rodar():
    print("🤖 Buscando jogos via API...")

    url = "https://www.thesportsdb.com/api/v1/json/3/eventsday.php?s=Soccer"

    response = requests.get(url)
    data = response.json()

    final = []

    if not data or not data.get("events"):
        print("⚠️ Nenhum jogo encontrado")
        return

    for jogo in data["events"]:
        casa = jogo.get("strHomeTeam")
        fora = jogo.get("strAwayTeam")
        liga = jogo.get("strLeague")
        hora = jogo.get("strTime")

        if not casa or not fora:
            continue

        palpite = analisar_partida(casa, fora)

        final.append({
            'Hora': hora,
            'Liga': liga,
            'TimeCasa': casa,
            'LogoCasa': '',
            'TimeFora': fora,
            'LogoFora': '',
            'Palpite': palpite
        })

    df = pd.DataFrame(final).drop_duplicates()
    df.to_csv('palpites.csv', index=False)

    print(f"✅ {len(df)} jogos salvos!")

if __name__ == "__main__":
    rodar()
