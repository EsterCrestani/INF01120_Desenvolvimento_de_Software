from app.partitura import Partitura
from app.constantes_musicais import (
    OITAVA_TETO_CICLO,
    OITAVA_MIN_BASE_CICLO,
    TAMANHO_CICLO_VOZ,
    VOLUME_TETO_CICLO,
    VOLUME_DECREMENTO_CICLO,
    CANAIS_MIDI_TOTAL,
    INSTRUMENTOS_CICLICOS,
)


class Voz:
    """
    Agrega a configuração de uma voz (oitava, volume, instrumento, canal e
    atraso inicial) e possui uma Partitura com a sequência de tokens.

    A configuração base é derivada ciclicamente do id_voz. A linha completa é
    entregue à Partitura, que apenas a tokeniza — inclusive o `!;,` inicial (vira
    TokenInstrumento) e o atraso `[n]` (vira tokens de pausa). A Voz não interpreta
    o prefixo: guarda só as configurações cíclicas.
    """

    def __init__(self, id_voz: int, linha_texto: str):
        self.id_voz = id_voz

        # Oitavas: V0=6, V1=5, V2=4, V3=3, V4=6, ...
        self.oitava_base = OITAVA_TETO_CICLO - (id_voz % TAMANHO_CICLO_VOZ)
        if self.oitava_base < OITAVA_MIN_BASE_CICLO:
            self.oitava_base = OITAVA_TETO_CICLO  # default seguro (6, 5, 4, 3 está correto)

        # Volume: V0=100, V1=80, V2=60, V3=40
        self.volume_base = max(VOLUME_TETO_CICLO - (id_voz % TAMANHO_CICLO_VOZ) * VOLUME_DECREMENTO_CICLO, 0)

        # Instrumentos: V0=Piano(0), V1=Organ(20), V2=Harpsichord(6), V3=Bassoon(70)
        self.instrumento_base = INSTRUMENTOS_CICLICOS[id_voz % TAMANHO_CICLO_VOZ]

        self.canal = id_voz % CANAIS_MIDI_TOTAL  # MIDI suporta canais de 0 a 15

        # A Partitura apenas tokeniza a linha (incluindo `!;,` inicial e `[n]`).
        self.partitura = Partitura(linha_texto)
        self.nota_atual: str | None = None

        # Varre os tokens iniciais (antes da primeira nota ou pausa) 
        # para extrair as configurações base especificadas no texto
        for token in self.partitura.tokens:
            if token.ocupa_beat:
                break
            if token.tipo == 'INSTRUMENTO':
                if hasattr(token, 'valor'):
                    self.instrumento_base = token.valor
                elif hasattr(token, 'incremento'):
                    self.instrumento_base = min(self.instrumento_base + token.incremento, 127)
            elif token.tipo == 'OITAVA_UP':
                if self.oitava_base >= 9:
                    pass  # Não cicla a base inicial de forma ruidosa
                else:
                    self.oitava_base += 1
            elif token.tipo == 'OITAVA_DOWN':
                self.oitava_base = max(self.oitava_base - 1, 0)
            elif token.tipo == 'VOLUME_UP':
                self.volume_base = min(self.volume_base + 10, 100)
            elif token.tipo == 'VOLUME_DOWN':
                self.volume_base = max(self.volume_base - 10, 0)

        self.reiniciar_estado()


    def reiniciar_estado(self):
        self.oitava_atual = self.oitava_base
        self.volume_atual = self.volume_base
        self.instrumento_atual = self.instrumento_base
        self.nota_atual = None
        self.partitura.reiniciar()


    def preparar_para_tocar(self, reproducao, gerador_midi):
        """
        Reinicia o estado da voz e registra seu instrumento inicial nas saídas
        de áudio e MIDI, deixando-a pronta para ser executada pelo Maestro.
        """
        self.reiniciar_estado()
        reproducao.set_instrumento_no_canal(self.instrumento_atual, self.canal)
        gerador_midi.registrar_instrumento(self.id_voz, self.canal, self.instrumento_atual)


    def has_next(self) -> bool:
        return self.partitura.has_next()
