class GerenciadorArquivo:
    @staticmethod
    def ler_arquivo_texto(caminho: str) -> str:
        try:
            with open(caminho, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise RuntimeError(f"Erro ao ler arquivo: {e}")

    @staticmethod
    def salvar_arquivo_texto(caminho: str, conteudo: str) -> None:
        try:
            with open(caminho, 'w', encoding='utf-8') as f:
                f.write(conteudo)
        except Exception as e:
            raise RuntimeError(f"Erro ao salvar arquivo de texto: {e}")
