import pandas as pd
import requests
from bs4 import BeautifulSoup

def rodar():
    url = "https://apostadorpro.tech"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    final = []
    print(f"Iniciando clonagem de: {url}")

    try:
        res = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(res.text, 'html.parser')

        # Procura os cards de jogos no site alvo
        cards = soup.select('.card, .match-card') 

        for card in cards:
            try:
                # Extraindo dados (ajustado para o padrão comum de scrapers)
                casa = card.select_one('.home-team, .team-name').get_text(strip=True)
                fora = card.select_one('.away-team, .team-name:last-child').get_text(strip=True)
                palpite = card.select_one('.tip, .badge, .btn-primary').get_text(strip=True)
                
                # Pega as logos
                imgs = card.select('img')
                l_casa = imgs[0]['src'] if len(imgs) > 0 else ""
                l_fora = imgs[1]['src'] if len(imgs) > 1 else ""

                final.append({
                    'Hora': 'Live',
                    'Liga': 'Análise Pro',
                    'TimeCasa': casa,
                    'LogoCasa': l_casa,
                    'TimeFora': fora,
                    'LogoFora': l_fora,
                    'Palpite': palpite
                })
            except: continue

    except Exception as e:
        print(f"Erro: {e}")

    if final:
        pd.DataFrame(final).to_csv('palpites.csv', index=False)
        print(f"✅ {len(final)} palpites clonados!")
    else:
        print("⚠️ Estrutura do site mudou ou está vazia.")

if __name__ == "__main__":
    rodar()
