import pytest

from app.gerador_midi import GeradorMIDI, MIDI_MAX_VAL, MIDI_MIN_VAL

@pytest.fixture
def gerador():
    """Fornece uma instância limpa do GeradorMIDI para os testes."""
    return GeradorMIDI()

# --- Testes de Cálculo Matemático da Nota MIDI ---

def test_calcular_nota_midi_doh_central(gerador):
    """Testa o cálculo para o Dó central (C4). Fórmula: (4+1)*12 + 0 = 60."""
    nota = gerador._calcular_nota_midi('C', 4)
    assert nota == 60

def test_calcular_nota_midi_la_padrao(gerador):
    """Testa o cálculo para o Lá (A4 - 440Hz). Fórmula: (4+1)*12 + 9 = 69."""
    nota = gerador._calcular_nota_midi('A', 4)
    assert nota == 69

def test_calcular_nota_midi_case_insensitive(gerador):
    """Testa se o cálculo ignora diferenças entre letras maiúsculas e minúsculas."""
    nota_maiuscula = gerador._calcular_nota_midi('E', 3)
    nota_minuscula = gerador._calcular_nota_midi('e', 3)
    assert nota_maiuscula == nota_minuscula
    assert nota_maiuscula == 52 # (3+1)*12 + 4

def test_calcular_nota_especial_mb(gerador):
    """Testa se o token duplo 'Mb' é calculado corretamente independente da capitalização."""
    assert gerador._calcular_nota_midi('Mb', 5) == 75 # (5+1)*12 + 3
    assert gerador._calcular_nota_midi('mb', 5) == 75
    assert gerador._calcular_nota_midi('MB', 5) == 75

def test_calcular_nota_invalida_retorna_erro(gerador):
    """Testa se passar um caractere que não é nota retorna -1."""
    assert gerador._calcular_nota_midi('X', 4) == -1
    assert gerador._calcular_nota_midi('Z', 4) == -1
    assert gerador._calcular_nota_midi('!', 4) == -1

def test_calcular_nota_limites_seguranca(gerador):
    """Testa se o cálculo restringe o resultado final entre 0 e 127 (Protocolo MIDI)."""
    # Forçando uma oitava absurdamente alta (ex: oitava 20)
    nota_alta = gerador._calcular_nota_midi('B', 20)
    assert nota_alta == MIDI_MAX_VAL # Deve ser "clampado" (travado) em 127
    
    # Forçando uma oitava negativa absurda
    nota_baixa = gerador._calcular_nota_midi('C', -5)
    assert nota_baixa == MIDI_MIN_VAL # Deve ser travado em 0
