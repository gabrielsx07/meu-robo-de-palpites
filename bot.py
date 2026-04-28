import pandas as pd
import requests
from bs4 import BeautifulSoup

def rodar():
    url = "https://apostadorpro.tech"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    final = []
    print(f"Buscando palpites em {url}...")

    try:
        response = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(response.text, 'html.parser')

        # O site deles usa cards para os jogos. Vamos localizar cada um.
        cards = soup.select('div.card') # Seleciona os cards de jogos

        for card in cards:
            try:
                # Pega a Liga e a Hora (geralmente no topo do card)
                info = card.select_one('div.card-header').get_text(separator="|").split("|")
                liga = info[0].strip()
                hora = info[1].strip() if len(info) > 1 else "Hoje"

                # Pega os nomes dos times
                casa = card.select_one('div.home-team').get_text(strip=True)
                fora = card.select_one('div.away-team').get_text(strip=True)

                # Pega as logos
                logos = card.select('img')
                logo_casa = logos[0]['src'] if len(logos) > 0 else ""
                logo_fora = logos[1]['src'] if len(logos) > 1 else ""

                # Pega o palpite que está no botão ou área de destaque
                palpite = card.select_one('div.tip-container, .badge-success').get_text(strip=True)

                final.append({
                    'Hora': hora,
                    'Liga': liga,
                    'TimeCasa': casa,
                    'LogoCasa': logo_casa,
                    'TimeFora': fora,
                    'LogoFora': logo_fora,
                    'Palpite': palpite
                })
            except:
                continue

    except Exception as e:
        print(f"Erro ao clonar: {e}")

    if final:
        pd.DataFrame(final).to_csv('palpites.csv', index=False)
        print(f"✅ SUCESSO: {len(final)} palpites clonados!")
    else:
        print("⚠️ O site deles pode ter mudado a estrutura. Me avise!")

if __name__ == "__main__":
    rodar()
