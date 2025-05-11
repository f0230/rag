# Sistema RAG con LangChain, ChromaDB y Khoj

Este proyecto implementa un sistema de Recuperación Aumentada de Generación (RAG) utilizando LangChain como framework de orquestación, ChromaDB como base de datos vectorial y Khoj como LLM.

## Arquitectura

El sistema está compuesto por los siguientes componentes:

- **Backend FastAPI**: API RESTful para procesar documentos y responder consultas
- **ChromaDB**: Base de datos vectorial para almacenar y buscar embeddings
- **Khoj**: LLM que se utiliza para generar respuestas basadas en el contexto recuperado
- **Frontend Next.js**: Interfaz de usuario web para interactuar con el sistema

Todo el sistema está containerizado con Docker Compose para facilitar el despliegue y desarrollo.

## Requisitos previos

- Docker y Docker Compose instalados
- Al menos 16GB de RAM disponible (32GB recomendado)
- Linux (probado en Linux Mint 22)

## Estructura de directorios

```
proyecto-rag/
├── backend/
│   ├── app/
│   │   ├── main.py          # API principal de FastAPI
│   │   ├── ingest.py        # Procesamiento de documentos
│   │   ├── chains.py        # Definición de cadenas LangChain
│   │   └── vectorstore.py   # Configuración de ChromaDB
│   ├── Dockerfile           # Configuración Docker para el backend
│   └── requirements.txt     # Dependencias Python
├── frontend/
│   ├── pages/               # Páginas Next.js
│   ├── Dockerfile           # Configuración Docker para el frontend
│   └── package.json         # Dependencias NPM
├── data/                    # Directorio para los documentos
├── .env                     # Variables de entorno
└── docker-compose.yml       # Configuración de servicios Docker
```

## Cómo empezar

### 1. Clonar y configurar el proyecto

```bash
# Crear la estructura de directorios
mkdir -p proyecto-rag/backend/app
mkdir -p proyecto-rag/frontend/pages
mkdir -p proyecto-rag/data
cd proyecto-rag
```

### 2. Copiar los archivos de configuración

Copie todos los archivos del repositorio a la estructura de directorios creada.

### 3. Iniciar los servicios con Docker Compose

```bash
docker-compose up -d
```

Este comando iniciará todos los servicios definidos en `docker-compose.yml`:
- Backend en http://localhost:8000
- ChromaDB en http://localhost:8100
- Khoj en http://localhost:4000
- Frontend en http://localhost:3000

### 4. Acceder a la aplicación

Abra su navegador en [http://localhost:3000](http://localhost:3000) para acceder a la interfaz de usuario.

## Uso del sistema

### Cargar documentos

1. Desde la interfaz web, use el panel lateral para subir documentos (PDF, DOCX, TXT, etc.)
2. El sistema procesará automáticamente los documentos, extrayendo texto y generando embeddings
3. Los documentos procesados estarán disponibles para consultas inmediatamente

### Realizar consultas

1. Escriba su pregunta en el campo de texto en la parte inferior
2. El sistema recuperará la información relevante de los documentos cargados
3. Khoj generará una respuesta basada en la información recuperada
4. La respuesta incluirá referencias a las fuentes utilizadas

## Extender el sistema

### Agregar nuevos tipos de documentos

Para agregar soporte para nuevos tipos de documento, modifique `backend/app/ingest.py` y añada el loader correspondiente al diccionario `FILE_LOADERS`.

### Integrar con otras fuentes de datos

El sistema está preparado para extenderse con otras fuentes como:
- Bases de datos: implemente la función `process_database()` en `ingest.py`
- APIs externas: cree nuevas rutas en `main.py` para conectarse a APIs
- Sitios web: implemente la función `process_url()` en `ingest.py`

## Solución de problemas

### El servicio backend no puede conectarse a ChromaDB

Asegúrese de que la variable de entorno `CHROMA_HOST` esté configurada correctamente en el servicio backend.

### Khoj no responde

Verifique los logs del contenedor Khoj para asegurarse de que se ha iniciado correctamente:

```bash
docker-compose logs khoj
```

### Problemas de memoria

Si experimenta problemas de memoria, ajuste la memoria asignada a Docker en la configuración de Docker Desktop (si está usando Windows/Mac) o ajuste los límites de memoria en `docker-compose.yml`.