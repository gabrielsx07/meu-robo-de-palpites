import pandas as pd
import os

def gerar_palpites():
    # Simulando a captura de dados (Aqui você pode integrar seu OCR depois)
    dados = [
        {
            "TimeCasa": "Real Madrid", 
            "TimeFora": "Barcelona", 
            "OddCasa": "2.10", 
            "OddFora": "3.45", 
            "xG": "2.1 vs 1.2",
            "Entrada": "Vitória Casa", 
            "Assertividade": 88
        },
        {
            "TimeCasa": "Manchester City", 
            "TimeFora": "Arsenal", 
            "OddCasa": "1.85", 
            "OddFora": "4.20", 
            "xG": "2.8 vs 1.1",
            "Entrada": "Over 2.5 Gols", 
            "Assertividade": 94
        },
        {
            "TimeCasa": "Bayern", 
            "TimeFora": "Dortmund", 
            "OddCasa": "1.65", 
            "OddFora": "5.10", 
            "xG": "2.4 vs 0.9",
            "Entrada": "Ambas Marcam", 
            "Assertividade": 82
        }
    ]
    
    # Gera o arquivo CSV que o site vai ler
    df = pd.DataFrame(dados)
    df.to_csv('palpites.csv', index=False)
    print("✅ Sucesso: O arquivo palpites.csv foi atualizado!")

if __name__ == "__main__":
    gerar_palpites()
