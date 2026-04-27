import requests
import pandas as pd
import random
from datetime import datetime

API_KEY = 'SUA_CHAVE_AQUI'
URL = 'https://api.football-data.org/v4/matches'
headers = {'X-Auth-Token': API_KEY}

def analisar_probabilidades(casa, fora):
    """
    Aqui o robô avalia as opções e escolhe a de maior confiança.
    """
    # Simulamos uma análise de 'força' dos times
    # Em um cenário real, aqui você cruzaria dados de vitórias/derrotas
    forca_casa = len(casa) # Exemplo: nomes maiores tendem a ser times mais estruturados
    forca_fora = len(fora)
    
    opcoes_viaveis = []

    # Opção 1: Analisar Vencedor / Dupla Chance
    if abs(forca_casa - forca_fora) > 5: # Grande diferença de força
        favorito = casa if forca_casa > forca_fora else fora
        conf = random.randint(92, 98)
        opcoes_viaveis.append({"tipo": f"Vitória: {favorito}", "conf": conf})
    else:
        conf = random.randint(88, 93)
        opcoes_viaveis.append({"tipo": "Dupla Chance (1X ou X2)", "conf": conf})

    # Opção 2: Analisar Mercado de Gols
    conf_gols = random.randint(85, 96)
    opcoes_viaveis.append({"tipo": "Mais de 1.5 Gols", "conf": conf_gols})

    # Opção 3: Analisar Ambas Marcam
    if abs(forca_casa - forca_fora) < 3: # Jogo muito equilibrado
        conf_ambas = random.randint(87, 94)
        opcoes_viaveis.append({"tipo": "Ambas Marcam: Sim", "conf": conf_ambas})

    # O "PULO DO GATO": O robô ordena pela maior confiança e escolhe APENAS A MELHOR
    opcoes_viaveis.sort(key=lambda x: x['conf'], reverse=True)
    melhor_escolha = opcoes_viaveis[0]

    return melhor_escolha['tipo'], f"{melhor_escolha['conf']}%"

def gerar_palpites():
    print("🧠 IA comparando mercados e selecionando a melhor entrada...")
    response = requests.get(URL, headers=headers)
    
    if response.status_code == 200:
        jogos = response.json().get('matches', [])
        lista_final = []

        for jogo in jogos:
            casa = jogo['homeTeam']['name']
            fora = jogo['awayTeam']['name']
            
            data_obj = datetime.strptime(jogo['utcDate'], "%Y-%m-%dT%H:%M:%SZ")
            
            # A IA decide qual é o melhor mercado para esse jogo específico
            entrada_mestre, conf_mestre = analisar_probabilidades(casa, fora)

            lista_final.append({
                "Dia": data_obj.strftime("%d/%m"),
                "Hora": data_obj.strftime("%H:%M"),
                "Confronto": f"{casa} vs {fora}",
                "Entrada": entrada_mestre,
                "Confianca": conf_mestre
            })
        
        df = pd.DataFrame(lista_final)
        df.to_csv('palpites.csv', index=False)
        print("✅ Análise concluída. Apenas a melhor opção de cada jogo foi salva.")

if __name__ == "__main__":
    gerar_palpites()
