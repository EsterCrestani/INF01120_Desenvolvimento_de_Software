# Poderia ser Instrumento por exemplo
class Exemplo:
    # Atributos
    parametro: int

    # Construtor
    def __init__(self, parametro: int):
        self.parametro = parametro

    # Métodos
    def getParametro(self) -> int:
        return self.parametro

    def setParametro(self, parametro: int):
        self.parametro = parametro
