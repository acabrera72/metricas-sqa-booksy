# Métricas de SQA - Booksy UCAB 

Script en Python con Pandas que calcula las métricas del Plan de Aseguramiento de la Calidad del Software (PACS, sección 9.2) a partir de los hallazgos de la inspección estática de Brief, ERS y DAS de Booksy UCAB.

## Métricas que calcula

| Métrica | Tipo | Qué mide |
| --- | --- | --- |
| FNC (Frecuencia de No Conformidades) | Descriptiva (frecuencia y porcentaje) | Distribución de no conformidades por artefacto, criterio y severidad |
| DDE | Producto, índice | Defectos por unidad de análisis de cada artefacto |
| EIC | Producto, índice | Porcentaje de unidades sin ningún defecto |
| CEP (Cobertura de Ejecución del PACS) | Proyecto | Porcentaje de actividades del PACS ejecutadas |
| EDD (Eficacia de Detección de Defectos) | Proceso | Eficacia de la detección (requiere defectos de fases posteriores) |
| CCI (Comparación y Correlación de Completitud e Inconsistencias) | Control estadístico | Comparación entre artefactos y correlación de Spearman y Pearson entre incompletitud e inconsistencias por sección |
| Verificación de la IA | Proceso | Precisión y EDD de la prerrevisión con IA frente a la verificación manual del equipo |

## Estructura

```
metricas_sqa.py          Script principal
datos/
  hallazgos.csv          83 no conformidades: artefacto, criterio, severidad, sección y duplicados
  unidades.csv           Unidades de análisis de DDE y EIC (9 por artefacto)
  secciones.csv          Secciones de cada artefacto y su grado de incompletitud (CCI)
  actividades.csv        Actividades del PACS con su estado en Jira y su evidencia (CEP)
  verificacion.csv       Resultado de la verificación manual de cada hallazgo de la IA
  defectos_nuevos.csv    Defectos que encontró el equipo y la IA no
resultados/              Salidas generadas por el script
```

## Uso

```
pip install -r requirements.txt
python metricas_sqa.py
```

El script lee la carpeta `datos/`, imprime los resultados y guarda las tablas en `resultados/`. Si cambia un hallazgo tras la verificación manual, basta con editar el CSV y volver a ejecutarlo.

## Verificación manual de la prerrevisión con IA

1. Revisar el Brief, el ERS y el DAS con las listas de chequeo, de preferencia sin mirar antes los hallazgos de la IA.
2. En `datos/verificacion.csv`, cambiar la columna `resultado` de cada hallazgo:
   - `confirmado`: es un defecto real.
   - `falso_positivo`: la IA lo marcó, pero no es un defecto.
   - `pendiente`: aún sin revisar (valor inicial).
   Las filas con `cuenta_en_metricas = No (duplicado)` no entran en el cálculo; basta con revisar sus originales.
3. Anotar en `datos/defectos_nuevos.csv` cada defecto que el equipo encontró y la IA no, con su artefacto, criterio y severidad.
4. Ejecutar el script. La sección "Verificación manual de la prerrevisión con IA" muestra, por artefacto:
   - **Precisión IA** = confirmados / (confirmados + falsos positivos)
   - **EDD IA** = confirmados / (confirmados + nuevos del equipo)

   Mientras queden hallazgos pendientes, las cifras se marcan como parciales.

## Supuestos

- Un defecto único es una no conformidad que no repite la evidencia de otra; los duplicados se marcan en la columna `duplicado_de`.
- Cada registro se asigna a la sección del artefacto donde debe corregirse.
- La incompletitud de una sección se mide en tres grados: 0 completa, 1 parcial (enlace externo o marcadores de plantilla), 2 vacía o solo texto de plantilla.
- Los hallazgos provienen de una prerrevisión asistida por IA y quedan sujetos a la verificación manual del equipo (PACS, sección 7.2).
- La EDD de la IA es una estimación de la eficacia de la prerrevisión; la EDD del PACS se calcula al cerrar construcción y pruebas.
