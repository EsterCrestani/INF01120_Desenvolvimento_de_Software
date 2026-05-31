import time
import pygame.midi

class ReproducaoAudio:
    
    def __init__(self):
        self._volume: int = 64
        self._instrumento_atual: int = 0
        self._oitava_atual: int = 4
        self._output: pygame.midi.Output = None
        
        self._inicializarDispositivo()

    def __del__(self):
        try:
            if pygame.midi.get_init():
                if self._output:
                    self._output.close()
                pygame.midi.quit()
        except:
            pass 

    # ==========================================
    #             MÉTODOS PRIVADOS
    # ==========================================

    def _inicializarDispositivo(self) -> None:
        pygame.midi.init()
        porta_destino = 1 
        
        try:
            self._output = pygame.midi.Output(porta_destino)
            print(f"Sucesso: Conectado ao dispositivo de áudio ID {porta_destino}")
        except Exception as e:
            print(f"Aviso: Não foi possível conectar ao dispositivo ID {porta_destino}. Erro: {e}")

    def _validarLimite(self, valor: int, minimo: int, maximo: int) -> int:
        return max(minimo, min(valor, maximo))

    def _calcularNotaMidi(self, nota_char: str) -> int:
        mapa_notas = {
            'C': 0, 'D': 2, 'E': 4, 'F': 5, 
            'G': 7, 'A': 9, 'B': 11
        }
        
        nota_upper = nota_char.upper()
        if nota_upper not in mapa_notas:
            raise ValueError(f"Nota inválida: {nota_char}")

        nota_base = mapa_notas[nota_upper]
        nota_midi = (self._oitava_atual + 1) * 12 + nota_base
        
        return self._validarLimite(nota_midi, 0, 127)

    # ==========================================
    #             MÉTODOS PÚBLICOS
    # ==========================================

    def reproduzirNota(self, nota: str, canal: int = 0) -> None:
        if not self._output:
            return
        nota_midi = self._calcularNotaMidi(nota)
        self._output.note_on(nota_midi, self._volume, canal)

    def executarPausa(self, ms: int) -> None:  # <-- CORRIGIDO AQUI!
        time.sleep(ms / 1000.0)

    def setVolume(self, novo_volume: int) -> None:
        self._volume = self._validarLimite(novo_volume, 0, 127)

    def setInstrumento(self, id_midi: int, canal: int = 0) -> None:
        id_valido = self._validarLimite(id_midi, 0, 127)
        self._instrumento_atual = id_valido
        if self._output:
            self._output.set_instrument(id_valido, canal)

    def setOitava(self, nova_oitava: int) -> None:
        self._oitava_atual = self._validarLimite(nova_oitava, -1, 9)

    def getVolume(self) -> int:
        return self._volume

    def getInstrumento(self) -> int:
        return self._instrumento_atual

    def pararReproducao(self) -> None:
        if not self._output:
            return
        for canal in range(16):
            self._output.write_short(0xB0 + canal, 123, 0)