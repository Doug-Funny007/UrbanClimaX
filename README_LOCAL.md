# UrbanClimaX com RSEI — versão local

Esta versão foi preparada para execução local no Windows.

## Requisitos
- Windows 10 ou 11
- Python 3.10 ou 3.11 instalado

## Execução rápida
1. Extraia o ZIP.
2. Abra a pasta do projeto.
3. Dê duplo clique em `run_local.bat`.

O script cria um ambiente virtual `.venv`, instala as dependências e abre o app no navegador.

## Execução via PowerShell
Rode `run_local.ps1`.

## Gerar executável local
Se quiser compilar no seu PC:
1. Dê duplo clique em `build_exe_pyinstaller.bat`
2. Ao final, o executável ficará em `dist/UrbanClimaX_RSEI/`

## Observações
- O primeiro início pode demorar alguns minutos por causa da instalação das bibliotecas.
- O app usa bibliotecas pesadas de geoprocessamento (`rasterio`, `geopandas`, `fiona`, `pyproj`).
- Para datasets Landsat grandes, prefira máquina com pelo menos 16 GB de RAM.
