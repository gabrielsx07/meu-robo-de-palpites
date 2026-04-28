import pandas as pd
import requests
from bs4 import BeautifulSoup

def rodar():
    url = "https://apostadorpro.tech"
    # Faz o robô fingir que é um navegador comum
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    final = []
    print(f"Clonando palpites de: {url}")

    try:
        response = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(response.text, 'html.parser')

        # No site deles, cada jogo fica dentro de uma 'div' com uma classe específica
        # Aqui o robô procura todos os blocos de jogos
        jogos = soup.find_all('div', class_='card-body') 

        for jogo in jogos:
            try:
                # O robô "caça" os nomes dentro do código do site deles
                casa = jogo.find('div', class_='home-team-name').get_text(strip=True)
                fora = jogo.find('div', class_='away-team-name').get_text(strip=True)
                palpite = jogo.find('div', class_='tip-text').get_text(strip=True)
                
                # Pega as imagens dos times
                fotos = jogo.find_all('img')
                l_casa = fotos[0]['src'] if len(fotos) > 0 else ""
                l_fora = fotos[1]['src'] if len(fotos) > 1 else ""

                final.append({
                    'Hora': 'Ao Vivo/Hoje',
                    'Liga': 'Análise Pro',
                    'TimeCasa': casa,
                    'LogoCasa': l_casa,
                    'TimeFora': fora,
                    'LogoFora': l_fora,
                    'Palpite': palpite
                })
            except:
                continue

    except Exception as e:
        print(f"Erro: {e}")

    if final:
        pd.DataFrame(final).to_csv('palpites.csv', index=False)
        print(f"✅ Sucesso! {len(final)} palpites clonados.")
    else:
        print("⚠️ Não achei palpites. O site deles pode ter mudado o código.")

if __name__ == "__main__":
    rodar()
