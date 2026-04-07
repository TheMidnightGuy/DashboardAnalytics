# Dashboard Analytics - Análisis de Calidad de los Datos y Modelo de Machine Learning.

Dashboard de analítica avanzada desarrollado en **Streamlit** con procesamiento interno de **Evidently AI** capaz de detectar *Data Drift*, *Data Quality* en base los datos que el usuario suba como archivo CSV para validar la calidad de los datos.

Logra evaluar la calidad de los datos para permitir un entrenamiento del Modelo de Machine Learning con una buena calidad de los datos, compara predicciones y genera metricas para evaluar la calidad del modelo.

---

## Ejecutar en local

**Clonar repositorio**
```bash
git clone https://github.com/TheMidnightGuy/DashboardAnalytics.git
```

### Requisitos

- Poetry instalado
- Ejecutar comandos dentro de entorno virtual (venv) en el proyecto

**1. Instalar Poetry en equipo**

*MacOS*
```bash
brew install pipx
pipx ensurepath
```

*Windows*
```bash
py -m pip install --user pipx
py -m pipx ensurepath
```

**2. Verificar instalación**
```bash
poetry --version
```

**3. Instalar dependencias del proyecto**
```bash
poetry install
```

**4. Iniciar aplicación**
```bash
streamlit run app.py
```

## Ejecutar con Docker

### Requisitos

- Docker instalado en el equipo

**1. Clonar repositorio**
```bash
git clone https://github.com/TheMidnightGuy/DashboardAnalytics.git
cd DashboardAnalytics
```
**2. Descargar imagen desde GHCR**
```bash
docker pull ghcr.io/themidnightguy/dashboard_analytics:latest
```

**3. Ejecutar contenedor**
```bash
docker run -p 8501:8501 dashboard-analytics
```

**4. Acceder a la aplicación**

Abrir en el navegador: `http://localhost:8501`