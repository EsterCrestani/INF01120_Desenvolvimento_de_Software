import pytest
from app.maestro import Maestro
import time

def test_maestro_preparacao():
    maestro = Maestro()
    maestro.preparar("[0] C D E\n[2] F G A")
    
    assert maestro.bpm == 120
    assert maestro.vozes is not None
    assert len(maestro.vozes) == 2
    assert maestro.gerador_midi is not None

def test_maestro_tocar_parar():
    maestro = Maestro()
    maestro.preparar("C")
    
    # Tocar executa em uma thread
    maestro.tocar()
    assert maestro.tocando == True
    
    # Parar altera a flag e invoca funções de áudio
    maestro.parar()
    assert maestro.tocando == False

def test_maestro_alteracao_bpm():
    maestro = Maestro()
    maestro.preparar("> > <") # Sobe 20, desce 10 = 130
    
    # Executamos o processamento de tokens manualmente para testar a lógica sem threads
    voz = maestro.vozes[0]

    while voz.partitura.has_next():
        token = voz.partitura.proximo_token()
        if token:
            token.processar(voz, maestro, {})

    assert maestro.bpm == 130
