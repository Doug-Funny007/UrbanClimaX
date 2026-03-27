# UrbanClimaX — Análise Espacial em Climatologia Urbana

Repositório preparado para hospedagem no **GitHub**, execução local com **Streamlit** e deploy em serviços como **Render**.

## O que este repositório contém

- `app.py` — aplicação principal
- `requirements.txt` — dependências do projeto
- `.python-version` — versão recomendada do Python
- `.streamlit/config.toml` — configuração básica do Streamlit
- `assets/logo.png` — imagem do projeto
- `render.yaml` — configuração pronta para deploy no Render
- `run_local.bat` / `run_local.ps1` — inicialização local no Windows
- `build_exe_pyinstaller.bat` — script auxiliar para gerar executável local

## Estrutura

```text
UrbanClimaX-GitHub/
├── .streamlit/
│   └── config.toml
├── assets/
│   └── logo.png
├── .gitignore
├── .python-version
├── app.py
├── README.md
├── README_LOCAL.md
├── build_exe_pyinstaller.bat
├── render.yaml
├── requirements.txt
├── run_local.bat
├── run_local.ps1
└── start_urbanclimax.py
```

## Executar localmente

### Windows
```bash
run_local.bat
```

ou

```powershell
./run_local.ps1
```

### Manualmente
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

## Deploy no Render

O arquivo `render.yaml` já está pronto. Se preferir configurar manualmente:

**Build Command**
```bash
pip install --upgrade pip && pip install -r requirements.txt
```

**Start Command**
```bash
streamlit run app.py --server.port $PORT --server.address 0.0.0.0
```

## Como subir para o GitHub

Crie um repositório vazio no GitHub e depois rode no terminal, dentro da pasta do projeto:

```bash
git init
git add .
git commit -m "Initial commit - UrbanClimaX"
git branch -M main
git remote add origin https://github.com/SEU-USUARIO/SEU-REPOSITORIO.git
git push -u origin main
```

## Observações importantes

- A pasta `__pycache__` foi removida do pacote preparado para versionamento.
- O arquivo `.gitignore` já evita subir ambiente virtual, caches e artefatos locais.
- A imagem foi organizada em `assets/logo.png` para deixar o repositório mais limpo.
- O app foi mantido em formato Streamlit, ideal para GitHub + deploy web.
