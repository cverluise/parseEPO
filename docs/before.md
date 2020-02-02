# Before starting

## Compress data

Both EPO `.txt` files and serailized `.jsonl` files are **uncompressed**. Hence, you can save a significant amount of space by compressing these files.

??? snippet
    ```bash
    gzip your/folder/EP*.*
    ```

!!! warning
    Although `bq load` can handle compressed files, it *cannot* read this type of files **asynchronously**.
    This means that loading the full database from compressed `EP*.jsonl.gz` files will last much longer (around 15 minutes).
    In short, you had better make sure that the database is properly loaded before compressing the `EP*.jsonl` files.


## Check data

### Validate schema

You can validate the json schema of each patent in the `.jsonl` files using the `validate-schema.py` CLI.

If there is an error, it will send a <span style="color:red">Warning</span> with the file name, the line number and
the json object which raised the error.

??? snippet "Validate schema"

    ``` bash
    python bin/validate-schema.py "your/folder/EP*.jsonl"
    ```

### Number of lines by EP0*.jsonl files

You can count the number of lines in the `.jsonl` objects to make sure that the serialization job did not fail silently.

Expected results [here](https://github.com/cverluise/parseEPO/tree/master/io/sanity-checks/nb_lines.csv).


??? snippet "Count lines"
    ``` bash
        for file in $(find you/folder/EP*.jsonl); do
        > echo "$file";
        > wc -l "$file";
        > done
    ```

### Duplicates

There are 954 `publication_number` duplicates. Manual inspection shows that they differ by their publication dates.

???+ snippet "Duplicates"

    ??? snippet "Number of duplicates"
        ``` sql
        WITH tmp AS (
            SELECT
              publication_number,
              COUNT(publication_number) AS count_
            FROM
              `project.dataset.epo_fulltext`
            GROUP BY
              publication_number)
          SELECT
            COUNT(DISTINCT(publication_number)) AS nb_pubnum_duplicates
          FROM
            tmp
          WHERE
            count_>1
        ```

    ??? snippet "Insights on duplicates"
        ``` sql
          WITH
            tmp AS (
            SELECT
              publication_number,
              COUNT(publication_number) AS count_
            FROM
              `project.dataset.epo_fulltext`
            GROUP BY
              publication_number)
          SELECT
            *
          FROM
            tmp
          WHERE
            count_>1)
        SELECT
          dup.publication_number,
          epo.publication_date,
          epo.abstract,
          epo.description,
          epo.title
        FROM
          dup,
          `npl-parsing.external.epo_fulltext` AS epo
        WHERE
          dup.publication_number = epo.publication_number
        ORDER BY
          publication_number
        ```
