import pandas as pd
import requests
from bs4 import BeautifulSoup

def rodar():
    # Usando a agenda do GE que é aberta e fácil de ler
    url = "https://ge.globo.com/agenda-do-dia/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    final = []
    print(f"Buscando jogos em: {url}")

    try:
        response = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # O GE organiza os jogos por blocos de evento
        eventos = soup.select('.agenda-item')

        for evento in eventos:
            try:
                # Filtrar apenas futebol
                esporte = evento.select_one('.agenda-item__meta').get_text(strip=True)
                if 'Futebol' not in esporte: continue

                # Times e Hora
                casa = evento.select_one('.agenda-item__equipe--mandante').get_text(strip=True)
                fora = evento.select_one('.agenda-item__equipe--visitante').get_text(strip=True)
                hora = evento.select_one('.agenda-item__horario').get_text(strip=True)
                liga = evento.select_one('.agenda-item__campeonato').get_text(strip=True)

                # Logos (GE usa tags de imagem com src)
                imgs = evento.select('.agenda-item__escudo')
                l_casa = imgs[0]['src'] if len(imgs) > 0 else ""
                l_fora = imgs[1]['src'] if len(imgs) > 1 else ""

                # GERADOR DE PALPITE (Como é site de notícia, nós criamos a "Tip")
                # Aqui você pode personalizar a lógica
                palpite = f"Vencer um dos Tempos: {casa}" if "Flamengo" in casa or "Palmeiras" in casa else "Mais de 1.5 Gols"

                final.append({
                    'Hora': hora, 'Liga': liga, 'TimeCasa': casa, 
                    'LogoCasa': l_casa, 'TimeFora': fora, 
                    'LogoFora': l_fora, 'Palpite': palpite
                })
            except: continue

    except Exception as e:
        print(f"Erro: {e}")

    if final:
        pd.DataFrame(final).to_csv('palpites.csv', index=False)
        print(f"✅ {len(final)} jogos encontrados e processados!")
    else:
        print("⚠️ Nenhum jogo de futebol encontrado na agenda hoje.")

if __name__ == "__main__":
    rodar()
