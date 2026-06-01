import time
import pygame.midi

# Constantes do Protocolo MIDI
MIDI_MIN_VAL = 0
MIDI_MAX_VAL = 127
MIDI_MIN_CHANNEL = 0
MIDI_MAX_CHANNEL = 15
MIDI_TOTAL_CHANNELS = 16
MIDI_CONTROL_CHANGE_BASE = 0xB0
MIDI_ALL_NOTES_OFF = 123

# Constantes de Teoria Musical
SEMITONS_POR_OITAVA = 12
MS_EM_UM_SEGUNDO = 1000.0

class ReproducaoAudio:

    def __init__(self):
        self._output: pygame.midi.Output | None = None
        self._inicializar_dispositivo()

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

    def _inicializar_dispositivo(self) -> None:
        if not pygame.midi.get_init():
            pygame.midi.init()
        porta_destino = pygame.midi.get_default_output_id()

        try:
            self._output = pygame.midi.Output(porta_destino)
        except Exception:
            pass  # falha silenciosa; notas simplesmente nao soam

    def _validar_limite(self, valor: int, minimo: int, maximo: int) -> int:
        return max(minimo, min(valor, maximo))

    def _calcular_nota_midi(self, nota_char: str, oitava: int) -> int:
        mapa_notas = {
            'C': 0, 'D': 2, 'E': 4, 'F': 5,
            'G': 7, 'A': 9, 'B': 11, 'H': 10, 'MB': 3
        }

        nota_upper = nota_char.upper()
        if nota_upper not in mapa_notas:
            raise ValueError(f"Nota inválida: {nota_char}")

        nota_base = mapa_notas[nota_upper]
        nota_midi = (oitava + 1) * SEMITONS_POR_OITAVA + nota_base

        return self._validar_limite(nota_midi, MIDI_MIN_VAL, MIDI_MAX_VAL)

    # ==========================================
    #             MÉTODOS PÚBLICOS
    # ==========================================

    def reproduzir_nota(self, nota: str, oitava: int, volume: int, canal: int) -> None:
        if not self._output:
            return
        try:
            nota_midi = self._calcular_nota_midi(nota, oitava)
            volume_seguro = self._validar_limite(volume, MIDI_MIN_VAL, MIDI_MAX_VAL)
            canal_seguro = self._validar_limite(canal, MIDI_MIN_CHANNEL, MIDI_MAX_CHANNEL)
            self._output.note_on(nota_midi, volume_seguro, canal_seguro)
        except ValueError:
            pass # Ignora notas inválidas silenciosamente

    def silenciar_nota(self, nota: str, oitava: int, canal: int) -> None:
        if not self._output:
            return
        try:
            nota_midi = self._calcular_nota_midi(nota, oitava)
            canal_seguro = self._validar_limite(canal, MIDI_MIN_CHANNEL, MIDI_MAX_CHANNEL)
            self._output.note_off(nota_midi, MIDI_MIN_VAL, canal_seguro)
        except ValueError:
            pass

    def executar_pausa(self, ms: int) -> None:
        time.sleep(ms / MS_EM_UM_SEGUNDO)

    def set_instrumento_no_canal(self, id_midi: int, canal: int) -> None:
        id_valido = self._validar_limite(id_midi, MIDI_MIN_VAL, MIDI_MAX_VAL)
        canal_seguro = self._validar_limite(canal, MIDI_MIN_CHANNEL, MIDI_MAX_CHANNEL)
        if self._output:
            self._output.set_instrument(id_valido, canal_seguro)

    def parar_reproducao(self) -> None:
        if not self._output:
            return
        for canal in range(MIDI_TOTAL_CHANNELS):
            self._output.write_short(MIDI_CONTROL_CHANGE_BASE + canal, MIDI_ALL_NOTES_OFF, 0) # All Notes Off
