"""
Métricas de calidad del PACS (sección 9.2) - Booksy UCAB, Equipo T7.

Calcula DDE, EIC, FNC, CEP, EDD y CCI a partir de los datos de la carpeta
datos/. Los hallazgos provienen del Informe de Revisiones (prerrevisión con IA);
las cifras son válidas solo después de la verificación manual del equipo.

Uso:
    python metricas_sqa.py            # usa la carpeta datos/ junto al script
    python metricas_sqa.py otra/ruta  # usa otra carpeta de datos
"""

import sys
from pathlib import Path

import pandas as pd
from scipy import stats

UMBRAL_DDE = 0.15
UMBRAL_EIC = 80.0
UMBRAL_CEP = 90.0
UMBRAL_EDD = 85.0
UMBRAL_FNC_ARTEFACTO = 20.0
ARTEFACTOS = ["ERS", "DAS", "Brief"]

# Ítems Sí y No por artefacto según los totales de las listas del informe.
# El Brief no tiene lista propia.
ITEMS_LISTAS = {
    "ERS": {"si": 33 + 5 + 1 + 4, "no": 26 + 6 + 13 + 15},
    "DAS": {"si": 1, "no": 18},
}


def separar(valor):
    if pd.isna(valor) or str(valor).strip() == "":
        return []
    return [v.strip() for v in str(valor).split("|")]


def cargar(carpeta):
    h = pd.read_csv(carpeta / "hallazgos.csv", dtype=str, keep_default_na=False)
    u = pd.read_csv(carpeta / "unidades.csv", dtype=str)
    s = pd.read_csv(carpeta / "secciones.csv", dtype=str, keep_default_na=False)
    a = pd.read_csv(carpeta / "actividades.csv", dtype=str)
    h["unico"] = h["duplicado_de"].str.strip() == ""
    return h, u, s, a


def estado(cumple):
    return "Cumple" if cumple else "No cumple"


def fnc(h):
    print("\n== FNC: Frecuencia de No Conformidades ==")
    for nombre, datos in [("Registros (como el informe)", h), ("Defectos únicos", h[h["unico"]])]:
        total = len(datos)
        print(f"\n-- {nombre}: {total} --")
        por_art = datos.groupby("artefacto").size().reindex(ARTEFACTOS, fill_value=0)
        sev = pd.crosstab(datos["artefacto"], datos["severidad"]).reindex(ARTEFACTOS, fill_value=0)
        tabla = pd.DataFrame({"fi": por_art, "%": (por_art / total * 100).round(1)}).join(sev)
        print(tabla.to_string())
        crit = pd.crosstab(datos["criterio"], datos["artefacto"]).reindex(columns=ARTEFACTOS, fill_value=0)
        crit["Total"] = crit.sum(axis=1)
        crit["%"] = (crit["Total"] / total * 100).round(1)
        print(crit.to_string())
        bloq = (datos["severidad"] == "Bloqueante").sum()
        print(f"Bloqueantes: {bloq} -> {estado(bloq == 0)} (umbral 0%)")

    print("\n-- Incumplimiento por artefacto (ítems No / ítems aplicables) --")
    for art, c in ITEMS_LISTAS.items():
        pct = c["no"] / (c["si"] + c["no"]) * 100
        print(f"{art}: {c['no']}/{c['si'] + c['no']} = {pct:.1f}% -> "
              f"{estado(pct <= UMBRAL_FNC_ARTEFACTO)} (umbral <= 20%)")
    print("Brief: sin lista propia, no calculable")


def dde_eic(h, u):
    print("\n== DDE y EIC por artefacto ==")
    filas = []
    for art in ARTEFACTOS:
        unidades = u.loc[u["artefacto"] == art, "unidad"].tolist()
        n = len(unidades)
        reg = h[h["artefacto"] == art]
        uni = reg[reg["unico"]]
        afectadas_reg = {x for v in reg["unidades"] for x in separar(v)}
        afectadas_uni = {x for v in uni["unidades"] for x in separar(v)}
        conformes_reg = n - len(afectadas_reg & set(unidades))
        conformes_uni = n - len(afectadas_uni & set(unidades))
        en_unidades = uni[uni["unidades"].str.strip() != ""]
        filas.append({
            "Artefacto": art,
            "Unidades": n,
            "DDE registros": round(len(reg) / n, 2),
            "DDE únicos": round(len(uni) / n, 2),
            "DDE solo en unidades": round(len(en_unidades) / n, 2),
            "EIC registros %": round(conformes_reg / n * 100, 1),
            "EIC únicos %": round(conformes_uni / n * 100, 1),
            "Unidades conformes (únicos)": ", ".join(sorted(set(unidades) - afectadas_uni)) or "ninguna",
        })
    tabla = pd.DataFrame(filas).set_index("Artefacto")
    print(tabla.to_string())
    print(f"Umbrales: DDE <= {UMBRAL_DDE}; EIC >= {UMBRAL_EIC}%")
    return tabla


def cep(a):
    print("\n== CEP: Cobertura de Ejecución del PACS ==")
    n = len(a)
    terminadas_jira = (a["estado_jira"].str.lower().isin(["terminada", "finalizada", "listo", "done"])).sum()
    ejec = a["ejecucion_por_evidencia"]
    completas = (ejec == "Ejecutada").sum()
    parciales = (ejec == "Parcial").sum()
    variantes = {
        "Estado en Jira (28/10/2026)": terminadas_jira / n * 100,
        "Evidencia, solo ejecutadas": completas / n * 100,
        "Evidencia, parciales = 0.5": (completas + 0.5 * parciales) / n * 100,
        "Evidencia, parciales = ejecutadas": (completas + parciales) / n * 100,
    }
    for nombre, valor in variantes.items():
        print(f"{nombre}: {valor:.1f}% -> {estado(valor >= UMBRAL_CEP)} (umbral >= 90%)")
    print(a[["clave", "actividad", "estado_jira", "ejecucion_por_evidencia", "responsable_jira"]].to_string(index=False))
    return variantes


def edd(h):
    print("\n== EDD: Eficacia de Detección de Defectos ==")
    detectados = int(h["unico"].sum())
    print(f"Defectos únicos detectados en la inspección estática: {detectados}")
    print("Defectos de los mismos artefactos detectados en fases posteriores: no disponible")
    print("EDD = N/D. Con 0 defectos posteriores daría 100% por construcción, valor sin significado.")
    print("Se calcula al cerrar las fases de construcción y pruebas (PACS 9.2).")


def cci(h, s, tabla_art):
    print("\n== CCI: Comparación y Correlación de Completitud e Inconsistencias ==")
    print("\n-- Comparación entre artefactos --")
    comp = tabla_art[["DDE únicos", "EIC únicos %"]].copy()
    comp["DDE <= 0.15"] = comp["DDE únicos"] <= UMBRAL_DDE
    comp["EIC >= 80%"] = comp["EIC únicos %"] >= UMBRAL_EIC
    print(comp.to_string())

    # Cada registro cuenta una vez en cada sección donde debe corregirse.
    filas = []
    for _, r in h.iterrows():
        for sec in separar(r["secciones"]):
            filas.append({"seccion": sec, "criterio": r["criterio"], "unico": r["unico"]})
    exp = pd.DataFrame(filas)

    datos = s[s["incluir_en_correlacion"] == "Sí"].copy()
    datos["incompletitud"] = datos["incompletitud"].astype(int)
    conteos = {
        "inconsistencias": exp[exp["criterio"] == "Coherente"].groupby("seccion").size(),
        "inconsistencias_unicas": exp[(exp["criterio"] == "Coherente") & exp["unico"]].groupby("seccion").size(),
        "defectos_totales": exp.groupby("seccion").size(),
        "defectos_no_completitud": exp[exp["criterio"] != "Completitud"].groupby("seccion").size(),
    }
    for col, serie in conteos.items():
        datos[col] = datos["seccion"].map(serie).fillna(0).astype(int)
    datos["incompleta_binaria"] = (datos["incompletitud"] > 0).astype(int)
    datos["incompletitud_sin_enlaces_hu"] = datos["incompletitud"].where(~datos["seccion"].str.startswith("ERS-HU"), 0)

    print(f"\n-- Datos por sección (n = {len(datos)}) --")
    print(datos[["seccion", "incompletitud", "inconsistencias", "inconsistencias_unicas",
                 "defectos_totales"]].to_string(index=False))
    excluidas = s[s["incluir_en_correlacion"] != "Sí"]
    if len(excluidas):
        n_exc = exp["seccion"].isin(excluidas["seccion"]).sum()
        print(f"Excluidas: {', '.join(excluidas['seccion'])} ({n_exc} registros sin sección medible)")

    pruebas = [
        ("Principal: incompletitud (0-2) vs inconsistencias", "incompletitud", "inconsistencias"),
        ("Inconsistencias únicas (sin duplicados)", "incompletitud", "inconsistencias_unicas"),
        ("Incompletitud binaria vs inconsistencias", "incompleta_binaria", "inconsistencias"),
        ("Sin contar enlaces de diagramas de HU", "incompletitud_sin_enlaces_hu", "inconsistencias"),
        ("Incompletitud vs defectos totales", "incompletitud", "defectos_totales"),
        ("Incompletitud vs defectos que no son Completitud", "incompletitud", "defectos_no_completitud"),
    ]
    print("\n-- Correlaciones --")
    resultados = []
    for nombre, x, y in pruebas:
        rho, p_s = stats.spearmanr(datos[x], datos[y])
        r, p_p = stats.pearsonr(datos[x], datos[y])
        resultados.append({"Prueba": nombre, "Coef. Spearman (ρ)": round(rho, 3), "Valor p Spearman": round(p_s, 4),
                           "Coef. Pearson (r)": round(r, 3), "Valor p Pearson": round(p_p, 4),
                           "¿Significativa? (p < 0,05)": "Sí" if p_s < 0.05 else "No"})
    res = pd.DataFrame(resultados).set_index("Prueba")
    print(res.to_string())
    print("\nPor artefacto (Spearman, principal):")
    for art in ARTEFACTOS:
        d = datos[datos["artefacto"] == art]
        if d["incompletitud"].nunique() > 1 and d["inconsistencias"].nunique() > 1:
            rho, p = stats.spearmanr(d["incompletitud"], d["inconsistencias"])
            print(f"  {art}: n = {len(d)}, rho = {rho:.3f}, p = {p:.4f}")
        else:
            print(f"  {art}: n = {len(d)}, sin variación suficiente")
    print("\nMedia de inconsistencias por grado de incompletitud:")
    print(datos.groupby("incompletitud")["inconsistencias"].agg(["count", "mean", "sum"]).round(2).to_string())
    return datos, res


def main():
    carpeta = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "datos"
    h, u, s, a = cargar(carpeta)
    print(f"Registros: {len(h)} | Defectos únicos: {int(h['unico'].sum())} | "
          f"Duplicados: {int((~h['unico']).sum())}")
    print(h[~h["unico"]].groupby("tipo_duplicado").size().to_string())
    fnc(h)
    tabla = dde_eic(h, u)
    cep(a)
    edd(h)
    datos, res = cci(h, s, tabla)
    salida = carpeta.parent / "resultados"
    salida.mkdir(exist_ok=True)
    tabla.to_csv(salida / "dde_eic.csv")
    datos.to_csv(salida / "cci_datos_por_seccion.csv", index=False)
    res.to_csv(salida / "cci_correlaciones.csv")
    print(f"\nResultados guardados en {salida}")


if __name__ == "__main__":
    main()
