# Pacote ui — expõe apenas o que o InterfaceApp precisa importar
from app.ui.page_home     import PageHome
from app.ui.page_input    import PageInput
from app.ui.page_config   import PageConfig
from app.ui.page_playing  import PagePlaying
from app.ui.page_finished import PageFinished

__all__ = ["PageHome", "PageInput", "PageConfig", "PagePlaying", "PageFinished"]
