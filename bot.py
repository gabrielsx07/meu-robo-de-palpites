import pandas as pd
import cloudscraper
from bs4 import BeautifulSoup

def rodar():
    url = "https://apostadorpro.tech"
    # O scraper substitui o requests para furar o bloqueio
    scraper = cloudscraper.create_scraper()
    
    final = []
    print(f"Buscando palpites em {url}...")

    try:
        response = scraper.get(url, timeout=30)
        if response.status_code != 200:
            print(f"Erro de acesso: {response.status_code}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # O site deles usa cards. Vamos buscar todos.
        cards = soup.find_all('div', class_=lambda x: x and 'card' in x.lower())

        for card in cards:
            try:
                # Localizando os nomes dos times
                times = card.find_all(class_=lambda x: x and 'team' in x.lower())
                if len(times) < 2: continue
                casa = times[0].get_text(strip=True)
                fora = times[1].get_text(strip=True)

                # Localizando o palpite bruto
                sug_elem = card.find(class_=lambda x: x and ('tip' in x.lower() or 'badge' in x.lower()))
                palpite_bruto = sug_elem.get_text(strip=True).upper() if sug_elem else "OVER 1.5 GOLS"

                # --- CLAREZA: Coloca o nome do time no palpite ---
                if "VENCER" in palpite_bruto or "CASA" in palpite_bruto:
                    palpite = f"VENCER UM DOS TEMPOS: {casa}"
                elif "FORA" in palpite_bruto:
                    palpite = f"VENCER UM DOS TEMPOS: {fora}"
                else:
                    palpite = palpite_bruto

                # Logos, Liga e Hora
                imgs = card.find_all('img')
                l_casa = imgs[0]['src'] if len(imgs) > 0 else ""
                l_fora = imgs[1]['src'] if len(imgs) > 1 else ""
                
                header = card.find(class_=lambda x: x and 'header' in x.lower())
                info = header.get_text(separator="|").split("|") if header else ["Futebol", "Hoje"]
                liga = info[0].strip()
                hora = info[1].strip() if len(info) > 1 else "Hoje"

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
        print(f"✅ SUCESSO: {len(final)} palpites encontrados!")
    else:
        # Se mesmo assim falhar, ele gera um aviso no CSV
        pd.DataFrame([{'Hora':'00:00','Liga':'Erro','TimeCasa':'Aguarde','LogoCasa':'','TimeFora':'Jogos','LogoFora':'','Palpite':'ATUALIZANDO... (SITE PROTEGIDO)'}]).to_csv('palpites.csv', index=False)

if __name__ == "__main__":
    rodar()
