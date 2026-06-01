from typing import List

from app.constantes_musicais import (
    INSTRUMENTO_HARMONICA,
    INSTRUMENTO_TUBULAR_BELLS,
    INSTRUMENTO_CHURCH_ORGAN,
    INSTRUMENTO_BAGPIPE,
    NOTAS,
    PAUSAS,
    VOGAIS,
)
from app.tokens import (
    Token,
    TokenNota,
    TokenPausa,
    TokenInstrumento,
    TokenOitavaUp,
    TokenOitavaDown,
    TokenVolumeDouble,
    TokenBpmUp,
    TokenBpmDown,
    TokenIgnore,
)


class Partitura:
    """
    Representa a sequência musical de UMA voz.

    Recebe uma linha de texto na inicialização, varre essa linha por completo
    (lexer) e armazena a lista de Tokens resultante. Expõe um cursor de leitura
    (has_next/proximo_token/reiniciar) consumido pelo Maestro durante a execução.
    """

    def __init__(self, linha_texto: str = ""):
        self.linha_texto = linha_texto
        self.tokens: List[Token] = self._tokenizar(linha_texto)
        self.posicao = 0

    def _tokenizar(self, linha: str) -> List[Token]:
        """
        Varre a linha inteira de uma vez, classificando cada caractere em um
        Token. Mantém o lookback `nota_anterior` para resolver, já em tempo de
        parse, a regra de repetição (uma consoante repete a nota anterior).
        """
        tokens: List[Token] = []
        nota_anterior = None
        i = 0
        n = len(linha)

        while i < n:
            char = linha[i]

            # Token duplo 'Mb'
            if char == 'M' and i + 1 < n and linha[i + 1] == 'b':
                char = 'Mb'
                i += 2
            else:
                i += 1

            # Notas
            if char in NOTAS:
                nota_anterior = char
                tokens.append(TokenNota(char))
            # Pausas (a-h)
            elif char in PAUSAS:
                tokens.append(TokenPausa(char))
            # Mudança de instrumento
            elif char == '!':
                tokens.append(TokenInstrumento(char, INSTRUMENTO_HARMONICA))
            elif char == ';':
                tokens.append(TokenInstrumento(char, INSTRUMENTO_TUBULAR_BELLS))
            elif char == ',':
                tokens.append(TokenInstrumento(char, INSTRUMENTO_CHURCH_ORGAN))
            # Controle de oitava
            elif char == '?':
                tokens.append(TokenOitavaUp(char))
            elif char == 'V':
                tokens.append(TokenOitavaDown(char))
            # Controle de volume
            elif char == ' ':
                tokens.append(TokenVolumeDouble(char))
            # Controle de BPM global
            elif char == '>':
                tokens.append(TokenBpmUp(char))
            elif char == '<':
                tokens.append(TokenBpmDown(char))
            # Vogais -> Gaita de Foles (Bagpipe)
            elif char in VOGAIS:
                tokens.append(TokenInstrumento(char, INSTRUMENTO_BAGPIPE))
            # Regra de repetição (consoantes e outros não classificados)
            else:
                if char.isalpha() or char.isdigit() or not char.isspace():
                    if nota_anterior:
                        tokens.append(TokenNota(nota_anterior))
                    else:
                        tokens.append(TokenPausa(char))
                else:
                    tokens.append(TokenIgnore(char))

        return tokens

    def get_tokens(self) -> List[Token]:
        return self.tokens

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
