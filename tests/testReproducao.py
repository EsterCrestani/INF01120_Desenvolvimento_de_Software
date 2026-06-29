from app.reproducao_audio import ReproducaoAudio

def rodar_testes():
    print("Iniciando testes do Módulo de Áudio...\n")

    try:
        # Cria a classe uma única vez
        audio = ReproducaoAudio()

        print("[Teste 1] Tocando escala (Dó, Ré, Mi, Fá, Sol) no Piano (canal 0)...")
        escala = ['C', 'D', 'E', 'F', 'G']
        audio.set_instrumento_no_canal(0, 0) # Piano (0) no canal 0
        for nota in escala:
            audio.reproduzir_nota(nota, 4, 100, 0)
            audio.executar_pausa(400)
            audio.silenciar_nota(nota, 4, 0)

        print("\n[Teste 2] Mudando para Órgão de Tubos (Instrumento 19) no canal 0 e oitava mais grave...")
        audio.set_instrumento_no_canal(19, 0) # Church Organ (19) no canal 0

        for nota in escala:
            audio.reproduzir_nota(nota, 3, 100, 0)
            audio.executar_pausa(400)
            audio.silenciar_nota(nota, 3, 0)

        print("\n[Teste 3] Acorde de piano e parada abrupta...")
        audio.set_instrumento_no_canal(0, 0)

        audio.reproduzir_nota('C', 4, 100, 0)
        audio.executar_pausa(500)

        audio.reproduzir_nota('G', 4, 100, 0)
        print("Cortando o som no meio da nota!")
        audio.parar_reproducao()
        audio.executar_pausa(1000)

        print("\nTodos os testes executados com sucesso!")

    except Exception as erro:
        print(f"\nOcorreu um erro durante a execução: {erro}")

if __name__ == "__main__":
    rodar_testes()
