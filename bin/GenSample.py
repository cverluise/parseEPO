import os
import pickle

import typer
from smart_open import open

from parseepo.utils import get_publication_number


def create_sample_list(file):
    """
    Return the .txt sample
    e.g.    EP  0700059 A1  1996-03-06  de  TITLE   Elektroma ...
            EP  0700059 A1  1996-03-06  en  TITLE   Electroma...
    in a list format
    e.g.    [[['EP','0700059 A1','1996-03-06','de','TITLE',' Elektroma...'],
            ['EP','0700059 A1','1996-03-06','en','TITLE',' Electroma...'],
            ...
    with the following schema [Publication Number[Row[...]]]
    :param file: str, file path (e.g. 'data/sampleEP0600000.txt')
    :return: list
    """
    assert os.path.isfile(file)

    publication_number = ""
    with open(file, "r") as fin:
        data = []
        data_ = []
        for line in fin:
            publication_number_next = get_publication_number(line)
            if publication_number != publication_number_next and data_:
                data += [data_]
                data_ = []
            data_ += [line.split("\t")]
            publication_number = publication_number_next
        data += [data_]
    return data


def main(file: str, dest: str):
    """
    Create and save sample as a list
    :param file: str
    :param dest: str
    """
    list_ = create_sample_list(file)
    pickle.dump(list_, open(dest, "wb"))


if __name__ == "__main__":
    typer.run(main)
