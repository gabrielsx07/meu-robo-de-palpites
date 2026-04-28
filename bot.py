import pandas as pd
import requests
from bs4 import BeautifulSoup

def rodar():
    url = "https://apostadorpro.tech"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    final = []
    try:
        response = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(response.text, 'html.parser')
        cards = soup.select('div.card') 

        for card in cards:
            try:
                # 1. Pega os Times
                casa = card.select_one('.home-team').get_text(strip=True)
                fora = card.select_one('.away-team').get_text(strip=True)
                
                # 2. Pega o Palpite do site deles
                sugestao = card.select_one('.tip-container, .badge, .sugestao')
                texto_palpite = sugestao.get_text(strip=True).upper() if sugestao else "OVER 1.5 GOLS"

                # --- LÓGICA DE CLAREZA GORILLA ---
                # Se o palpite for vitória, a gente especifica QUEM
                if "VENCER" in texto_palpite or "CASA" in texto_palpite:
                    palpite_claro = f"Vencer um dos Tempos: {casa}"
                elif "FORA" in texto_palpite:
                    palpite_claro = f"Vencer um dos Tempos: {fora}"
                elif "CANTOS" in texto_palpite or "CORNER" in texto_palpite:
                    palpite_claro = "Mais de 8.5 Escanteios (Jogo)"
                elif "HT" in texto_palpite:
                    palpite_claro = "Gol no 1º Tempo (HT)"
                else:
                    palpite_claro = texto_palpite # Mantém o original se for gols

                # 3. Resto dos dados
                header = card.select_one('.card-header')
                info = header.get_text(separator="|").split("|")
                liga = info[0].strip()
                hora = info[1].strip() if len(info) > 1 else "Hoje"
                imgs = card.select('img')
                logo_c = imgs[0]['src'] if len(imgs) > 0 else ""
                logo_f = imgs[1]['src'] if len(imgs) > 1 else ""

                final.append({
                    'Hora': hora, 'Liga': liga, 'TimeCasa': casa, 
                    'LogoCasa': logo_c, 'TimeFora': fora, 
                    'LogoFora': logo_f, 'Palpite': palpite_claro
                })
            except: continue

    except Exception as e: print(f"Erro: {e}")

    if final:
        pd.DataFrame(final).to_csv('palpites.csv', index=False)
