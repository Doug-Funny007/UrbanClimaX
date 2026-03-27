# UrbanClimaX — Render hardened

Versão preparada para **GitHub + deploy no Render** com configuração mais robusta para Streamlit.

## O que foi ajustado

- `render.yaml` reforçado para deploy via Blueprint
- `render_start.py` adicionado para iniciar o Streamlit com:
  - `0.0.0.0`
  - porta do `PORT` do Render
  - modo headless
- `.streamlit/config.toml` ajustado para ambiente cloud
- `runtime.txt` adicionado como redundância útil para versão do Python
- `README.md` atualizado com fluxo de deploy e troubleshooting rápido

## Estrutura principal

```text
UrbanClimaX-Render-hardened/
├── .streamlit/
│   └── config.toml
├── assets/
│   └── logo.png
├── .gitignore
├── .python-version
├── runtime.txt
├── app.py
├── render.yaml
├── render_start.py
├── requirements.txt
└── README.md
```

## Deploy no Render

### Opção 1 — via `render.yaml`

1. Envie este projeto para um repositório no GitHub.
2. No Render, escolha **New +** → **Blueprint**.
3. Conecte o repositório.
4. O Render lerá automaticamente o `render.yaml`.

### Opção 2 — configuração manual

Use estes valores:

**Environment**
```text
Python
```

**Build Command**
```bash
pip install --upgrade pip setuptools wheel && pip install -r requirements.txt
```

**Start Command**
```bash
python render_start.py
```

## Variáveis já previstas

- `PYTHON_VERSION=3.11.11`
- `STREAMLIT_SERVER_HEADLESS=true`
- `STREAMLIT_BROWSER_GATHER_USAGE_STATS=false`

## Observações importantes

### 1. Bibliotecas geoespaciais
Este app usa dependências pesadas como `rasterio`, `geopandas`, `fiona`, `pyproj`, `shapely`, `mgwr`, `libpysal` e `esda`.
Em muitos casos o Render instala tudo normalmente via wheels, mas esse continua sendo o ponto de maior risco de build.

### 2. Plano free
O plano gratuito pode funcionar bem para testes, mas análises raster grandes, uploads extensos e processamento espacial pesado podem causar lentidão, reinícios ou falhas por memória.

### 3. Armazenamento temporário
O app usa diretórios temporários para uploads e processamento. Em deploy cloud, esse armazenamento é efêmero: arquivos não ficam persistidos entre reinícios.

## Execução local

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# ou .venv\Scripts\activate no Windows
pip install --upgrade pip
pip install -r requirements.txt
python render_start.py
```

## Troubleshooting rápido

### Build falhou em pacote geoespacial
- confira os logs do build
- valide se a falha ocorreu em `rasterio`, `fiona`, `pyproj` ou `geopandas`
- se necessário, faça uma rodada futura de enxugamento do `requirements.txt`

### Subiu, mas não abre
- confirme que o serviço é **Web Service**
- confirme que o comando inicial é `python render_start.py`
- confira nos logs se a aplicação bindou na porta do `PORT`

### App reinicia sozinho
- normalmente é limite de memória ou processamento no plano free
- nesse caso, reduza tamanho dos arquivos de entrada ou use plano com mais recursos
