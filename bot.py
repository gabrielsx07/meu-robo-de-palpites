import pandas as pd
import requests
from bs4 import BeautifulSoup
import os

def rodar():
    url = "https://apostadorpro.tech"
    # Cabeçalho para o site não bloquear o robô
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
    }
    
    final = []
    print(f"Iniciando clonagem de: {url}")

    try:
        response = requests.get(url, headers=headers, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Procura por todos os cards de jogos no site deles
        cards = soup.select('div.card') 
        
        for card in cards:
            try:
                # 1. Pega a Liga e a Hora
                header = card.select_one('.card-header')
                if not header: continue
                info = header.get_text(separator="|").split("|")
                liga = info[0].strip()
                hora = info[1].strip() if len(info) > 1 else "Hoje"

                # 2. Pega os Times
                casa = card.select_one('.home-team').get_text(strip=True)
                fora = card.select_one('.away-team').get_text(strip=True)

                # 3. Pega as Imagens (Logos)
                imgs = card.select('img')
                logo_casa = imgs[0]['src'] if len(imgs) > 0 else ""
                logo_fora = imgs[1]['src'] if len(imgs) > 1 else ""

                # 4. Pega o Palpite (A "Sugestão")
                # Eles costumam usar classes como 'tip-container' ou 'badge-success'
                sugestao = card.select_one('.tip-container, .badge, .sugestao')
                palpite = sugestao.get_text(strip=True).replace("SUGESTÃO", "").strip() if sugestao else "Análise VIP"

                final.append({
                    'Hora': hora,
                    'Liga': liga,
                    'TimeCasa': casa,
                    'LogoCasa': logo_casa,
                    'TimeFora': fora,
                    'LogoFora': logo_fora,
                    'Palpite': palpite
                })
            except Exception as e:
                continue

    except Exception as e:
        print(f"Erro ao conectar no site alvo: {e}")

    if final:
        # Salva o CSV com os dados clonados
        pd.DataFrame(final).to_csv('palpites.csv', index=False)
        print(f"✅ SUCESSO: {len(final)} palpites clonados e prontos!")
    else:
        # Se falhar, cria uma linha de erro para você saber
        pd.DataFrame([{
            'Hora': '00:00', 'Liga': 'Erro', 'TimeCasa': 'Site Alvo', 
            'LogoCasa': '', 'TimeFora': 'Mudou Layout', 'LogoFora': '', 
            'Palpite': 'Me avise no chat'
        }]).to_csv('palpites.csv', index=False)
        print("⚠️ Não encontramos cards. O site pode ter mudado as classes HTML.")

if __name__ == "__main__":
    rodar()
