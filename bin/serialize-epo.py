import json
from concurrent.futures import ThreadPoolExecutor
from glob import glob

import typer
from smart_open import open
from tqdm import tqdm
from wasabi import Printer

from parseepo import validate
from parseepo.serialize import serialize_patent
from parseepo.utils import get_publication_number

msg = Printer()


def milestone_msg(nb_patents_serialized, mile=10000):
    if nb_patents_serialized % mile == 0:
        msg.info(f"🎉 {nb_patents_serialized} patents serialized! You are on 🔥")
    else:
        pass


def flush(data, fout, prepare_names, handle_html):
    data_ = serialize_patent(data, prepare_names=prepare_names, handle_html=handle_html)
    fout.write(json.dumps(data_, ensure_ascii=False) + "\n")


def process_epo_file(
    src: str,
    dest: str,
    verbose: bool = False,
    prepare_names: bool = False,
    handle_html: bool = False,
):
    with open(src, "r") as fin:
        with open(dest, "w", encoding="utf-8") as fout:

            # init var
            nb_patents_serialized = 0
            data_ = []
            publication_number = ""

            for line in tqdm(fin):
                publication_number_next = get_publication_number(line)

                if publication_number != publication_number_next and data_:
                    # flush data when the publication_number changes
                    flush(data_, fout, prepare_names, handle_html)
                    data_ = []

                    nb_patents_serialized += 1
                    if verbose:
                        milestone_msg(nb_patents_serialized)

                # split line and append row_ to data_
                row_ = line.split("\t")
                validate.row(row_)
                data_ += [row_]
                publication_number = publication_number_next

            # don't forget the last one
            flush(data_, fout, prepare_names, handle_html)


def main(
    path: str,
    max_workers: int = typer.Option(4, help="Maximum number of threads allowed"),
    verbose: bool = typer.Option(False, help="Display info on-going process"),
    prepare_names: bool = typer.Option(
        False, help="Prepare names in line with BigQuery " "patents data standards"
    ),
    handle_html: bool = typer.Option(False, help="Handle html"),
):
    """
    Process epo full-text files in PATH using multi-threading

    Each file is serialized and the output is saved in the same PATH under <epo-file-name>.jsonl(
    .<suffix>)
    """
    files = glob(path)
    args = (
        (src, src.replace("txt", "jsonl"), verbose, prepare_names, handle_html)
        for src in files
    )
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        executor.map(lambda arg: process_epo_file(*arg), args)


if __name__ == "__main__":
    typer.run(main)
