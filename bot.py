import pandas as pd
import requests
from bs4 import BeautifulSoup
import time

def rodar():
    url = "https://apostadorpro.tech"
    # Headers ultra-reais para evitar o bloqueio que estás a ter
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8',
        'Referer': 'https://www.google.com/'
    }
    
    final = []
    print(f"A iniciar extração de palpites em {url}...")

    try:
        # Criamos uma sessão para manter cookies (ajuda a passar por bloqueios)
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=30)
        
        if response.status_code != 200:
            print(f"Erro de conexão: {response.status_code}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Procuramos os cards de jogos usando seletores mais flexíveis
        cards = soup.find_all('div', class_=lambda x: x and 'card' in x.lower())

        for card in cards:
            try:
                # Extração dos Times
                teams = card.find_all(class_=lambda x: x and 'team' in x.lower())
                if len(teams) < 2: continue
                
                casa = teams[0].get_text(strip=True)
                fora = teams[1].get_text(strip=True)
                
                # Extração do Palpite Original
                sug_elem = card.find(class_=lambda x: x and ('tip' in x.lower() or 'badge' in x.lower()))
                txt_original = sug_elem.get_text(strip=True).upper() if sug_elem else "OVER 1.5 GOLS"

                # --- LÓGICA DE CLAREZA (Diz quem vence) ---
                if "VENCER" in txt_original or "CASA" in txt_original or " 1 " in txt_original:
                    palpite_claro = f"VENCER UM DOS TEMPOS: {casa}"
                elif "FORA" in txt_original or " 2 " in txt_original:
                    palpite_claro = f"VENCER UM DOS TEMPOS: {fora}"
                elif "AMBAS" in txt_original:
                    palpite_claro = "AMBAS MARCAM: SIM"
                else:
                    palpite_claro = txt_original

                # Logos, Liga e Hora
                imgs = card.find_all('img')
                logo_c = imgs[0]['src'] if len(imgs) > 0 else ""
                logo_f = imgs[1]['src'] if len(imgs) > 1 else ""
                
                header = card.find(class_=lambda x: x and 'header' in x.lower())
                info = header.get_text(separator="|").split("|") if header else ["Futebol", "Hoje"]
                liga = info[0].strip()
                hora = info[1].strip() if len(info) > 1 else "Hoje"

                final.append({
                    'Hora': hora, 'Liga': liga, 'TimeCasa': casa, 
                    'LogoCasa': logo_c, 'TimeFora': fora, 
                    'LogoFora': logo_f, 'Palpite': palpite_claro
                })
            except:
                continue

    except Exception as e:
        print(f"Erro no robô: {e}")

    if final:
        # Remove duplicados e salva
        pd.DataFrame(final).drop_duplicates().to_csv('palpites.csv', index=False)
        print(f"✅ SUCESSO: {len(final)} palpites extraídos.")
    else:
        # Se falhar, avisa no CSV para não ficar em branco
        pd.DataFrame([{'Hora': '00:00', 'Liga': 'Erro', 'TimeCasa': 'Site Alvo', 'LogoCasa': '', 'TimeFora': 'Protegido', 'LogoFora': '', 'Palpite': 'Aguarde Atualização'}]).to_csv('palpites.csv', index=False)
        print("⚠️ Nenhum jogo encontrado. O site pode ter aumentado a segurança.")

if __name__ == "__main__":
    rodar()
