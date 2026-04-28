import pandas as pd
import requests
from bs4 import BeautifulSoup

def rodar():
    url = "https://apostadorpro.tech"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    final = []
    print(f"Clonando palpites de {url}...")

    try:
        response = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # O site deles usa 'div' com classes que começam com 'Card_card' ou similar
        # Esse seletor abaixo pega os cards de forma mais agressiva
        cards = soup.find_all('div', class_=lambda x: x and 'card' in x.lower())

        for card in cards:
            try:
                # 1. Pega os Times (procurando por classes de 'team' ou 'name')
                times = card.find_all(class_=lambda x: x and 'team' in x.lower())
                if len(times) < 2: continue
                
                casa = times[0].get_text(strip=True)
                fora = times[1].get_text(strip=True)
                
                # 2. Pega o Palpite Original
                sug_elem = card.find(class_=lambda x: x and ('tip' in x.lower() or 'sugestao' in x.lower() or 'badge' in x.lower()))
                txt_original = sug_elem.get_text(strip=True).upper() if sug_elem else ""

                # --- LÓGICA DE CLAREZA GORILLA ---
                palpite_final = "MAIS DE 1.5 GOLS" # Padrão
                
                if "VENCER" in txt_original or "CASA" in txt_original or "1" in txt_original:
                    palpite_final = f"VENCER UM DOS TEMPOS: {casa}"
                elif "FORA" in txt_original or "2" in txt_original:
                    palpite_final = f"VENCER UM DOS TEMPOS: {fora}"
                elif "CANTOS" in txt_original or "ESC" in txt_original:
                    palpite_final = "MAIS DE 8.5 ESCANTEIOS"
                elif "AMBAS" in txt_original:
                    palpite_final = "AMBAS MARCAM: SIM"
                elif "HT" in txt_original:
                    palpite_final = "GOL NO 1º TEMPO"
                else:
                    palpite_final = txt_original if txt_original else "ANALISAR MERCADO"

                # 3. Logos, Liga e Hora
                imgs = card.find_all('img')
                logo_c = imgs[0]['src'] if len(imgs) > 0 else ""
                logo_f = imgs[1]['src'] if len(imgs) > 1 else ""
                
                info = card.get_text(separator="|").split("|")
                # Tenta achar a liga e hora no texto do card
                liga = "Futebol"
                hora = "Hoje"
                for item in info:
                    if ":" in item and len(item) < 6: hora = item.strip()
                    if len(item) > 5 and len(item) < 30 and item.strip() != casa: liga = item.strip()

                final.append({
                    'Hora': hora, 'Liga': liga, 'TimeCasa': casa, 
                    'LogoCasa': logo_c, 'TimeFora': fora, 
                    'LogoFora': logo_f, 'Palpite': palpite_final
                })
            except: continue

    except Exception as e: print(f"Erro: {e}")

    if final:
        pd.DataFrame(final).to_csv('palpites.csv', index=False)
        print(f"✅ SUCESSO: {len(final)} palpites extraídos!")
    else:
        print("⚠️ Estrutura não reconhecida. Verifique o site.")

if __name__ == "__main__":
    rodar()
