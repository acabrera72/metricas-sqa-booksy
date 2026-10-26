# Métricas de SQA - Booksy UCAB 

Script en Python con Pandas que calcula las métricas del Plan de Aseguramiento de la Calidad del Software (PACS, sección 9.2) a partir de los hallazgos de la inspección estática de Brief, ERS y DAS de Booksy UCAB.

## Métricas que calcula

| Métrica | Tipo | Qué mide |
| --- | --- | --- |
| FNC | Descriptiva (frecuencia y porcentaje) | Distribución de no conformidades por artefacto, criterio y severidad |
| DDE | Producto, índice | Defectos por unidad de análisis de cada artefacto |
| EIC | Producto, índice | Porcentaje de unidades sin ningún defecto |
| CEP | Proyecto | Porcentaje de actividades del PACS ejecutadas |
| EDD | Proceso | Eficacia de la detección (requiere defectos de fases posteriores) |
| CCI | Control estadístico | Comparación entre artefactos y correlación de Spearman y Pearson entre incompletitud e inconsistencias por sección |

## Estructura

```
metricas_sqa.py        Script principal
datos/
  hallazgos.csv        83 no conformidades: artefacto, criterio, severidad, sección y duplicados
  unidades.csv         Unidades de análisis de DDE y EIC (9 por artefacto)
  secciones.csv        Secciones de cada artefacto y su grado de incompletitud (CCI)
  actividades.csv      Actividades del PACS con su estado en Jira y su evidencia (CEP)
resultados/            Salidas generadas por el script
```

## Uso

```
pip install -r requirements.txt
python metricas_sqa.py
```

El script lee la carpeta `datos/`, imprime los resultados y guarda las tablas en `resultados/`. Si cambia un hallazgo tras la verificación manual, basta con editar el CSV y volver a ejecutarlo.

## Supuestos

- Un defecto único es una no conformidad que no repite la evidencia de otra; los duplicados se marcan en la columna `duplicado_de`.
- Cada registro se asigna a la sección del artefacto donde debe corregirse.
- La incompletitud de una sección se mide en tres grados: 0 completa, 1 parcial (enlace externo o marcadores de plantilla), 2 vacía o solo texto de plantilla.
- Los hallazgos provienen de una prerrevisión asistida por IA y quedan sujetos a la verificación manual del equipo (PACS, sección 7.2).
