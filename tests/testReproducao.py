from app.reproducao_audio import ReproducaoAudio

def rodar_testes():
    print("Iniciando testes do Módulo de Áudio...\n")

    try:
        # Cria a classe uma única vez
        audio = ReproducaoAudio()

        # Ajusta para o volume máximo
        audio.setVolume(127)
        print(f"Volume ajustado para: {audio.getVolume()}")
        print(f"Instrumento atual: {audio.getInstrumento()}\n")

        print("[Teste 1] Tocando escala (Dó, Ré, Mi, Fá, Sol)...")
        escala = ['C', 'D', 'E', 'F', 'G']
        for nota in escala:
            audio.reproduzir_nota(nota)
            audio.executar_pausa(400)

        print("\n[Teste 2] Mudando para Órgão de Tubos (Instrumento 19) e oitava mais grave...")
        audio.set_instrumento_no_canal(19)
        audio.setOitava(3)

        for nota in escala:
            audio.reproduzir_nota(nota)
            audio.executar_pausa(400)

        print("\n[Teste 3] Acorde de piano e parada abrupta...")
        audio.set_instrumento_no_canal(0)
        audio.setOitava(4)

        audio.reproduzir_nota('C')
        audio.executar_pausa(500)

        audio.reproduzir_nota('G')
        print("Cortando o som no meio da nota!")
        audio.parar_reproducao()
        audio.executar_pausa(1000)

        print("\n✅ Todos os testes executados com sucesso!")

    except Exception as erro:
        print(f"\n❌ Ocorreu um erro durante a execução: {erro}")

if __name__ == "__main__":
    rodar_testes()
