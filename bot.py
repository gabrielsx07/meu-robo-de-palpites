import pandas as pd
import cloudscraper
from bs4 import BeautifulSoup

def rodar():
    url = "https://apostadorpro.tech"
    # O cloudscraper passa pelo bloqueio do Cloudflare que você viu nas fotos
    scraper = cloudscraper.create_scraper()
    
    final = []
    print(f"Buscando palpites em {url}...")

    try:
        response = scraper.get(url, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # O site deles usa 'Card_card__...' nas classes. Buscamos qualquer div de card.
        cards = soup.find_all('div', class_=lambda x: x and 'card' in x.lower())

        for card in cards:
            try:
                # Localiza times (procurando textos em negrito ou classes de team)
                teams = card.find_all(['p', 'span', 'div'], class_=lambda x: x and ('team' in x.lower() or 'name' in x.lower()))
                if len(teams) < 2: continue
                
                casa = teams[0].get_text(strip=True)
                fora = teams[1].get_text(strip=True)
                
                # Pega a sugestão (palpite)
                tip_elem = card.find(class_=lambda x: x and ('tip' in x.lower() or 'badge' in x.lower() or 'sugestao' in x.lower()))
                original = tip_elem.get_text(strip=True).upper() if tip_elem else "OVER 1.5 GOLS"

                # --- Lógica de clareza do Gorilla ---
                if "VENCER" in original or "CASA" in original:
                    palpite = f"VENCER UM DOS TEMPOS: {casa}"
                elif "FORA" in original:
                    palpite = f"VENCER UM DOS TEMPOS: {fora}"
                elif "CANTOS" in original:
                    palpite = "MAIS DE 8.5 ESCANTEIOS"
                else:
                    palpite = original

                # Logos, Liga e Hora
                imgs = card.find_all('img')
                l_casa = imgs[0]['src'] if len(imgs) > 0 else ""
                l_fora = imgs[1]['src'] if len(imgs) > 1 else ""
                
                info = card.get_text(separator="|").split("|")
                liga = info[0].strip() if len(info) > 0 else "Futebol"
                hora = "Hoje"
                for i in info:
                    if ":" in i and len(i) <= 5: hora = i.strip()

                final.append({
                    'Hora': hora, 'Liga': liga, 'TimeCasa': casa, 
                    'LogoCasa': l_casa, 'TimeFora': fora, 
                    'LogoFora': l_fora, 'Palpite': palpite
                })
            except: continue

    except Exception as e:
        print(f"Erro: {e}")

    if final:
        pd.DataFrame(final).drop_duplicates().to_csv('palpites.csv', index=False)
        print(f"✅ SUCESSO: {len(final)} palpites extraídos!")
    else:
        # Se falhar, avisa no log
        print("⚠️ Nenhum palpite encontrado. Verifique se o site mudou as classes.")

if __name__ == "__main__":
    rodar()
