# Dataset: Twitter Financial News Sentiment

## Origen

| Atributo | Valor |
|---|---|
| Fuente | Hugging Face Hub — [`zeroshot/twitter-financial-news-sentiment`](https://huggingface.co/datasets/zeroshot/twitter-financial-news-sentiment) |
| Revisión fijada | `ccbe24de388e287beb92dd393a335c376b350ac3` |
| Licencia | MIT |
| Idioma | Inglés |
| Recolección | Tweets de noticias financieras obtenidos con la API de Twitter y anotados manualmente por los autores del dataset |
| Tamaño | 11,931 tweets: 9,543 de `train` y 2,388 de `validation` |
| Clases | 0 = Bearish (bajista), 1 = Bullish (alcista), 2 = Neutral |

> La ficha del Hub indica 9,938 / 2,486 filas, pero los archivos parquet de la revisión fijada
> contienen 9,543 / 2,388. Este proyecto usa las cifras reales de los archivos, registradas en
> `dataset_metadata.json`.

## Archivos

| Archivo | Contenido |
|---|---|
| `twitter_financial_news_sentiment.csv` | Todas las filas de ambas particiones (UTF-8) |
| `twitter_financial_news_sentiment.xlsx` | Hoja `datos` (igual al CSV), hoja `diccionario` (descripción de campos) y hoja `distribucion` (clases por partición) |
| `dataset_metadata.json` | Origen, revisión, fecha de descarga, filas por partición y estadísticas básicas |

## Estructura (diccionario de datos)

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | string | Identificador único generado: `<split>-<índice>` (p. ej. `validation-00042`) |
| `split` | string | Partición original: `train` (entrenamiento) o `validation` (evaluación) |
| `text` | string | Texto original del tweet en inglés, tal como lo publica el dataset |
| `text_clean` | string | Texto tras el ajuste mínimo: sin URLs y con espacios normalizados |
| `label` | int | Etiqueta numérica original: 0 = Bearish, 1 = Bullish, 2 = Neutral |
| `label_name` | string | Etiqueta legible: Bearish, Bullish o Neutral |
| `n_chars` | int | Longitud del tweet original en caracteres (máximo 227) |
| `n_words` | int | Número de palabras del tweet original |
| `has_url` | bool | `True` si el tweet contiene al menos un enlace http(s) (47 % de los tweets) |
| `n_cashtags` | int | Número de cashtags (símbolos bursátiles como `$AAPL`) |

Los campos `id`, `split`, `text` y `label` vienen del dataset original; los demás son derivados
y se calculan en `src/data_utils.py`.

## Distribución de clases

| Partición | Bearish | Bullish | Neutral | Total |
|---|---|---|---|---|
| train | 1,442 (15.1 %) | 1,923 (20.2 %) | 6,178 (64.7 %) | 9,543 |
| validation | 347 (14.5 %) | 475 (19.9 %) | 1,566 (65.6 %) | 2,388 |

El desbalance (~4.5 : 1 entre Neutral y Bearish) es la razón por la que la evaluación usa F1 macro
y recall por clase además de accuracy.

## Cómo se generó (script reproducible)

```bash
# desde la raíz del repositorio, con el entorno activo
python src/download_dataset.py
```

El script (`src/download_dataset.py`):

1. Se autentica en Hugging Face Hub con `HF_TOKEN` (ver `.env.example`).
2. Descarga la revisión fijada con `datasets.load_dataset`.
3. Une ambas particiones, agrega los campos derivados y exporta el CSV, el Excel y los metadatos.

Volver a ejecutarlo genera archivos idénticos, salvo la fecha de descarga en `dataset_metadata.json`.
