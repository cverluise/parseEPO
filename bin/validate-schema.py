import json
from glob import glob

import typer
from jsonschema import validate
from smart_open import open
from tqdm import tqdm
from wasabi import Printer

from parseepo.utils import prepare_name


def schema(prepare_names: bool = False):
    return {
        "type": "object",
        "properties": {
            "publication_number": {"type": "string"},
            "publication_date": {"type": "string"},
            prepare_name("ABSTR", prepare_names): {
                "items": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string"},
                        "language": {"type": "string"},
                    },
                }
            },
            prepare_name("DESCR", prepare_names): {
                "items": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string"},
                        "language": {"type": "string"},
                    },
                }
            },
            prepare_name("AMEND", prepare_names): {
                "items": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "array"},
                        "language": {"type": "array"},
                    },
                }
            },
            prepare_name("CLAIM", prepare_names): {
                "items": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "array"},
                        "language": {"type": "array"},
                    },
                }
            },
            prepare_name("PDFEP", prepare_names): {
                "items": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string"},
                        "language": {"type": "string"},
                    },
                }
            },
        },
    }


def main(
    path: str,
    prepare_names: bool = typer.Option(
        False, help="Prepare names in line with BigQuery " "patents data standards"
    ),
):
    files = glob(path)
    schema_ = schema(prepare_names=prepare_names)
    msg = Printer()
    for file in files:
        with open(file) as fin:
            for i, line in tqdm(enumerate(fin)):
                row = json.loads(line)
                try:
                    validate(row, schema_)
                except Exception as e:
                    msg.warn(e, text=f"FILE: {file}\nLINE: {i}\nROW: {row}")


if __name__ == "__main__":
    typer.run(main)
