# MN Clean Car — Backend

API REST en Python/FastAPI conectada a Supabase.

---

## 🚀 Despliegue en 3 pasos

### PASO 1 — Configurar Supabase (base de datos gratuita 24/7)

1. Ve a **https://supabase.com** y crea una cuenta gratis
2. Crea un nuevo proyecto (guarda la contraseña de la BD)
3. En el menú lateral ve a **SQL Editor**
4. Copia y pega todo el contenido de `schema.sql` y presiona **Run**
5. Ve a **Settings > API** y copia:
   - `Project URL` → es tu `SUPABASE_URL`
   - `service_role` key (en "Project API keys") → es tu `SUPABASE_SERVICE_KEY`

---

### PASO 2 — Desplegar el backend en Railway (gratis, 24/7)

1. Ve a **https://railway.app** y crea una cuenta con GitHub
2. Haz clic en **New Project > Deploy from GitHub repo**
   - Si no tienes el código en GitHub, usa **Deploy from local** y sube esta carpeta
3. Railway detectará automáticamente el `Procfile` y usará Python
4. Ve a **Variables** y agrega estas variables de entorno:
   ```
   SUPABASE_URL=https://xxxx.supabase.co
   SUPABASE_SERVICE_KEY=eyJhbGci...
   JWT_SECRET=una-clave-secreta-larga-y-aleatoria
   ```
5. Railway desplegará y te dará una URL pública como:
   `https://mn-clean-car-api.up.railway.app`

---

### PASO 3 — Conectar el frontend en Netlify

En el frontend (tu archivo JS compilado), la URL del API está en:
```
https://language-helper-82.preview.emergentagent.com/api
```

Para cambiarlo a tu nuevo backend, tienes 2 opciones:

**Opción A — Variable de entorno en Netlify (recomendado):**
- En Netlify > Site > Environment variables, agrega:
  ```
  EXPO_PUBLIC_API_URL=https://mn-clean-car-api.up.railway.app
  ```
- Luego reconstruye el proyecto Expo con esta variable

**Opción B — Editar directamente (más rápido):**
- Abre el archivo JS del bundle y reemplaza la URL del API
- Vuelve a subir el ZIP a Netlify

---

## 🔑 Usuario admin

- **Teléfono:** `8717958646`
- **Contraseña:** `Andrea27!`

---

## 📋 Endpoints disponibles

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | /auth/register | Registro de usuario |
| POST | /auth/login | Login |
| GET | /auth/me | Usuario actual |
| GET | /services | Listar servicios |
| POST | /services | Crear servicio (admin) |
| PUT | /services/{id} | Editar servicio (admin) |
| DELETE | /services/{id} | Eliminar servicio (admin) |
| GET | /bookings | Todas las citas (admin) |
| GET | /bookings/me | Mis citas (cliente) |
| GET | /bookings/availability | Horarios disponibles |
| POST | /bookings | Crear cita |
| PATCH | /bookings/{id}/status | Cambiar estado (admin) |
| GET | /coupons | Todos los cupones (admin) |
| GET | /coupons/me | Mis cupones (cliente) |
| POST | /coupons | Crear cupón (admin) |
| DELETE | /coupons/{id} | Eliminar cupón (admin) |
| GET | /expenses | Listar egresos (admin) |
| POST | /expenses | Crear egreso (admin) |
| DELETE | /expenses/{id} | Eliminar egreso (admin) |
| GET | /admin/dashboard | Estadísticas (admin) |

---

## 🛠️ Desarrollo local

```bash
pip install -r requirements.txt

# Crea un archivo .env
echo "SUPABASE_URL=https://xxxx.supabase.co" > .env
echo "SUPABASE_SERVICE_KEY=eyJ..." >> .env
echo "JWT_SECRET=mi-secreto-local" >> .env

uvicorn main:app --reload
```

La API estará en http://localhost:8000
Documentación automática en http://localhost:8000/docs
