# Appointment Management API

API REST desarrollada en Python para la gestión de turnos aplicando reglas de negocio reales.
El objetivo del proyecto es demostrar buenas prácticas en el diseño de APIs backend para perfiles trainee/junior.

---

## 🚀 Características principales

- Creación de turnos con validaciones
- Listado de turnos con filtros
- Cancelación lógica de turnos (soft delete)
- Separación clara entre rutas, lógica de negocio y modelos
- Manejo de errores y códigos HTTP

---

## 🧠 Reglas de negocio implementadas

- No se pueden crear turnos en fechas pasadas
- Horario permitido: 09:00 a 18:00
- Un usuario no puede reservar dos turnos en el mismo horario
- Los turnos no se eliminan físicamente, se cancelan
- Validaciones previas a persistir datos

---

## 🛠️ Tecnologías utilizadas

- Python 3
- Flask
- SQLite
- SQLAlchemy
- Pydantic
- Git

---

## 📂 Estructura del proyecto

```txt
appointment_api/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── services.py
│   ├── routes.py
│   └── utils.py
├── requirements.txt
├── README.md
└── .gitignore

▶️ Ejecución del proyecto

Clonar el repositorio

Crear entorno virtual (opcional)

Instalar dependencias:

pip install -r requirements.txt


Ejecutar la aplicación:

python app/main.py


La API quedará disponible en:

http://localhost:5000

## Interfaz Web

El proyecto incluye una interfaz web simple desarrollada con Jinja2 para facilitar la interacción con la API.

Funcionalidades:
- Listado de turnos
- Creación de turnos mediante formulario
- Cancelación de turnos
- Mensajes de feedback (flash messages)
- Página 404 personalizada

La interfaz prioriza simplicidad, claridad y correcta separación entre lógica de negocio y presentación.
