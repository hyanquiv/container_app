# Cloud Computing - Lab A  
**Pregrado 2025B**  
**Tema: Contenedores**  

**Alumno:** Henry Aron Yanqui Vera  

---

## 📌 Introducción  
En este laboratorio se desarrolló una aplicación simple compuesta por **tres contenedores**:  

1. **Frontend** → Encargado de la interfaz para interactuar con el usuario.  
2. **Backend** → Provee la lógica de negocio y procesa las peticiones.  
3. **Base de datos** → Almacena los resultados generados.  

Cada contenedor cuenta con su propio **Dockerfile** y todos son orquestados mediante **docker-compose**.  

---

## ⚙️ Estructura de la solución  

```
.
├── frontend/
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
├── backend/
│   ├── app.py
│   ├── aligner.py
│   └── Dockerfile
├── db/
│   ├── app.py
│   ├── db.sqlite   # se genera automáticamente
│   └── Dockerfile
└── docker-compose.yml
```

---

## 🚀 Funcionamiento de los contenedores  

### 1. **Frontend**  
- Construido con **Flask**.  
- Expone un formulario para subir archivos y consultar historial.  
- Envía peticiones HTTP al **backend** para procesar datos.  

### 2. **Backend**  
- También desarrollado en **Flask**.  
- Recibe los archivos desde el frontend, los procesa y genera resultados.  
- Se comunica con la **base de datos** vía peticiones HTTP (`POST` y `GET`).  

### 3. **Base de datos (DB)**  
- Implementada con **Flask + SQLite**.  
- Expone endpoints REST para:  
  - Guardar nuevos registros (`/save`)  
  - Listar resultados (`/list`)  
  - Recuperar un registro por ID (`/get/<id>`)  
- Los datos se almacenan en un archivo `db.sqlite` persistente dentro del contenedor.  

---

## 🔄 Interacción entre contenedores  

La comunicación se gestiona mediante **docker-compose**, que crea una red interna:  

- El **frontend** se conecta al **backend** usando la URL `http://backend:5000`.  
- El **backend** se conecta al **db** usando la URL `http://db:6000`.  

Esto evita el uso de `localhost` dentro de los contenedores y permite que todos interactúen de manera aislada pero conectada.  

---

## 🐳 Configuración de contenedores  

### Dockerfile (ejemplo simplificado para backend)  

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

CMD ["python", "app.py"]
```

Cada servicio tiene su propio Dockerfile con la misma lógica:  
1. Se copia el código.  
2. Se instalan dependencias.  
3. Se expone el puerto y ejecuta la aplicación.  

---

### docker-compose.yml  

```yaml
version: "3.9"
services:
  frontend:
    build: ./frontend
    ports:
      - "8501:8501"
    depends_on:
      - backend

  backend:
    build: ./backend
    ports:
      - "5000:5000"
    depends_on:
      - db

  db:
    build: ./db
    ports:
      - "6000:6000"
    volumes:
      - db_data:/app/data

volumes:
  db_data:
```

---

## ▶️ Ejecución  

1. Construir y levantar los contenedores:  
   ```bash
   docker-compose up --build
   ```
2. Acceder al **frontend** en el navegador:  
   ```
   http://localhost:3000
   ```
3. Probar flujo:  
   - Subir archivo desde frontend.  
   - Backend procesa y envía resultados al DB.  
   - Consultar historial desde frontend.  

---

## 📂 Repositorio  

👉 [Enlace al repositorio](https://github.com/hyanquiv/container_bio_app)
