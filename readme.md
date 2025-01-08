# LowCostWatch - Log Viewer

<p align="center">
  <img src="icons/icon.png" alt="LowCostWatch Icon" width="120px">
</p>

**LowCostWatch** é uma aplicação de desktop para visualização e filtragem de logs. A solução foi desenvolvida usando **Python**, **PyQt6** para a interface gráfica, e **boto3** para a interação com a AWS S3.

## Tecnologias Usadas

- **Python**: Linguagem de programação utilizada para desenvolver a aplicação.
- **PyQt6**: Framework para desenvolver a interface gráfica (GUI), utilizado para criar janelas, botões, e gerenciamento de eventos.
- **boto3**: SDK da AWS utilizado para interagir com o Amazon S3 na leitura e carregamento dos arquivos de log comprimidos.
- **gzip**: Utilizado para descomprimir os arquivos '.log.gz' armazenados no S3.

## Funcionalidades

- **Visualização de logs**: A aplicação permite ao usuário visualizar logs de diferentes formatos, sem a necessidade de uma instalação pesada ou servidores específicos.
- **Filtragem**: O usuário pode aplicar filtros para localizar entradas específicas de log.
- **Exportação de Logs**: O usuário pode exportar os logs filtrados para um arquivo em formato texto ou CSV.
- **Suporte ao AWS S3**: Permite ao usuário carregar logs diretamente de um bucket do S3 configurado no AWS.

## Requisitos

Certifique-se de ter o seguinte instalado no seu ambiente de desenvolvimento:
- **Python 3.x**: A versão do python utilizada, é recomendável o 3.9 ou superior.
- **Bibliotecas**:
    - 'boto3': para interação com o Amazon S3.
    - 'PyQt6' : para a criação da interface gráfica.
    - 'gzip': usada para descomprimir arquivos '.log.gz*


Você pode instalar as dependências com o seguinte comando:
```bash
pip install -r requirements.txt
```

## Uso

1. **Configuração do AWS Profile**: Selecionar o profile da AWS com o qual os logs serão carregados.
2. **S3 Path**: Inserir o caminho do bucket e da pasta dos logs dentro do S3 (exemplo: *s3://meu-bucket/pasta/logs/*).
3. **Carregar Logs**: Ao clicar em "Load Logs", os logs disponíveis serão carregados e listados. Após carregar, você poderá visualizar os detalhes e aplicar filtros.
4. **Aplicar Filtro**: O campo de filtro permite pesquisar por palavras-chave nos logs.
5. **Exportar Logs**: Permite salvar os logs filtrados em arquivos 'txt' ou 'csv'.

## Estrutura do Projeto
A estrutura do projeto é organizada em duas principais pastas:

```bash
low_cost_watch/
├── main.py              # Ponto de entrada (inicia a aplicação PyQt6)
├── requirements.txt
│
├── ui/
│   ├── log_viewer_window.py
│   └── __init__.py
│
├── core/
│   ├── s3_manager.py    # Lida com conexão S3, listagem e download
│   ├── log_parser.py    # Lida com regex e parsing das linhas de log
│   └── __init__.py
│
├── icons/
│   └── icon.png         # Ícone do projeto
│
└── README.md            # Este arquivo
```

## Contributions
Se core dessa contribuir para o projeto, fique à vontade para fazer um **fork** e sugerir **pull requests** com melhorias ou correções.