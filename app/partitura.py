from typing import List
from app.voz import Voz

class Partitura:
    def __init__(self, texto: str):
        self.vozes: List[Voz] = []
        self._inicializar_vozes(texto)
        
    def _inicializar_vozes(self, texto: str):
        linhas = texto.splitlines()
        for i, linha in enumerate(linhas):
            linha_limpa = linha.strip()
            if linha_limpa:
                voz = Voz(id_voz=i, linha_texto=linha_limpa)
                self.vozes.append(voz)
                
    def get_vozes(self) -> List[Voz]:
        return self.vozes
        
    def reiniciar_todas(self):
        for voz in self.vozes:
            voz.reiniciar_estado()

    def has_next(self) -> bool:
        return any(voz.has_next() for voz in self.vozes)
