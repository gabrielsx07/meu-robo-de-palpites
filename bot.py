import pandas as pd
import requests
from bs4 import BeautifulSoup
import os

def rodar():
    url = "https://apostadorpro.tech"
    # Cabeçalho completo para parecer um navegador real e não ser bloqueado
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
    }
    
    final = []
    print(f"Tentando capturar palpites de: {url}")

    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code != 200:
            print(f"Erro de acesso: Status {response.status_code}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Procura os cards. Eles usam classes que contém 'Card'
        cards = soup.find_all('div', class_=lambda x: x and 'card' in x.lower())

        for card in cards:
            try:
                # Localizando os times
                # Tentamos pegar pelas classes específicas que eles usam
                home_team = card.find(class_=lambda x: x and 'homeTeam' in x)
                away_team = card.find(class_=lambda x: x and 'awayTeam' in x)
                
                if not home_team or not away_team:
                    # Tenta busca genérica se a específica falhar
                    teams = card.find_all('p', class_=lambda x: x and 'team' in x.lower())
                    if len(teams) >= 2:
                        casa = teams[0].get_text(strip=True)
                        fora = teams[1].get_text(strip=True)
                    else:
                        continue
                else:
                    casa = home_team.get_text(strip=True)
                    fora = away_team.get_text(strip=True)

                # Localizando o Palpite (Tip)
                tip_elem = card.find(class_=lambda x: x and 'tip' in x.lower())
                palpite = tip_elem.get_text(strip=True).upper() if tip_elem else "OVER 1.5 GOLS"

                # Localizando Logos e Infos
                imgs = card.find_all('img')
                l_casa = imgs[0]['src'] if len(imgs) > 0 else ""
                l_fora = imgs[1]['src'] if len(imgs) > 1 else ""
                
                # Liga e Hora (buscando no header do card)
                header = card.find(class_=lambda x: x and 'header' in x.lower())
                info_txt = header.get_text(separator="|").split("|") if header else ["Futebol", "Hoje"]
                liga = info_txt[0].strip()
                hora = info_txt[1].strip() if len(info_txt) > 1 else "Hoje"

                final.append({
                    'Hora': hora, 'Liga': liga, 'TimeCasa': casa, 
                    'LogoCasa': l_casa, 'TimeFora': fora, 
                    'LogoFora': l_fora, 'Palpite': palpite
                })
            except:
                continue

    except Exception as e:
        print(f"Erro na clonagem: {e}")

    if final:
        df = pd.DataFrame(final).drop_duplicates()
        df.to_csv('palpites.csv', index=False)
        print(f"✅ Sucesso! {len(df)} palpites capturados.")
    else:
        print("⚠️ Nenhum palpite encontrado. O site alvo pode estar offline ou bloqueado.")

if __name__ == "__main__":
    rodar()
