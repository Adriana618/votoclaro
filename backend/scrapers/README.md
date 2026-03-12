# VotoClaro - Infraestructura de Importacion de Datos

## Resumen

VotoClaro necesita datos de 3 fuentes para construir los perfiles de candidatos al Congreso 2026.
Este directorio contiene los schemas esperados y los scripts de importacion.

## Fuentes de Datos

### 1. Voto Informado (JNE) - `voto_informado.json`

**URL base:** https://votoinformado.jne.gob.pe

**Que extraer:** Hoja de vida de cada candidato al Senado y Camara de Diputados.

**Spider output:** Un archivo JSON con un array de candidatos. Cada candidato debe seguir
el schema definido en `schemas/voto_informado.json`.

**Campos criticos:**
- `jne_id`: ID unico del candidato en el sistema JNE
- `partido_sigla`: Debe coincidir con las siglas usadas en la app (ver mapeo abajo)
- `region`: Nombre del departamento en MAYUSCULAS tal como aparece en JNE
- `antecedentes_penales` / `sentencias`: Booleanos, son factores del controversy score

**Mapeo de siglas de partido:**
| JNE / Voto Informado | App (slug) | Nombre |
|---|---|---|
| FP | fp | Fuerza Popular |
| RP | rp | Renovacion Popular |
| PM | pm | Partido Morado |
| JPP | jpp | Juntos por el Peru |
| AP | ap | Accion Popular |
| SP | sc | Somos Peru |
| PL | pl | Peru Libre |
| AN | an | Alianza Nacional |
| APP | app | Alianza Para el Progreso |
| PP | pod | Podemos Peru |
| FE | fep | Frente Esperanza |
| AVP | avp | Avanza Pais |

### 2. Congreso - Votaciones (PDFs) - `congreso_votaciones.json`

**URL base:** https://www.congreso.gob.pe/votaciones/

**Que extraer:** Los PDFs de resultados de votacion para las 6 leyes pro-crimen identificadas.

**Proceso:**
1. Descargar los PDFs de votacion del Congreso
2. Ejecutar `parse_congreso_pdf.py` para extraer los datos de cada PDF
3. El script genera JSON en el formato de `schemas/congreso_votaciones.json`

**Las 6 leyes pro-crimen a rastrear:**
1. Ley que modifica el codigo penal sobre crimen organizado
2. Ley que limita la colaboracion eficaz
3. Ley que reduce penas por lavado de activos
4. Ley que debilita la extincion de dominio
5. Ley que modifica la prision preventiva
6. Ley que dificulta la persecucion de testaferros

### 3. Convoca - Investigaciones - `convoca_investigaciones.json`

**URL base:** https://convoca.pe

**Que extraer:** Investigaciones periodisticas vinculadas a candidatos.

**Spider output:** Un archivo JSON con un array de investigaciones.
Cada entrada vincula a un candidato con una investigacion o nota periodistica.
Seguir schema en `schemas/convoca_investigaciones.json`.

## Como Ejecutar la Importacion

### Paso 1: Importar candidatos desde Voto Informado
```bash
cd backend
python -m scrapers.import_candidates --input scrapers/data/voto_informado_output.json --output scrapers/data/candidates_validated.json
```

### Paso 2: Parsear PDFs de votaciones del Congreso
```bash
# Para cada PDF descargado:
python -m scrapers.parse_congreso_pdf --input scrapers/data/votacion_001.pdf --output scrapers/data/votacion_001.json

# O procesar todos los PDFs de un directorio:
for pdf in scrapers/data/pdfs/*.pdf; do
  python -m scrapers.parse_congreso_pdf --input "$pdf" --output "${pdf%.pdf}.json"
done
```

### Paso 3: Importar votaciones
```bash
python -m scrapers.import_votaciones --input scrapers/data/votaciones/ --output scrapers/data/votaciones_merged.json
```

### Paso 4: Merge final de todas las fuentes
```bash
python -m scrapers.merge_data \
  --candidates scrapers/data/candidates_validated.json \
  --votaciones scrapers/data/votaciones_merged.json \
  --investigaciones scrapers/data/convoca_output.json \
  --output scrapers/data/candidates_final.json
```

### Paso 5: Cargar datos a la app
```bash
python -m scrapers.load_to_app --input scrapers/data/candidates_final.json
```

## Estructura de Archivos

```
scrapers/
  schemas/                    # JSON Schemas para validar output de spiders
    voto_informado.json
    congreso_votaciones.json
    convoca_investigaciones.json
  data/                       # Aqui van los outputs de los spiders (gitignored)
    pdfs/                     # PDFs descargados del Congreso
  import_candidates.py        # Importa datos de Voto Informado
  import_votaciones.py        # Procesa votaciones del Congreso
  parse_congreso_pdf.py       # Parser de PDFs de votacion
  merge_data.py               # Merge final de todas las fuentes
  load_to_app.py              # Carga datos a la app
  README.md                   # Este archivo
```

## Notas para los Scrapers

- **Encoding:** Todos los archivos JSON deben ser UTF-8.
- **Nombres:** Usar nombres completos tal como aparecen en la fuente, SIN normalizar.
  El merge script se encarga del fuzzy matching.
- **Fechas:** Formato YYYY-MM-DD.
- **Montos:** En soles, como numeros (no strings).
- **Booleanos:** true/false de JSON, no strings.
