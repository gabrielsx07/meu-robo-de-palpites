import pandas as pd
import requests
from bs4 import BeautifulSoup

def gerar_analise(casa, fora):
    # Aqui entra a inteligência: times favoritos para vencer
    favoritos = ['Flamengo', 'Palmeiras', 'Real Madrid', 'Manchester City', 'Bayern', 'Barcelona', 'Liverpool', 'Arsenal', 'Inter de Milão']
    
    casa_f = casa.strip()
    fora_f = fora.strip()
    
    if any(fav in casa_f for fav in favoritos):
        return f"VENCER UM DOS TEMPOS: {casa_f}"
    elif any(fav in fora_f for fav in favoritos):
        return f"VENCER UM DOS TEMPOS: {fora_f}"
    else:
        # Se forem times parelhos, a IA sugere mercado de gols
        return "MAIS DE 1.5 GOLS NO JOGO"

def rodar():
    url = "https://www.uol.com.br/esporte/futebol/placar-uol/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    final = []
    print("Iniciando Analista IA Gorilla...")

    try:
        response = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(response.text, 'html.parser')
        jogos = soup.find_all('div', class_='match-card')

        for jogo in jogos:
            try:
                liga = jogo.select_one('.match-info__competition').get_text(strip=True)
                hora = jogo.select_one('.match-info__date').get_text(strip=True)
                casa = jogo.select_one('.team-info__name--home').get_text(strip=True)
                fora = jogo.select_one('.team-info__name--away').get_text(strip=True)
                
                # Logos
                logos = jogo.select('.team-info__shield')
                l_casa = logos[0]['src'] if len(logos) > 0 else ""
                l_fora = logos[1]['src'] if len(logos) > 1 else ""

                # A IA gera o palpite agora!
                palpite = gerar_analise(casa, fora)

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
        print(f"✅ Sucesso! {len(final)} análises de IA geradas.")

if __name__ == "__main__":
    rodar()
