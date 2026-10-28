# PrevenApp

Guía de configuración y colaboración para el desarrollo de PrevenApp.

## Contenido

1. [Requisitos previos](#requisitos-previos)
2. [Configuración del entorno](#configuración-del-entorno)
3. [Estructura del proyecto](#estructura-del-proyecto)
4. [Flujo de trabajo con Git](#flujo-de-trabajo-con-git)
5. [Convención de commits](#convención-de-commits)
6. [Extensiones recomendadas para VS Code](#extensiones-recomendadas-para-vs-code)
7. [Documentación relacionada](#documentación-relacionada)

## Requisitos previos

- Python, en una versión compatible con las dependencias del proyecto.
- Git.
- Un entorno virtual de Python, como `venv` (recomendado).

> **Dependencias:** actualmente no hay un archivo `requirements.txt` en el repositorio. Antes de instalar las dependencias, confirma con el equipo las versiones requeridas y registra las dependencias del proyecto en un manifiesto.

## Configuración del entorno

### 1. Clonar el repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd <DIRECTORIO_DEL_REPOSITORIO>
```

### 2. Crear y activar un entorno virtual

**Windows (PowerShell):**

```powershell
python -m venv venv
.\venv\Scripts\Activate
```

**macOS o Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

Cuando el equipo haya definido y agregado el archivo `requirements.txt`, instala las dependencias desde la raíz del repositorio:

```bash
python -m pip install -r requirements.txt
```

### 4. Ejecutar migraciones y servidor

Los siguientes comandos se ejecutan desde la carpeta `src`:

```bash
cd src
python manage.py migrate
python manage.py runserver
```

Abre <http://127.0.0.1:8000/> para acceder a la aplicación. Para detener el servidor, usa `Ctrl+C`.

> La configuración actual no incluye un archivo `.env.example` ni documenta variables de entorno. Consulta con el equipo antes de crear o configurar variables adicionales.

## Estructura del proyecto

```text
PrevenApp-Develop-/
├── .github/                 # Plantillas de Issues y Pull Requests
├── docs/                    # Guías y documentación del proyecto
├── src/
│   ├── app_prevenapp/       # Aplicación de Django y sus plantillas
│   ├── pr_prevenapp/        # Configuración del proyecto Django
│   ├── media/               # Archivos cargados por usuarios (no versionados)
│   ├── static/              # Archivos estáticos del proyecto
│   └── manage.py            # Comandos de administración de Django
├── .gitignore
└── README.md
```

Los archivos de la carpeta `media/`, la base de datos local `db.sqlite3` y los entornos virtuales no deben subirse al repositorio. El archivo `.gitignore` ya excluye estos elementos.

## Flujo de trabajo con Git

El equipo utiliza `develop` como rama de integración y `main` como rama de producción. No hagas `push` directamente a `main`.

### Ramas de trabajo

Crea cada rama desde la rama base correspondiente y usa el formato `tipo/descripcion-corta`.

| Tipo | Propósito | Ejemplo |
|---|---|---|
| `feature/` | Agregar funcionalidad | `feature/gestion-usuarios` |
| `bugfix/` | Corregir un error no crítico | `bugfix/alineacion-header` |
| `hotfix/` | Corregir urgentemente producción; parte de `main` | `hotfix/conexion-db` |
| `docs/` | Actualizar documentación | `docs/guia-instalacion` |

Ejemplo para iniciar una funcionalidad:

```bash
git checkout develop
git pull origin develop
git checkout -b feature/gestion-usuarios
```

### Pull Requests

1. Actualiza `develop` y crea una rama para tu tarea.
2. Implementa los cambios y realiza commits descriptivos.
3. Publica la rama en el repositorio remoto:

   ```bash
   git push -u origin feature/gestion-usuarios
   ```

4. Abre un Pull Request hacia `develop` y solicita la revisión de al menos un compañero.
5. Integra los cambios cuando el Pull Request esté aprobado y las verificaciones hayan pasado.

## Convención de commits

Usa el formato de Conventional Commits:

```text
<tipo>: <descripción breve>
```

| Tipo | Uso |
|---|---|
| `feat` | Agregar una funcionalidad |
| `fix` | Corregir un error |
| `docs` | Actualizar documentación |
| `style` | Aplicar cambios de formato que no alteran la lógica |
| `refactor` | Mejorar el código sin agregar funcionalidad ni corregir un error |
| `test` | Agregar o corregir pruebas |

Ejemplo:

```bash
git commit -m "feat: agregar validación al formulario de registro"
```

## Extensiones recomendadas para VS Code

| Extensión | Identificador | Uso |
|---|---|---|
| Python | `ms-python.python` | Ejecución y depuración de Python |
| Pylance | `ms-python.vscode-pylance` | Autocompletado y análisis de tipos |
| Django | `batisteo.vscode-django` | Soporte para plantillas Django |
| Ruff | `charliermarsh.ruff` | Análisis y formato de código |
| EditorConfig for VS Code | `EditorConfig.EditorConfig` | Mantener consistentes los estilos del editor |

## Documentación relacionada

- [Definición de terminado](docs/definition-of-done.md)
- [Guía de aprendizaje del Sprint 1](docs/guia-aprendizaje-sprint1.md)
- [Rúbrica de evaluación](docs/rubrica-evaluacion.md)
