from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.voz import Voz
    from app.maestro import Maestro

# Constantes de Execução de Token
DURACAO_BEAT_PADRAO = 1.0

# Limites de Oitava e Volume (aplicados na mutação de estado da voz)
OITAVA_MAXIMA = 9
OITAVA_MINIMA = 0
VOLUME_MAXIMO = 127
INSTRUMENTO_MAXIMO = 127  # programa MIDI máximo (0-127)

# Ajuste de Andamento (BPM)
BPM_AJUSTE = 10
BPM_MINIMO = 10


class Token(ABC):
    """
    Interface base para os tokens. Cada subtipo encapsula toda a sua lógica de
    execução em processar(): muta o estado musical (voz/maestro) e dispara os
    efeitos colaterais (áudio e MIDI).
    """
    tipo: str = 'UNKNOWN'
    # Indica se o token consome um beat inteiro da execução (nota/pausa) ou se é
    # apenas um controle instantâneo (instrumento, oitava, BPM, volume...).
    ocupa_beat: bool = False

    def __init__(self, char: str):
        self.char = char

    @abstractmethod
    def processar(self, voz: 'Voz', maestro: 'Maestro', notas_tocando: dict):
        ...


class TokenNota(Token):
    tipo = 'NOTA'
    ocupa_beat = True

    def processar(self, voz: Voz, maestro: Maestro, notas_tocando: dict):
        nota = self.char
        voz.nota_atual = nota
        maestro.reproducao.reproduzir_nota(nota, voz.oitava_atual, voz.volume_atual, voz.canal)
        maestro.gerador_midi.registrar_nota(voz.id_voz, voz.canal, nota, voz.oitava_atual, voz.volume_atual, DURACAO_BEAT_PADRAO)
        notas_tocando[voz.id_voz] = (nota, voz.oitava_atual, voz.canal)


class TokenPausa(Token):
    tipo = 'PAUSA'
    ocupa_beat = True

    def processar(self, voz: Voz, maestro: Maestro, notas_tocando: dict):
        maestro.gerador_midi.registrar_pausa(voz.id_voz, DURACAO_BEAT_PADRAO)


class TokenInstrumento(Token):
    tipo = 'INSTRUMENTO'

    def __init__(self, char: str, valor: int):
        super().__init__(char)
        self.valor = valor

    def processar(self, voz: Voz, maestro: Maestro, notas_tocando: dict):
        voz.instrumento_atual = self.valor
        maestro.reproducao.set_instrumento_no_canal(voz.instrumento_atual, voz.canal)
        maestro.gerador_midi.registrar_instrumento(voz.id_voz, voz.canal, voz.instrumento_atual)


class TokenInstrumentoIncremento(Token):
    """Soma um valor ao instrumento atual da voz (usado por dígitos pares)."""
    tipo = 'INSTRUMENTO'

    def __init__(self, char: str, incremento: int):
        super().__init__(char)
        self.incremento = incremento

    def processar(self, voz: Voz, maestro: Maestro, notas_tocando: dict):
        voz.instrumento_atual = min(voz.instrumento_atual + self.incremento, INSTRUMENTO_MAXIMO)
        maestro.reproducao.set_instrumento_no_canal(voz.instrumento_atual, voz.canal)
        maestro.gerador_midi.registrar_instrumento(voz.id_voz, voz.canal, voz.instrumento_atual)


class TokenOitavaUp(Token):
    tipo = 'OITAVA_UP'

    def processar(self, voz: Voz, maestro: Maestro, notas_tocando: dict):
        # Sobe uma oitava; se já está no máximo, volta para a oitava base da voz.
        if voz.oitava_atual >= OITAVA_MAXIMA:
            voz.oitava_atual = voz.oitava_base
        else:
            voz.oitava_atual += 1


class TokenOitavaDown(Token):
    tipo = 'OITAVA_DOWN'

    def processar(self, voz: Voz, maestro: Maestro, notas_tocando: dict):
        voz.oitava_atual = max(voz.oitava_atual - 1, OITAVA_MINIMA)


class TokenVolumeUp(Token):
    tipo = 'VOLUME_UP'

    def processar(self, voz: Voz, maestro: Maestro, notas_tocando: dict):
        voz.volume_atual = min(voz.volume_atual + 10, VOLUME_MAXIMO)


class TokenVolumeDown(Token):
    tipo = 'VOLUME_DOWN'

    def processar(self, voz: Voz, maestro: Maestro, notas_tocando: dict):
        voz.volume_atual = max(voz.volume_atual - 10, 0)


class TokenBpmUp(Token):
    tipo = 'BPM_UP'

    def processar(self, voz: Voz, maestro: Maestro, notas_tocando: dict):
        maestro.bpm += BPM_AJUSTE
        maestro.gerador_midi.alterar_bpm(maestro.bpm)


class TokenBpmDown(Token):
    tipo = 'BPM_DOWN'

    def processar(self, voz: Voz, maestro: Maestro, notas_tocando: dict):
        maestro.bpm = max(BPM_MINIMO, maestro.bpm - BPM_AJUSTE)
        maestro.gerador_midi.alterar_bpm(maestro.bpm)


class TokenIgnore(Token):
    tipo = 'IGNORE'

    def processar(self, voz: Voz, maestro: Maestro, notas_tocando: dict):
        pass
