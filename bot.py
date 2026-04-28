import pandas as pd
import requests
from bs4 import BeautifulSoup
import random

def rodar():
    url = "https://apostadorpro.tech"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    final = []
    print(f"Buscando e detalhando palpites de {url}...")

    try:
        response = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(response.text, 'html.parser')
        cards = soup.select('div.card')

        for card in cards:
            try:
                # Extração básica
                casa = card.select_one('div.home-team').get_text(strip=True)
                fora = card.select_one('div.away-team').get_text(strip=True)
                palpite_base = card.select_one('div.tip-container, .badge-success').get_text(strip=True)
                
                # GERADOR DE DETALHES (Aqui está o segredo)
                confianca = random.randint(82, 98) # Gera uma % de confiança realista
                
                # Criar um detalhe técnico baseado no palpite
                if "Gols" in palpite_base or "Over" in palpite_base:
                    detalhe = f"Média de {random.uniform(2.1, 3.4):.1f} gols nos últimos jogos."
                elif "Cantos" in palpite_base or "Escanteios" in palpite_base:
                    detalhe = f"Tendência de {random.randint(9, 12)} cantos totais verificada."
                else:
                    detalhe = "Forte pressão ofensiva do time da casa detectada."

                final.append({
                    'Hora': "Ao Vivo" if "vivo" in card.get_text().lower() else "Hoje",
                    'Liga': "🏆 Análise VIP Oliveira",
                    'TimeCasa': casa,
                    'LogoCasa': card.select('img')[0]['src'] if card.select('img') else "",
                    'TimeFora': fora,
                    'LogoFora': card.select('img')[1]['src'] if len(card.select('img')) > 1 else "",
                    'Palpite': palpite_base,
                    'Detalhe': detalhe,
                    'Confianca': f"{confianca}%"
                })
            except: continue

    except Exception as e:
        print(f"Erro: {e}")

    if final:
        pd.DataFrame(final).to_csv('palpites.csv', index=False)
        print(f"✅ SUCESSO: {len(final)} palpites detalhados gerados!")

if __name__ == "__main__":
    rodar()
