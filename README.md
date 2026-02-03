# kanban_project
#  **Documentación del Sistema de Gestión de Construcción**

##  **Introducción**

### **Sistema de Gestión de Construcción Profesional**

Este sistema es una aplicación web completa diseñada para gestionar proyectos de construcción, empleados y asignaciones de manera eficiente. Desarrollado con **Streamlit** y **SQLite**, proporciona una interfaz intuitiva y modular para administrar todos los aspectos de un proyecto de construcción.

### ** Características Principales**

1. **Gestión Completa de Sitios de Construcción**
   - Crear, editar y eliminar sitios
   - Seguimiento de estado (Activo/Inactivo)
   - Información detallada de cada proyecto

2. **Administración de Empleados**
   - Registro completo de empleados
   - Estados de empleo (Activo/Inactivo)
   - Identificadores únicos de empleado

3. **Sistema de Asignación Kanban**
   - Tablero visual para asignaciones
   - Drag-and-drop lógico
   - Gestión en tiempo real de asignaciones

4. **Generación de Reportes Profesionales**
   - Exportación en múltiples formatos (Excel, CSV, JSON)
   - Estadísticas detalladas
   - Envío por email integrado

5. **Interfaz Modular y Escalable**
   - Diseño responsive
   - Componentes reutilizables
   - Fácil mantenimiento

## 📁 **Estructura del Proyecto**

```
construction_system/
│
├── 📄 app.py                    # Aplicación principal y navegación
├── 🗃️ database.py               # Base de datos SQLite y operaciones CRUD
├── 🎨 ui_helpers.py             # Componentes UI reutilizables
├── 🏗️ construction_module.py    # Módulo de gestión de sitios
├── 👷 employees_module.py       # Módulo de gestión de empleados
├── 📊 report_module.py          # Módulo de generación de reportes
└── 🗄️ construction_system.db    # Base de datos SQLite
```

## ⚙️ **Configuración Técnica**

### **Tecnologías Utilizadas**
- **Frontend**: Streamlit (Python)
- **Backend**: Python 3.11+
- **Base de Datos**: SQLite
- **Email**: SMTP (modo demo/producción)
- **Formato de Datos**: JSON, CSV, Excel


### **1. Base de Datos Preconfigurada**
El sistema incluye una base de datos SQLite preconfigurada con datos de ejemplo:

**📋 Sitios de Construcción Predefinidos:**
- "12 Buildings in Minnesota" (Activo)
- "Soccer Camp NYC" (Activo) 
- "Central Building" (Activo)

**👷 Empleados Predefinidos:**
- Luis Fernández (ID: SS-12345) - Activo
- Sofía Martínez (ID: SS-12346) - Activo
- Roberto Díaz (ID: SS-12347) - Inactivo
- Ana Gómez (ID: SS-12348) - Activo

### **2. Ejecución del Sistema**
```bash
# Ejecutar la aplicación
streamlit run app.py
```

## 🎨 **Interfaz de Usuario**

### **Pantalla de Carga**
Al iniciar, el sistema muestra una pantalla de carga profesional con:
- Animaciones de pulso
- Barra de progreso
- Mensaje de bienvenida

### **Sidebar de Navegación**
Contiene:
- Logo del sistema
- Navegación entre módulos
- Información del sistema (hora/fecha)
- Estadísticas rápidas

### **Módulos Principales**

#### **📋 Assignment Board (Tablero Kanban)**
- Visualización de sitios activos
- Empleados disponibles
- Sistema de arrastrar y soltar
- Botones de asignación rápida

#### **🏗️ Construction Sites**
- Métricas de sitios (total/activos/inactivos)
- Filtros avanzados
- CRUD completo de sitios
- Búsqueda en tiempo real

#### **👷 Employees**
- Métricas de empleados
- Gestión completa de empleados
- Filtros por estado
- Validación de ID único

#### **📊 Reports**
- Generación de reportes
- Exportación múltiple
- Envío por email
- Estadísticas detalladas

##  **Sistema de Email (Modo Demo)**

### **Configuración Actual**
```python
# Modo Demo (predeterminado)
EMAIL_USER = "demo@example.com"
EMAIL_PASSWORD = "demo-password"

# Modo Producción (requiere configuración)
export EMAIL_USER="tu-email@gmail.com"
export EMAIL_PASSWORD="tu-app-password"
```

### **Características del Email**
- **Formato**: Texto plano con adjuntos
- **Adjuntos**: Excel, CSV, JSON
- **Simulación**: Modo demo integrado
- **Logs**: Historial de envíos

## **Arquitectura Modular**

### **Principio de Responsabilidad Única**
Cada módulo tiene una responsabilidad específica:

1. **`database.py`** - Operaciones de base de datos
2. **`ui_helpers.py`** - Componentes de interfaz reutilizables
3. **`construction_module.py`** - Lógica de sitios de construcción
4. **`employees_module.py`** - Lógica de empleados
5. **`report_module.py`** - Lógica de reportes
6. **`app.py`** - Navegación y coordinación

### **Patrón de Diseño**
- **MVC simplificado**: Separación clara entre datos, lógica y presentación
- **Singleton**: Base de datos única por sesión
- **Factory**: Creación de componentes UI
- **Observer**: Actualización en tiempo real del estado

##  **Seguridad y Validación**

### **Validaciones Implementadas**
- IDs únicos para empleados
- Estados consistentes (Activo/Inactivo)
- Validación de formatos de email
- Prevención de asignaciones duplicadas

### **Características de Seguridad**
- Sesiones de usuario separadas
- Cache de base de datos
- Validación de entrada del usuario
- Manejo de errores robusto

## **Capacidades de Exportación**

### **Formatos Soportados**
1. **Excel (.xlsx)**
   - Múltiples hojas
   - Formato profesional
   - Fórmulas y estilos

2. **CSV (.csv)**
   - Formato simple
   - Compatible universalmente
   - Fácil importación

3. **JSON (.json)**
   - Estructura jerárquica
   - Fácil de procesar
   - Mantiene relaciones

## **Estado de Producción**

### **Listo para Producción**
-  Base de datos estable
-  Validaciones completas
-  Interfaz responsive
-  Manejo de errores
-  Documentación completa

### ** Pendiente para Producción**
- Configuración de email real
- Autenticación de usuarios
- Logs de auditoría
- Backup automático

## **Contribución y Mantenimiento**

### **Código Abierto**
El sistema está diseñado para ser:
- **Modificable**: Código claro y comentado
- **Extensible**: Arquitectura modular
- **Mantenible**: Estándares de código consistentes

### **Ciclo de Desarrollo**
1. **Desarrollo**: Funcionalidades básicas completadas
2. **Pruebas**: Testing manual exhaustivo
3. **Documentación**: Guías completas
4. **Despliegue**: Fácil configuración

---
