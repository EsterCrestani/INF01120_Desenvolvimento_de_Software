import pytest
from app.voz import Voz
from app.partitura import Partitura
from app.maestro import Maestro
import os

def test_voz_inicializacao():
    voz = Voz(0, "[4] C D E F")
    assert voz.oitava_base == 6
    assert voz.volume_base == 100
    assert voz.instrumento_base == 0
    # O atraso [4] vira 4 tokens de pausa no início da partitura
    assert [t.tipo for t in voz.partitura.tokens[:4]] == ['PAUSA'] * 4

    voz2 = Voz(1, "G A B")
    assert voz2.oitava_base == 5
    assert voz2.volume_base == 80
    assert voz2.instrumento_base == 20
    # Sem atraso: a partitura começa direto na nota
    assert voz2.partitura.tokens[0].tipo == 'NOTA'

def test_voz_tokenizacao():
    voz = Voz(0, "CMb!")
    tokens = voz.partitura.tokens

    assert len(tokens) == 3
    assert tokens[0].char == 'C'
    assert tokens[1].char == 'Mb'
    assert tokens[2].tipo == 'INSTRUMENTO'

def test_partitura_tokeniza_linha():
    partitura = Partitura("CMb!")
    tokens = partitura.tokens
    assert len(tokens) == 3
    assert [t.tipo for t in tokens] == ['NOTA', 'NOTA', 'INSTRUMENTO']

    # O cursor de leitura consome os tokens em ordem e pode ser reiniciado
    assert partitura.has_next()
    assert partitura.proximo_token().char == 'C'
    partitura.reiniciar()
    assert partitura.posicao == 0

def test_maestro_divide_vozes():
    maestro = Maestro()
    maestro.preparar("[0] C D E F\n[4] G A B C")
    vozes = maestro.vozes
    assert len(vozes) == 2
    assert vozes[0].partitura.tokens[0].tipo != 'PAUSA'           # [0] -> sem pausas
    assert [t.tipo for t in vozes[1].partitura.tokens[:4]] == ['PAUSA'] * 4  # [4]

def test_gerador_midi(tmp_path):
    maestro = Maestro()
    texto = "[0] C D\n[2] E F"
    maestro.preparar(texto)

    arquivo_teste = tmp_path / "teste.mid"

    # Executar a lógica de tocar sem rodar o sleep longo
    # para não travar o teste
    maestro.bpm = 6000 # Super rápido para o teste
    maestro.tocar()

    # Esperar a thread terminar
    import time
    time.sleep(0.5) # aguarda um pouco para o loop finalizar na thread

    maestro.gerador_midi.salvar(str(arquivo_teste))
    assert os.path.exists(str(arquivo_teste))
    assert os.path.getsize(str(arquivo_teste)) > 0
