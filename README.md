# Proyecto Gestor de Tareas con Python y Docker

Este proyecto implementa una aplicación distribuida con **3 contenedores Docker**:

- **Frontend**: Interfaz web (Flask + HTML).
- **Backend**: API REST (Flask) que conecta frontend y base de datos.
- **DB**: Servicio en Flask que maneja una base de datos SQLite.

## Ejecución

```bash
docker-compose up --build
```

- Frontend disponible en: http://localhost:3000  
- Backend API en: http://localhost:5000/tareas  
- Servicio de base de datos en: http://localhost:6000/tareas
