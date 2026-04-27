import pandas as pd

def gerar_dados():
    # Simulando a coleta de dados (pode ser trocado por OCR depois)
    jogos = [
        {
            "TimeCasa": "Real Madrid", 
            "TimeFora": "Barcelona", 
            "OddCasa": "1.98", 
            "OddFora": "3.75", 
            "xG": "2.1 vs 1.4",
            "Entrada": "Vitória Real Madrid", 
            "Assertividade": 88
        },
        {
            "TimeCasa": "Manchester City", 
            "TimeFora": "Arsenal", 
            "OddCasa": "1.80", 
            "OddFora": "4.20", 
            "xG": "2.5 vs 1.1",
            "Entrada": "Over 2.5 Gols", 
            "Assertividade": 94
        }
    ]
    
    df = pd.DataFrame(jogos)
    df.to_csv('palpites.csv', index=False)
    print("✅ Planilha 'palpites.csv' gerada com sucesso!")

if __name__ == "__main__":
    gerar_dados()
