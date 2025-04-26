🗂️ **Modelo en Cascada - Plan de Proyecto (8 semanas)**

🔹 Fase 1: Requisitos (Semana 1)
Objetivo: Definir con claridad qué debe hacer el sistema.

Entregables:

-Documento SRS (Software Requirements Specification), que incluye:

-Objetivo del sistema

-Requisitos funcionales (e.g., interceptar conexiones HTTP, capturar credenciales)

-Requisitos no funcionales (seguridad, usabilidad, desempeño)

-Casos de uso

🔹 Fase 2: Diseño (Semana 2)
Objetivo: Diseñar la arquitectura y componentes del sistema.

Entregables:

-Diagrama de contexto

-HLD (High-Level Design):

-Diagrama de arquitectura general (red → laptop → portal cautivo → base de datos)

-Componentes del sistema (captura de red, redirección, backend Django, DB)

-LLD (Low-Level Design):

-Esquema de base de datos (registro de IP/MAC, timestamp, usuario, etc.)

-Flujos de autenticación

-Lógica del portal falso (HTML + Django views)

🔹 Fase 3: Implementación (Semanas 3-5)
Objetivo: Codificar los módulos según el diseño.

Entregables:

-Código fuente funcional del sistema:

-Interfaz para interceptar tráfico (iptables/DNS spoofing)

-Portal web falso con Django (formulario de captura)

-Backend de registro de datos

-Documentación técnica del código (README, estructura del proyecto, dependencias)


🔹 Fase 4: Pruebas (Semana 6)
Objetivo: Validar el funcionamiento del sistema.

Entregables:

Plan de pruebas:

-Pruebas unitarias (formularios, rutas Django, validación de datos)

-Pruebas funcionales (flujo completo de acceso a red)

-Casos de prueba documentados

-Resultados de pruebas (bugs encontrados, soluciones aplicadas)

-Pruebas automatizadas


🔹 Fase 5: Despliegue (Semana 7)
Objetivo: Configurar y preparar el entorno real.

Entregables:

Manual de instalación:

-Requisitos del sistema (Python, Django, iptables, etc.)

-Configuración paso a paso

-Manual de usuario:

-Cómo acceder al sistema, revisar registros, detener el servicio

-Scripts de automatización (si los tienes)


🔹 Fase 6: Mantenimiento (Semana 8)
Objetivo: Documentar mejoras, posibles vulnerabilidades, y plan de soporte.

Entregables:

-Registro de incidencias detectadas

-Lista de mejoras futuras (e.g., notificaciones, dashboard de logs)

-Bitácora de cambios/versiones


