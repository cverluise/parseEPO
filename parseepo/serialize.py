import html2text
import pandas as pd
from wasabi import Printer

from parseepo import validate
from parseepo.exception import SingleAttrException
from parseepo.utils import prepare_name

h = html2text.HTML2Text()
msg = Printer()
NAMES = ["EP", "Num", "Ext", "publication_date", "language", "attr", "text"]
NESTED_ATTR = ["TITLE", "CLAIM", "AMEND", "title", "claims", "amendment"]


def format_patent_df(
    data: list, prepare_names: bool = False, handle_html: bool = False
):
    """
    Return data as a prepared DataFrame from a list of rows
    Nb: Input is [publication_number[Row]].
    E.g. [['EP','0700059 A1','1996-03-06','de','TITLE',' Elektroma...'],
         ['EP','0700059 A1','1996-03-06','en','TITLE',' Electroma...'],
            ...
    :param data: List[List]
    :param prepare_names: bool, True if you want to prepare names for BQ compatibility
    :param handle_html: bool, True if you want to handle html
    :return: pd.DataFrame
             publication_date  language attr    text   publication_number
    0  1996-03-06  ...     ...     ...     EP-0700059-A1
    1  1996-03-06  ...     ...     ...     EP-0700059-A1
    2  1996-03-06  ...     ...     ...     EP-0700059-A1
    3  1996-03-06  ...     ...     ...     EP-0700059-A1
    4  1996-03-06  ...     ...     ...     EP-0700059-A1
    5  1996-03-06  ...     ...     ...     EP-0700059-A1
    6  1996-03-06  ...     ...     ...     EP-0700059-A1
    """

    df_ = pd.DataFrame(data, columns=NAMES)
    df_["publication_number"] = df_["EP"] + "-" + df_["Num"] + "-" + df_["Ext"]
    df_ = df_.drop(["EP", "Num", "Ext"], axis=1)

    if prepare_names:
        df_["attr"] = df_["attr"].apply(lambda x: prepare_name(x, True))
    if handle_html:
        df_["text"] = df_["text"].apply(lambda x: h.handle(x))
    return df_


def unnest_attr(patent_dict: dict, publication_number: str):
    """
    Unnest flat attributes returned as nested by the batch aggregation operation in
    serialize_patent.
    Raises warning if expected flat attributes has multiple values.
    :param patent_dict: dict, returned by serialize_patent
    :param publication_number: str, e.g. 'EP-0600083-A1'
    :return: dict
    In:
    { ...,
    'PDFEP': {'language': ['en'],
           'text': ['https://data.epo.org/publication-server/...']},
           }
    Out:
    {...,
     'PDFEP': 'https://data.epo.org/publication-server/...',}

    """
    attrs = list(filter(lambda x: x not in NESTED_ATTR, patent_dict.keys()))
    for attr in attrs:
        val = patent_dict[attr]["text"]
        try:
            validate.single_attr(val, attr, publication_number)
        except SingleAttrException:
            msg.warn(
                f"{publication_number}: {attr} has more than 1 value. Only the first value "
                f"was kept. Add {attr} to the list NESTED_ATTR to fix this behavior."
            )
        patent_dict.update(
            {
                attr: {
                    "text": patent_dict[attr]["text"][0],
                    "language": patent_dict[attr]["language"][0],
                }
            }
        )


def serialize_patent_df(patent_df: pd.DataFrame):
    """
    Return the serialized patent
    :param patent_df: pd.DataFrame, returned by format_patent_df
    :return: dict
    {'ABSTR': '<p id="pa01" num="0001">A device ...',
     'CLAIM': {'language': ['en'],
               'text': ['<claim id="c-en-0001" ...']},
     'DESCR': '<heading id="h0001">Field of ...',
     'PDFEP': 'https://data.epo.org/publication-server/...',
     'TITLE': {'language': ['de', 'en', 'fr'],
               'text': ['VORRICHTUNG ZUM ...',
                        'DEVICE FOR CONVEYING ...',
                        "DISPOSITIF D'ACHEMINEMENT ...']},
     'publication_date': '1994-06-08',
     'publication_number': 'EP-0600083-A1'}
    """
    publication_number = patent_df["publication_number"].values[0]
    publication_date = patent_df["publication_date"].values[0]

    out = (
        patent_df.drop(["publication_number", "publication_date"], axis=1)
        .groupby("attr")
        .aggregate(list)
        .T.to_dict()
    )

    unnest_attr(out, publication_number)
    out.update({"publication_number": publication_number})
    out.update({"publication_date": publication_date})
    return out


def serialize_patent(
    data: list, prepare_names: bool = False, handle_html: bool = False
):
    """
    Return the serialized patent
    :param data: List[List[str]], E.g.
        [['EP','0700059 A1','1996-03-06','de','TITLE',' Elektroma...'],
         ['EP','0700059 A1','1996-03-06','en','TITLE',' Electroma...'],
    :param prepare_names: bool, True if you want to prepare names for BQ compatibility
    :param handle_html: bool, True if you want to handle html
    :return: dict
    """
    out = format_patent_df(data, prepare_names, handle_html)
    out = serialize_patent_df(out)
    return out
