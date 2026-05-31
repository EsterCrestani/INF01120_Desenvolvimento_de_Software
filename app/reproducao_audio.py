import time
import pygame.midi

class ReproducaoAudio:
    
    def __init__(self):
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
        if not pygame.midi.get_init():
            pygame.midi.init()
        porta_destino = pygame.midi.get_default_output_id()
        
        try:
            self._output = pygame.midi.Output(porta_destino)
            print(f"Sucesso: Conectado ao dispositivo de áudio ID {porta_destino}")
        except Exception as e:
            print(f"Aviso: Não foi possível conectar ao dispositivo ID {porta_destino}. Erro: {e}")

    def _validarLimite(self, valor: int, minimo: int, maximo: int) -> int:
        return max(minimo, min(valor, maximo))

    def _calcularNotaMidi(self, nota_char: str, oitava: int) -> int:
        mapa_notas = {
            'C': 0, 'D': 2, 'E': 4, 'F': 5, 
            'G': 7, 'A': 9, 'B': 11, 'H': 10, 'MB': 3
        }
        
        nota_upper = nota_char.upper()
        if nota_upper not in mapa_notas:
            raise ValueError(f"Nota inválida: {nota_char}")

        nota_base = mapa_notas[nota_upper]
        nota_midi = (oitava + 1) * 12 + nota_base
        
        return self._validarLimite(nota_midi, 0, 127)

    # ==========================================
    #             MÉTODOS PÚBLICOS
    # ==========================================

    def reproduzirNota(self, nota: str, oitava: int, volume: int, canal: int) -> None:
        if not self._output:
            return
        try:
            nota_midi = self._calcularNotaMidi(nota, oitava)
            volume_seguro = self._validarLimite(volume, 0, 127)
            canal_seguro = self._validarLimite(canal, 0, 15)
            self._output.note_on(nota_midi, volume_seguro, canal_seguro)
        except ValueError:
            pass # Ignora notas inválidas silenciosamente
            
    def silenciarNota(self, nota: str, oitava: int, canal: int) -> None:
        if not self._output:
            return
        try:
            nota_midi = self._calcularNotaMidi(nota, oitava)
            canal_seguro = self._validarLimite(canal, 0, 15)
            self._output.note_off(nota_midi, 0, canal_seguro)
        except ValueError:
            pass

    def executarPausa(self, ms: int) -> None:
        time.sleep(ms / 1000.0)

    def setInstrumento(self, id_midi: int, canal: int) -> None:
        id_valido = self._validarLimite(id_midi, 0, 127)
        canal_seguro = self._validarLimite(canal, 0, 15)
        if self._output:
            self._output.set_instrument(id_valido, canal_seguro)

    def pararReproducao(self) -> None:
        if not self._output:
            return
        for canal in range(16):
            self._output.write_short(0xB0 + canal, 123, 0) # All Notes Off