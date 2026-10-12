"""Download the pinned dataset from the Hugging Face Hub and export it to CSV and Excel.

Usage (from the repository root):
    python src/download_dataset.py

Outputs:
    data/twitter_financial_news_sentiment.csv   all rows, both splits
    data/twitter_financial_news_sentiment.xlsx  sheets: datos, diccionario, distribucion
    data/dataset_metadata.json                  source, revision, sizes and download date
"""

import json
from datetime import datetime, timezone

import pandas as pd

from config import (
    DATA_DIR, DATASET_CSV, DATASET_ID, DATASET_METADATA, DATASET_REVISION, DATASET_XLSX, LABELS,
)
from data_utils import load_splits, to_dataframe
from hub_auth import authenticate


# Human-readable data dictionary, exported as the "diccionario" sheet of the Excel file.
DATA_DICTIONARY = [
    ("id", "string", "Identificador único generado: <split>-<índice> (p. ej. validation-00042)."),
    ("split", "string", "Partición original del dataset: train (entrenamiento) o validation (evaluación)."),
    ("text", "string", "Texto original del tweet en inglés, tal como lo publica el dataset."),
    ("text_clean", "string", "Texto tras el ajuste mínimo: sin URLs y con espacios normalizados."),
    ("label", "int", "Etiqueta numérica original: 0 = Bearish, 1 = Bullish, 2 = Neutral."),
    ("label_name", "string", "Etiqueta legible: Bearish (bajista), Bullish (alcista) o Neutral."),
    ("n_chars", "int", "Longitud del tweet original en caracteres."),
    ("n_words", "int", "Número de palabras del tweet original (separadas por espacios)."),
    ("has_url", "bool", "True si el tweet contiene al menos un enlace http(s)."),
    ("n_cashtags", "int", "Número de cashtags (símbolos bursátiles como $AAPL) en el tweet."),
]


def class_distribution(df: pd.DataFrame) -> pd.DataFrame:
    counts = (
        df.groupby(["split", "label_name"]).size().unstack("label_name")
        .reindex(columns=LABELS).fillna(0).astype(int)
    )
    counts["Total"] = counts.sum(axis=1)
    shares = counts[LABELS].div(counts["Total"], axis=0).mul(100).round(1).add_suffix(" %")
    return pd.concat([counts, shares], axis=1).reset_index()


def main() -> None:
    token = authenticate()
    print(f"Descargando {DATASET_ID} @ {DATASET_REVISION[:8]}…")
    splits = load_splits(token)
    df = to_dataframe(splits)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(DATASET_CSV, index=False, encoding="utf-8")

    dictionary = pd.DataFrame(DATA_DICTIONARY, columns=["campo", "tipo", "descripcion"])
    distribution = class_distribution(df)
    with pd.ExcelWriter(DATASET_XLSX, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="datos", index=False)
        dictionary.to_excel(writer, sheet_name="diccionario", index=False)
        distribution.to_excel(writer, sheet_name="distribucion", index=False)

    metadata = {
        "dataset_id": DATASET_ID,
        "revision": DATASET_REVISION,
        "source_url": f"https://huggingface.co/datasets/{DATASET_ID}",
        "license": "MIT",
        "language": "en",
        "downloaded_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "rows_per_split": {name: len(split) for name, split in splits.items()},
        "label_mapping": {"0": "Bearish", "1": "Bullish", "2": "Neutral"},
        "max_chars": int(df["n_chars"].max()),
        "share_with_url": round(float(df["has_url"].mean()), 4),
    }
    DATASET_METADATA.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Filas totales: {len(df):,}")
    print(distribution.to_string(index=False))
    print(f"CSV   -> {DATASET_CSV.relative_to(DATA_DIR.parent)}")
    print(f"Excel -> {DATASET_XLSX.relative_to(DATA_DIR.parent)}")


if __name__ == "__main__":
    main()
