import pytest

from app.partitura import Partitura, CHAR_ATRASO
from app.tokens import (
    TokenNota,
    TokenPausa,
    TokenInstrumento,
    TokenInstrumentoIncremento,
    TokenVolumeDouble
)
from app.constantes_musicais import INSTRUMENTO_TUBULAR_BELLS

# --- Testes de Navegação (Cursor) ---

def test_partitura_navegacao_cursor():
    """Testa se os métodos has_next, proximo_token e reiniciar funcionam corretamente."""
    # Utilizando "CDE" sem espaços para gerar exatamente 3 tokens (TokenNota)
    partitura = Partitura("CDE") 
    
    assert partitura.has_next() is True
    
    token_1 = partitura.proximo_token()
    token_2 = partitura.proximo_token()
    token_3 = partitura.proximo_token()
    
    assert token_1 is not None
    assert partitura.has_next() is False
    assert partitura.proximo_token() is None
    
    partitura.reiniciar()
    assert partitura.has_next() is True
    assert partitura.posicao == 0

# --- Testes do Lexer (_tokenizar e _classificar) ---

def test_tokenizar_atraso_valido():
    """Testa a geração de N pausas ao utilizar a sintaxe de atraso [n]."""
    partitura = Partitura("[3]")
    tokens = partitura.tokens
    
    assert len(tokens) == 3
    for token in tokens:
        assert isinstance(token, TokenPausa)
        assert token.char == CHAR_ATRASO

def test_tokenizar_atraso_invalido():
    """Testa o fallback para processamento normal se a sintaxe de atraso falhar."""
    partitura_sem_fechamento = Partitura("[a")
    partitura_com_letras = Partitura("[abc]")
    
    assert len(partitura_sem_fechamento.tokens) > 0
    assert len(partitura_com_letras.tokens) > 0

def test_classificacao_digitos_par_e_impar():
    """Testa a regra de instrumentos baseada em dígitos pares e ímpares."""
    # A string "23" não possui espaços para facilitar a extração dos índices
    partitura = Partitura("23")
    tokens = partitura.tokens
    
    assert isinstance(tokens[0], TokenInstrumentoIncremento)
    assert tokens[0].char == '2'
    assert tokens[0].incremento == 2
    
    assert isinstance(tokens[1], TokenInstrumento)
    assert tokens[1].char == '3'
    assert tokens[1].valor == INSTRUMENTO_TUBULAR_BELLS

def test_regra_repeticao_nota_anterior():
    """Testa se uma consoante/vogal repete a última nota tocada."""
    partitura = Partitura("AK")
    tokens = partitura.tokens
    
    assert isinstance(tokens[0], TokenNota)
    assert tokens[0].char == 'A'
    
    assert isinstance(tokens[1], TokenNota)
    assert tokens[1].char == 'A'

def test_repeticao_sem_nota_anterior_gera_pausa():
    """Testa se um caractere de repetição no início da string gera pausa."""
    partitura = Partitura("K")
    tokens = partitura.tokens
    
    assert isinstance(tokens[0], TokenPausa)
    assert tokens[0].char == 'K'

def test_token_duplo_mb():
    """Testa se os caracteres 'M' e 'b' adjacentes são lidos como um único token de nota."""
    partitura = Partitura("Mb")
    tokens = partitura.tokens
    
    assert len(tokens) == 1
    assert isinstance(tokens[0], TokenNota)
    assert tokens[0].char == 'Mb'

def test_token_espaco_dobra_volume():
    """Testa se o caractere de espaço é processado como controle de volume."""
    partitura = Partitura(" ")
    tokens = partitura.tokens

    assert len(tokens) == 1
    assert isinstance(tokens[0], TokenVolumeDouble)
    assert tokens[0].char == ' '
