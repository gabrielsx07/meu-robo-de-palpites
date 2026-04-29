import pandas as pd
import requests
from bs4 import BeautifulSoup

def rodar():
    # Placar do UOL: Estável, rápido e sem bloqueios chatos
    url = "https://www.uol.com.br/esporte/futebol/placar-uol/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    
    final = []
    print(f"Buscando jogos no Placar UOL...")

    try:
        response = requests.get(url, headers=headers, timeout=25)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Seleciona cada bloco de jogo
        jogos = soup.find_all('div', class_='match-card')

        for jogo in jogos:
            try:
                # 1. Campeonato/Liga
                liga_elem = jogo.select_one('.match-info__competition')
                liga = liga_elem.get_text(strip=True) if liga_elem else "Futebol"

                # 2. Horário
                hora_elem = jogo.select_one('.match-info__date')
                hora = hora_elem.get_text(strip=True) if hora_elem else "Hoje"

                # 3. Times
                casa = jogo.select_one('.team-info__name--home').get_text(strip=True)
                fora = jogo.select_one('.team-info__name--away').get_text(strip=True)

                # 4. Logos
                logos = jogo.select('.team-info__shield')
                l_casa = logos[0]['src'] if len(logos) > 0 else ""
                l_fora = logos[1]['src'] if len(logos) > 1 else ""

                # 5. Lógica de Palpites (Gerada pelo Bot)
                # Se for time grande ou conhecido, sugere vitória. Se não, Over gols.
                grandes = ['Flamengo', 'Palmeiras', 'Real Madrid', 'City', 'Barcelona', 'Bayern', 'PSG', 'Inter', 'Grêmio', 'Inter']
                if any(g in casa for g in grandes):
                    palpite = f"VENCER UM DOS TEMPOS: {casa}"
                elif any(g in fora for g in grandes):
                    palpite = f"VENCER UM DOS TEMPOS: {fora}"
                else:
                    palpite = "MAIS DE 1.5 GOLS NO JOGO"

                final.append({
                    'Hora': hora, 'Liga': liga, 'TimeCasa': casa, 
                    'LogoCasa': l_casa, 'TimeFora': fora, 
                    'LogoFora': l_fora, 'Palpite': palpite
                })
            except Exception as e:
                continue

    except Exception as e:
        print(f"Erro ao acessar: {e}")

    if final:
        df = pd.DataFrame(final).drop_duplicates()
        df.to_csv('palpites.csv', index=False)
        print(f"✅ SUCESSO: {len(df)} jogos capturados!")
    else:
        # Garante que o CSV não fique vazio para não quebrar o site
        pd.DataFrame([{'Hora': '00:00', 'Liga': 'Aviso', 'TimeCasa': 'Sem jogos', 'LogoCasa': '', 'TimeFora': 'Disponíveis', 'LogoFora': '', 'Palpite': 'AGUARDANDO ATUALIZAÇÃO'}]).to_csv('palpites.csv', index=False)
        print("⚠️ Nenhum jogo encontrado agora.")

if __name__ == "__main__":
    rodar()
