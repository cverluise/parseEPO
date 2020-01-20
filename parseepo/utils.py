ATTR_NAMES = {
    "ABSTR": "abstract",
    "DESCR": "description",
    "PDFEP": "url",
    "AMEND": "amendment",
    "CLAIM": "claims",
}
ATTR_NAMES_ = list(ATTR_NAMES.keys())


def get_publication_number(line):
    """
    Return the publication number based on a row from the EPO full-text bulk dataset
    :param line: str, E.g. EP  0700059 A1  1996-03-06  de  TITLE   Elektroma ...
    :return: str, E.g. EP-0700059-A1
    """
    return "-".join(line.split("\t")[:3])


def prepare_name(name: str, prepare_names: bool):
    if prepare_names:
        name = ATTR_NAMES[name] if name in ATTR_NAMES_ else name.lower()
    else:
        pass
    return name
