# Prueba con datos ficticios

⚠ Todo lo de esta carpeta es **inventado**. Sirve solo para probar el cálculo de la verificación manual; no son resultados del proyecto.

`datos/verificacion.xlsx` simula una revisión del equipo:

| Artefacto | Hallazgos IA (únicos) | Confirmados | Falsos positivos | Pendientes | Nuevos del equipo |
| --- | --- | --- | --- | --- | --- |
| ERS | 49 | 40 | 5 | 4 | 4 |
| DAS | 14 | 12 | 2 | 0 | 2 |
| Brief | 5 | 4 | 1 | 0 | 1 |
| **Total** | **68** | **56** | **8** | **4** | **7** |

Los 15 duplicados están marcados a propósito como `falso_positivo` para comprobar que el cálculo los ignora.

## Ejecutar

Desde la raíz del repo:

```
python metricas_sqa.py prueba/datos
```

Los resultados se guardan en `prueba/resultados/` (no tocan los reales). Lo esperado:

- Precisión IA total: 56 / (56 + 8) = **87,5 %**
- EDD IA total: 56 / (56 + 7) = **88,9 %**
- Aviso: «Verificación en curso: 4 de 68 hallazgos sin revisar».

La hoja **Resumen** del Excel debe mostrar las mismas cifras.
