import pytest

from app.voz import Voz
from app.tokens import (
    TokenOitavaUp,
    TokenOitavaDown,
    TokenVolumeUp,
    TokenVolumeDown,
    TokenInstrumentoIncremento,
    OITAVA_MAXIMA,
    OITAVA_MINIMA,
    VOLUME_MAXIMO,
    INSTRUMENTO_MAXIMO
)

# --- Fixtures e Dummies ---

@pytest.fixture
def voz_padrao():
    """Retorna uma Voz limpa (id 0) para cada teste (oitava_base=6, volume_base=100)."""
    return Voz(id_voz=0, linha_texto="")

class DummyReproducao:
    def set_instrumento_no_canal(self, instrumento, canal): pass

class DummyGeradorMIDI:
    def registrar_instrumento(self, id_voz, canal, instrumento): pass

class DummyMaestro:
    """Simula o Maestro para evitar a inicialização da placa de áudio (pygame.midi) durante os testes."""
    def __init__(self):
        self.reproducao = DummyReproducao()
        self.gerador_midi = DummyGeradorMIDI()

@pytest.fixture
def dummy_maestro():
    return DummyMaestro()

# --- Testes de Limites de Oitava ---

def test_token_oitava_up_dentro_do_limite(voz_padrao):
    """Testa se TokenOitavaUp incrementa a oitava normalmente."""
    voz_padrao.oitava_atual = 8
    token = TokenOitavaUp('?')
    
    # OitavaUp e Down não usam o maestro, podemos passar None
    token.processar(voz_padrao, None, {})
    
    assert voz_padrao.oitava_atual == 9

def test_token_oitava_up_ultrapassa_limite_retorna_base(voz_padrao):
    """Testa se ultrapassar OITAVA_MAXIMA (9) reseta a oitava para a base cíclica da voz."""
    voz_padrao.oitava_atual = OITAVA_MAXIMA
    token = TokenOitavaUp('?')
    
    token.processar(voz_padrao, None, {})
    
    # A oitava base da voz com id 0 é 6. Ao tentar subir no limite, deve voltar pra base.
    assert voz_padrao.oitava_atual == voz_padrao.oitava_base
    assert voz_padrao.oitava_atual == 6

def test_token_oitava_down_limite_minimo(voz_padrao):
    """Testa se TokenOitavaDown não permite descer abaixo de OITAVA_MINIMA (0)."""
    voz_padrao.oitava_atual = OITAVA_MINIMA
    token = TokenOitavaDown('V')
    
    token.processar(voz_padrao, None, {})
    
    assert voz_padrao.oitava_atual == OITAVA_MINIMA

# --- Testes de Limites de Volume ---

def test_token_volume_up_limite_maximo(voz_padrao):
    """Testa se aumentar o volume é travado em VOLUME_MAXIMO (100)."""
    voz_padrao.volume_atual = 95
    token = TokenVolumeUp('+')
    token.processar(voz_padrao, None, {})
    assert voz_padrao.volume_atual == VOLUME_MAXIMO

def test_token_volume_down_limite_minimo(voz_padrao):
    """Testa se diminuir o volume é travado em 0."""
    voz_padrao.volume_atual = 5
    token = TokenVolumeDown('-')
    token.processar(voz_padrao, None, {})
    assert voz_padrao.volume_atual == 0

# --- Testes de Limites de Instrumento ---

def test_token_instrumento_incremento_limite(voz_padrao, dummy_maestro):
    """Testa se incrementar o instrumento é travado em INSTRUMENTO_MAXIMO (127)."""
    voz_padrao.instrumento_atual = 120
    # Simulando que o token '8' (dígito par) foi lido, com incremento de 8.
    token = TokenInstrumentoIncremento('8', incremento=8)
    
    # Este token chama o maestro, por isso passamos o objeto mock/dummy.
    token.processar(voz_padrao, dummy_maestro, {})
    
    # 120 + 8 = 128, o que causaria erro no MIDI. Deve ser travado no limite (127).
    assert voz_padrao.instrumento_atual == INSTRUMENTO_MAXIMO
