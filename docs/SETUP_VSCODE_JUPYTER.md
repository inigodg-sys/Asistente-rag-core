Contenido para pegar en docs/SETUP_VSCODE_JUPYTER.md
# Setup del entorno: VS Code + Jupyter + venv (Windows)

Este documento describe **todo** lo que hicimos para preparar el entorno de trabajo del TFM en la carpeta del proyecto `asistente-rag-core`.

> Objetivo: tener **VS Code + Jupyter** ejecutando notebooks con un **venv** propio, dependencias instaladas y kernel registrado, listo para producir código del RAG.

---

## 0) Baseline del repositorio

Estructura mínima (confirmada):



asistente-rag-core/
├─ README.md
├─ requirements.txt
├─ LICENSE
├─ .gitignore
├─ docs/
│ ├─ ROADMAP.md
│ └─ RIESGOS.md
├─ data/
│ ├─ raw/
│ └─ index/ # ignorado en git
├─ notebooks/
└─ src/
├─ init.py
└─ app.py


`.gitignore` (fragmento relevante):


.venv/
.env
pycache/
.ipynb_checkpoints/
data/index/


---

## 1) Extensiones de VS Code
- **Python** (Microsoft)  
- **Jupyter** (Microsoft)  
- (Opcional) **Pylance**, **Jupyter Keymap**, **Jupyter Notebook Renderers**

---

## 2) Instalación de Python 3.11 (si la terminal no lo detecta)

**Winget (recomendado):**
```powershell
winget install -e --id Python.Python.3.11


Instalador oficial: https://www.python.org/downloads/windows/

Marca “Add Python to PATH”.

Desactivar alias de la Store:
Settings → Apps → Advanced app settings → App execution aliases → OFF en python.exe y python3.exe.

3) Crear y activar el entorno virtual (venv)

Detectar ruta real si python no responde:

$pyUser = "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe"
$pyProg = "C:\Program Files\Python311\python.exe"
if (Test-Path $pyUser) { $py = $pyUser } elseif (Test-Path $pyProg) { $py = $pyProg }


Crear venv:

python -m venv .venv
# o
& $py -m venv .venv


Activar venv (PowerShell):

# si PowerShell bloquea scripts
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

.\.venv\Scripts\Activate.ps1


Éxito = el prompt muestra (.venv).

4) Instalar dependencias y registrar kernel Jupyter

Usar la forma segura (instala en el venv):

python -m pip install -U pip
python -m pip install -r requirements.txt


Evitar error de rutas largas (notebook 7 / JupyterLab):

python -m pip uninstall -y jupyter jupyterlab notebook jupyterlab-widgets jupyterlab_server
python -m pip install ipykernel "notebook<7"


Registrar kernel:

python -m ipykernel install --user --name asistente-rag-core


(Opcional) Barras de progreso en notebook:

python -m pip install ipywidgets

5) Seleccionar intérprete y kernel en VS Code

Ctrl+Shift+P → Python: Select Interpreter → ...\Asistente-rag-core\.venv\Scripts\python.exe

Abrir/crear notebooks/00_smoke_test.ipynb

Kernel: asistente-rag-core

6) Smoke test
# --- Smoke test del entorno ---
import sys, platform
print("Python:", sys.version)
print("Platform:", platform.platform())

# Librerías clave del proyecto
import faiss
import transformers
import sentence_transformers
import langchain

print("✅ Entorno OK: faiss, transformers, sentence_transformers, langchain")


Si ves TqdmWarning: IProgress not found, instala ipywidgets (ver 4).

7) GPU (cuando se necesite)
# Pytorch con CUDA (ver comando recomendado en pytorch.org)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# FAISS GPU (opcional; si falla, mantener faiss-cpu)
pip uninstall -y faiss-cpu
pip install faiss-gpu


Test:

import torch
print("CUDA disponible:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("GPU:", torch.cuda.get_device_name(0))

8) Verificar venv activo

Terminal:

python -c "import sys; print(sys.executable)"
pip -V


Correcto si apuntan a ...\Asistente-rag-core\.venv\....

Notebook:

import sys, site
print("exe:", sys.executable)
print("site-packages:", site.getsitepackages())

9) Troubleshooting

Python no encontrado
Instala 3.11, apaga alias Store y reinicia terminal.

No module named ipykernel / fallo de instalación
Usa notebook<7 y registra kernel:

python -m pip uninstall -y jupyter jupyterlab notebook jupyterlab-widgets jupyterlab_server
python -m pip install ipykernel "notebook<7"
python -m ipykernel install --user --name asistente-rag-core


OSError Long Path
Usa notebook<7 o habilita Long Paths (gpedit o registro).

Activate.ps1 bloqueado

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1


Faltan librerías del smoke test

python -m pip install "faiss-cpu==1.8.0.post1"
python -m pip install sentence-transformers transformers
python -m pip install langchain langchain-community


