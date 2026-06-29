from typing import List

from app.constantes_musicais import (
    INSTRUMENTO_TUBULAR_BELLS,
    INSTRUMENTO_BAGPIPE,
    MAPA_INSTRUMENTO_SIMBOLO,
    NOTAS,
    PAUSAS,
)
from app.tokens import (
    Token,
    TokenNota,
    TokenPausa,
    TokenInstrumento,
    TokenInstrumentoIncremento,
    TokenOitavaUp,
    TokenOitavaDown,
    TokenVolumeUp,
    TokenVolumeDown,
    TokenIgnore,
)

# Caractere marcador usado nos tokens de pausa gerados a partir do atraso `[n]`.
CHAR_ATRASO = '['


class Partitura:
    """
    Tokenizador da linha de UMA voz.

    Recebe a linha de texto na inicialização, varre-a por completo (lexer) e
    armazena a lista de Tokens resultante. É apenas isso: não guarda configuração
    de voz. O prefixo da linha não é caso especial — o `!;,` inicial vira um
    TokenInstrumento (não ocupa beat, então é aplicado antes da 1ª nota) e o `[n]`
    vira N TokenPausa. Expõe um cursor de leitura (has_next/proximo_token/reiniciar)
    consumido pelo Maestro durante a execução.
    """

    def __init__(self, linha_texto: str = ""):
        self.linha_texto = linha_texto
        self.tokens: List[Token] = _tokenizar(linha_texto)
        self.posicao = 0


    def has_next(self) -> bool:
        return self.posicao < len(self.tokens)

    def proximo_token(self) -> Token | None:
        if not self.has_next():
            return None
        token = self.tokens[self.posicao]
        self.posicao += 1
        return token

    def reiniciar(self):
        self.posicao = 0


def _tokenizar(linha: str) -> List[Token]:
    """
    Varre a linha inteira, classificando cada caractere em um Token. Mantém o
    lookback `nota_anterior` para resolver, já em tempo de parse, a regra de
    repetição (uma consoante/vogal repete a última nota).
    """
    tokens: List[Token] = []
    nota_anterior = None
    i = 0
    n = len(linha)

    while i < n:
        # Atraso `[n]` -> N tokens de pausa
        if linha[i] == '[':
            pausas, i = _consumir_atraso(linha, i)
            if pausas is not None:
                tokens.extend(pausas)
                continue

        # Ignora espaços em branco como delimitadores puros de notas
        if linha[i] == ' ':
            i += 1
            continue

        char, i = _proximo_caractere(linha, i)
        token, nota_anterior = _classificar(char, nota_anterior)
        tokens.append(token)

    return tokens

def _consumir_atraso(linha: str, i: int) -> tuple[List[Token] | None, int]:
    """
    Tenta ler `[n]` a partir de `i`. Em caso de sucesso, retorna N
    TokenPausa (n >= 0) e o índice logo após `]`. Se não houver `]` ou `n`
    não for inteiro, retorna (None, i) — o `[` segue o fluxo normal.
    """
    fim = linha.find(']', i)
    if fim == -1:
        return None, i
    try:
        n = max(int(linha[i + 1:fim]), 0)
    except ValueError:
        return None, i
    return [TokenPausa(CHAR_ATRASO) for _ in range(n)], fim + 1

def _proximo_caractere(linha: str, i: int) -> tuple[str, int]:
    """Lê o próximo caractere, tratando o token duplo `Mb`."""
    if linha[i] == 'M' and i + 1 < len(linha) and linha[i + 1] == 'b':
        return 'Mb', i + 2
    return linha[i], i + 1

def _classificar(char: str, nota_anterior: str | None) -> tuple[Token, str | None]:
    """
    Classifica um único caractere num Token e devolve o `nota_anterior`
    atualizado (alterado apenas quando o caractere é uma nota).
    """
    match char:
        # Notas (atualizam o lookback de repetição)
        case c if c in NOTAS:
            return TokenNota(char), char
        # Pausas (a-h)
        case c if c in PAUSAS:
            return TokenPausa(char), nota_anterior
        # Troca de instrumento por símbolo (! ; ,)
        case c if c in MAPA_INSTRUMENTO_SIMBOLO:
            return TokenInstrumento(char, MAPA_INSTRUMENTO_SIMBOLO[char]), nota_anterior
        # Gaita de Foles (O, I, U)
        case c if c in ['O', 'I', 'U']:
            return TokenInstrumento(char, INSTRUMENTO_BAGPIPE), nota_anterior
        # Controle de oitava
        case '?':
            return TokenOitavaUp(char), nota_anterior
        case 'V':
            return TokenOitavaDown(char), nota_anterior
        # Controle de volume (+ / -)
        case '+':
            return TokenVolumeUp(char), nota_anterior
        case '-':
            return TokenVolumeDown(char), nota_anterior
        # Controle de BPM global (removido, ignorado textualmente)
        case '>' | '<':
            return TokenIgnore(char), nota_anterior
        # Dígitos -> troca de instrumento (par: incrementa o atual; ímpar: Tubular Bells)
        case c if c.isdigit():
            digito = int(char)
            if digito % 2 == 0:
                return TokenInstrumentoIncremento(char, digito), nota_anterior
            return TokenInstrumento(char, INSTRUMENTO_TUBULAR_BELLS), nota_anterior
        # Consoantes e caracteres não mapeados geram silêncio/pausa
        case c if c.isalpha() or not c.isspace():
            return TokenPausa(char), nota_anterior
        # Caracteres ignorados (espaços que não dobram volume, etc.)
        case _:
            return TokenIgnore(char), nota_anterior
