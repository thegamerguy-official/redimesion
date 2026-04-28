# CONTEXTO TÉCNICO Y DE NEGOCIO: REDIMENSION

## 1. Visión General y Propuesta de Valor
REDIMENSION es un software B2B SaaS de optimización espacial diseñado para el sector de la logística e-commerce y operadores 3PL (PYMES)[cite: 1]. Su función principal es asistir en el proceso de Pick & Pack para eliminar el "sobredimensionamiento crónico de los embalajes"[cite: 1]. El sistema sustituye la intuición humana por un algoritmo de "Problema de Empaquetado 3D" (3D Bin Packing) que dicta la caja óptima en tiempo real[cite: 1]. 

El valor del software reside en un Triple ROI: reducción de consumibles (cartón/plásticos), ahorro en tarifas de transporte por "peso volumétrico" y disminución de emisiones de CO2 (Alcance 3)[cite: 1].

## 2. Definición del Problema Operativo
*   **Fallo de percepción humana (Efecto Tetris):** Bajo presión de tiempo, los operarios eligen cajas más grandes de lo necesario por aversión al riesgo y dificultad mental para rotar objetos 3D[cite: 1].
*   **Fórmula del Peso Volumétrico:** Las agencias cobran usando la fórmula $(Largo \times Ancho \times Alto) / 5000$[cite: 1]. Esto penaliza severamente el envío de "aire"[cite: 1].
*   **Penalización en última milla:** Furgonetas que se llenan por volumen antes que por peso máximo legal, requiriendo más vehículos y empeorando la saturación urbana[cite: 1].

## 3. Arquitectura y Lógica del Motor Algorítmico
El backend debe resolver el Problema de Empaquetado 3D de forma ultra-rápida (fracciones de segundo) para no retrasar la cadena de montaje[cite: 1].
*   **Data de Entrada (Inputs):** 
    *   Dimensiones en 3 ejes (Alto, Ancho, Profundo) y peso de cada SKU (artículo) del catálogo[cite: 1].
    *   Dimensiones internas de los tipos de cajas de cartón disponibles en el inventario del cliente (ej. Caja A, Caja B, Sobre Kraft)[cite: 1].
*   **Procesamiento:** El algoritmo evalúa combinaciones de rotación en los ejes X, Y, Z para lograr el encaje más denso posible[cite: 1].
*   **Data de Salida (Output):** La identificación exacta del contenedor más pequeño requerido para el pedido completo y, opcionalmente, las coordenadas u orientación visual para colocar cada ítem dentro de esa caja[cite: 1].

## 4. Restricciones de la Interfaz de Usuario (UX/UI Frontend)
El entorno de uso es hostil para interfaces complejas: es un almacén con ruido, estrés por cumplir SLAs, y operarios que usan guantes[cite: 1].
*   **Dispositivo:** Tablet o pantalla táctil en la mesa de empaquetado[cite: 1].
*   **Flujo Cero-Clics:** El sistema debe integrarse con lectores de códigos de barras convencionales; al escanear el ID del pedido, el resultado debe aparecer automáticamente[cite: 1].
*   **Jerarquía Visual:** Interfaz sin texto innecesario[cite: 1]. Uso estricto de códigos de colores (tipo semáforo) y botones sobredimensionados[cite: 1].
*   **Veredicto Visual:** Mensajes inequívocos como "Caja Modelo B" y un esquema 3D simplificado de disposición de los productos[cite: 1].

## 5. Casos de Prueba (Validación Empírica para Unit Testing)
El algoritmo debe ser capaz de superar los siguientes casos reales documentados en el "Experimento del Aire"[cite: 1]:
*   **Caso 1 (Micro-producto):** Input: 1 Memoria USB. Output esperado: Sobre Kraft Acolchado A5 (eliminando el 88.9% de volumen respecto a cajas estándar)[cite: 1].
*   **Caso 2 (Textil Múltiple):** Input: 1 pantalón, 2 camisetas, 1 cinturón. Output esperado: Caja compacta (reducción del 70.6%), asumiendo flexibilidad de los ítems[cite: 1].
*   **Caso 3 (Efecto Tetris):** Input: 3 libros tapa dura y 1 libreta. Output esperado: Apilado vertical (eje Z) con rotación a 90 grados de la libreta, logrando una caja cúbica un 62.5% más pequeña[cite: 1].

## 6. Base de Datos y Módulo SaaS (Backend & Analytics)
El sistema opera bajo suscripción (Plan Starter / Plan Pro) y requiere demostrar su valor mediante datos[cite: 1].
*   **Esquema de Datos Core:** Entidades relacionales para Clientes, Catálogo de SKUs, Inventario de Cajas y Registro de Pedidos Procesados.
*   **Métricas de Impacto (Dashboard):** El sistema debe almacenar la diferencia entre el "volumen bruto del pedido" y el "volumen de la caja óptima calculada" para generar reportes mensuales de cumplimiento ESG y ODS[cite: 1].
*   **KPIs a reportar:** Kilogramos de cartón ahorrados y reducción de emisiones de CO2[cite: 1].