# Serialize data

## EPO full-text tsv data limitations

The EP full text data are served in a **tab-separated value** (tsv) format. E.g.

``` tsv
EP	0600083	A1	1994-06-08	de	TITLE	VORRICHTUNG ZUM FÖRDERN UND ORIENTIEREN VON PAPIERBOGEN
EP	0600083	A1	1994-06-08	en	TITLE	DEVICE FOR CONVEYING AND ARRANGING PAPER SHEET
EP	0600083	A1	1994-06-08	fr	TITLE	DISPOSITIF D'ACHEMINEMENT ET DE POSITIONNEMENT DE FEUILLES DE PAPIER
EP	0600083	A1	1994-06-08	en	ABSTR	<p id="pa01" num="0001">A device for conveying ...
EP	0600083	A1	1994-06-08	en	DESCR	<heading id="h0001">Field of Technology</heading><p id="p0001" num="0001">This ...
EP	0600083	A1	1994-06-08	en	CLAIM	<claim id="c-en-0001" num="0001"><claim-text>A paper sheet conveying ...
EP	0600083	A1	1994-06-08	en	PDFEP	https://data.epo.org/publication-server/pdf-document?cc=EP&pn=0600083&ki=A1&pd=1994-06-08
...
```

This comes with two drawbacks:

- Redundant information (e.g. `EP	0600083	A1`)
- Not supported by major big data tools (e.g. BigQuery)

## `ParseEPO`: EPO full-text for humans

We overcome these drawbacks by **serializing** the data. Each patent is represented by a single `json` object with
**nested** fields. E.g.

``` json
{"publication_number": "EP-0600083-A1" ,
 "publication_date": "1994-06-08" ,
 "country_code":["de","en","fr"],
 "title": { "language":["de","en","fr"] ,
            "text":["VORRICHTUNG ZUM FÖRDERN UND ORIENTIEREN VON PAPIERBOGEN\n" ,
                    "DEVICE FOR CONVEYING AND ARRANGING PAPER SHEET\n" ,
                    "DISPOSITIF D'ACHEMINEMENT ET DE POSITIONNEMENT DE FEUILLES DE PAPIER\n"] } ,
 "abstract": {  "text": "<p id=\"pa01\" num=\"0001\">A device for ...",
                "language": "en" } ,
 "claims": { "language":["en"] ,
             "text":["<claim id=\"c-en-0001\" num=\"0001\"><claim-text>A paper ..."] } ,
 "description": { "text": "<heading id=\"h0001\">Field of Technology</heading><p ..." ,
                  "language": "en" } ,
 "url": { "text": "https://data.epo.org/publication-server/pdf-document?cc=EP&pn=0600083&ki=A1&pd=1994-06-08\n" ,
          "language": "en" } ,
 }

```

!!! note
    In this example, variable names have been slightly modified (e.g. `ABSTR` becomes `abstract`). This is meant to align
    variable names with BigQuery patents data standards. You can avoid this behavior by setting `--no-prepare-names` (see **tip:SerializeEPO.py** below.)


## In practice

`SerializeEPO.py` (python CLI) turns the EP **tsv** files into **json newline delimited** files.

``` bash
python  bin/serialize-epo.py \
        --max-workers 2 \
        --verbose \
        --prepare-names \
        "your/folder/EP*.txt"  # "your/folder/EP*.txt.gz" if compressed beforehand
```

!!! tip "SerializeEPO.py"
    Each file is serialized and the output is saved in `your/folder/` as
    `<epo-file-name>.jsonl( .<suffix>)`. Nb: if the original file was compressed (`.gz`), the serialized file will be compressed as well.

    - `--max-workers`: Maximum number of threads allowed
    - `--verbose` / `--no-verbose`: Display info on-going process
    - `--prepare-names` / `--no-prepare-names`: Prepare names in line with BigQuery patents data standards
    - `--handle-html` / `--no-handle-html`: Handle html
    - `--help`: Show this message and exit.
