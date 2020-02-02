import os

import typer
from google.cloud import bigquery as bq
from google.cloud.bigquery import SchemaField
from wasabi import Printer

from parseepo.utils import prepare_name

msg = Printer()


def main(
    dest: str,
    prepare_names: bool = typer.Option(
        False, help="Prepare names in line with BigQuery " "patents data standards"
    ),
):
    schema_list = [
        SchemaField(
            "publication_number",
            "STRING",
            "NULLABLE",
            description="DOCDB publication number",
        ),
        SchemaField(
            "publication_date",
            "DATE",
            "NULLABLE",
            description="Publication date of the EP patent",
        ),
        SchemaField(
            prepare_name("PDFEP", prepare_names),
            "RECORD",
            "NULLABLE",
            description="Url link to the pdf of the " "EP patent",
            fields=(
                SchemaField(
                    "language", "STRING", "NULLABLE", description="Language of the pdf"
                ),
                SchemaField("text", "STRING", "NULLABLE", description="Url"),
            ),
        ),
        SchemaField(
            prepare_name("TITLE", prepare_names),
            "RECORD",
            "NULLABLE",
            description="Title of the patent",
            fields=(
                SchemaField(
                    "language", "STRING", "REPEATED", description="Title language"
                ),
                SchemaField(
                    "text", "STRING", "REPEATED", description="Localized title"
                ),
            ),
        ),
        SchemaField(
            prepare_name("ABSTR", prepare_names),
            "RECORD",
            "NULLABLE",
            description="Abstract of the patent",
            fields=(
                SchemaField(
                    "language", "STRING", "NULLABLE", description="Abstract language"
                ),
                SchemaField(
                    "text", "STRING", "NULLABLE", description="Localized abstract"
                ),
            ),
        ),
        SchemaField(
            prepare_name("DESCR", prepare_names),
            "RECORD",
            "NULLABLE",
            description="Description of the patent",
            fields=(
                SchemaField(
                    "language",
                    "STRING",
                    "NULLABLE",
                    description="Language of the description",
                ),
                SchemaField(
                    "text", "STRING", "NULLABLE", description="Localized description"
                ),
            ),
        ),
        SchemaField(
            prepare_name("CLAIM", prepare_names),
            "RECORD",
            "NULLABLE",
            description="Claims of patent",
            fields=(
                SchemaField(
                    "language", "STRING", "REPEATED", description="Claims language"
                ),
                SchemaField(
                    "text", "STRING", "REPEATED", description="Localized claims"
                ),
            ),
        ),
        SchemaField(
            prepare_name("AMEND", prepare_names),
            "RECORD",
            "NULLABLE",
            description="Amendments",
            fields=(
                SchemaField(
                    "language", "STRING", "REPEATED", description="Amendments language"
                ),
                SchemaField(
                    "text", "STRING", "REPEATED", description="Localized amendments"
                ),
            ),
        ),
    ]

    bq.Client().schema_to_json(schema_list=schema_list, destination=dest)
    if os.path.isfile(dest):
        msg.good(f"Schema successfully generated and saved to {dest}.")


if __name__ == "__main__":
    typer.run(main)
