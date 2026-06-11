import pytest

from app.voz import Voz
from app.constantes_musicais import (
    INSTRUMENTOS_CICLICOS,
    OITAVA_TETO_CICLO,
    VOLUME_TETO_CICLO,
    CANAIS_MIDI_TOTAL
)

# --- Testes de Distribuição Cíclica ---

def test_distribuicao_ciclica_oitava():
    """Testa se a oitava base diminui de 6 a 3 e reinicia o ciclo corretamente."""
    assert Voz(id_voz=0, linha_texto="").oitava_base == 6
    assert Voz(id_voz=1, linha_texto="").oitava_base == 5
    assert Voz(id_voz=2, linha_texto="").oitava_base == 4
    assert Voz(id_voz=3, linha_texto="").oitava_base == 3
    # O id 4 deve reiniciar o ciclo de tamanho 4 (retornando ao topo)
    assert Voz(id_voz=4, linha_texto="").oitava_base == 6

def test_distribuicao_ciclica_volume():
    """Testa se o volume decresce de 20 em 20 a partir de 100 e reinicia no id 4."""
    assert Voz(id_voz=0, linha_texto="").volume_base == 100
    assert Voz(id_voz=1, linha_texto="").volume_base == 80
    assert Voz(id_voz=2, linha_texto="").volume_base == 60
    assert Voz(id_voz=3, linha_texto="").volume_base == 40
    # Reinício do ciclo
    assert Voz(id_voz=4, linha_texto="").volume_base == 100

def test_distribuicao_ciclica_instrumento():
    """Testa se os instrumentos são atribuídos com base na lista de instrumentos cíclicos."""
    assert Voz(id_voz=0, linha_texto="").instrumento_base == INSTRUMENTOS_CICLICOS[0]
    assert Voz(id_voz=1, linha_texto="").instrumento_base == INSTRUMENTOS_CICLICOS[1]
    assert Voz(id_voz=2, linha_texto="").instrumento_base == INSTRUMENTOS_CICLICOS[2]
    assert Voz(id_voz=3, linha_texto="").instrumento_base == INSTRUMENTOS_CICLICOS[3]
    # Reinício do ciclo
    assert Voz(id_voz=4, linha_texto="").instrumento_base == INSTRUMENTOS_CICLICOS[0]

def test_distribuicao_canal_midi():
    """Testa se o canal MIDI respeita o limite total de canais suportado."""
    # Canais vão de 0 a 15, reiniciando no 16
    assert Voz(id_voz=0, linha_texto="").canal == 0
    assert Voz(id_voz=15, linha_texto="").canal == 15
    assert Voz(id_voz=16, linha_texto="").canal == 0
    assert Voz(id_voz=17, linha_texto="").canal == 1

# --- Testes de Mutação de Estado ---

def test_reiniciar_estado_voz():
    """Testa se forçar alterações de estado durante a execução permite uma reinicialização limpa."""
    voz = Voz(id_voz=0, linha_texto="C D E")
    
    # 1. Arrange: Força a mutação do estado como se estivesse no meio da música
    voz.oitava_atual = 9
    voz.volume_atual = 50
    voz.instrumento_atual = 127
    voz.nota_atual = 'C'
    voz.partitura.proximo_token() # Move o cursor da partitura da posição 0 para 1
    
    # 2. Act: Executa o método de reinicialização
    voz.reiniciar_estado()
    
    # 3. Assert: Valida se todos os parâmetros voltaram para a configuração base
    assert voz.oitava_atual == voz.oitava_base
    assert voz.volume_atual == voz.volume_base
    assert voz.instrumento_atual == voz.instrumento_base
    assert voz.nota_atual is None
    assert voz.partitura.posicao == 0
