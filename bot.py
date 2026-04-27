import pandas as pd
import os

def gerar_palpites():
    # Simulando os dados capturados pelo OCR
    dados = [
        {
            "TimeCasa": "Flamengo", 
            "TimeFora": "Palmeiras", 
            "OddCasa": "2.10", 
            "OddFora": "3.40", 
            "xG": "1.9 vs 1.2",
            "Entrada": "Vitória Casa", 
            "Assertividade": 85
        },
        {
            "TimeCasa": "Real Madrid", 
            "TimeFora": "Barcelona", 
            "OddCasa": "1.85", 
            "OddFora": "4.20", 
            "xG": "2.5 vs 1.1",
            "Entrada": "Over 2.5 Gols", 
            "Assertividade": 92
        }
    ]
    
    df = pd.DataFrame(dados)
    df.to_csv('palpites.csv', index=False)
    print("✅ Arquivo palpites.csv gerado com sucesso!")

if __name__ == "__main__":
    gerar_palpites()
