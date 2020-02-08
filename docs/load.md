[doc-bqload]:https://cloud.google.com/bigquery/docs/reference/bq-cli-reference#bq_load
[doc-bqload-json]:https://cloud.google.com/bigquery/docs/loading-data-cloud-storage-json
[pypi-bqschemagen]:https://pypi.org/project/bigquery-schema-generator/
[bq-quickstart]:https://cloud.google.com/bigquery/docs/quickstarts/quickstart-web-ui
# Load


BigQuery offers a convenient way to query and analyze large amounts of data.

!!! info
    In case you are new to BigQuery, you might want to:

    - Take the Google BigQuery [Quickstart][bq-quickstart]
    - Learn more on [`bq load`][doc-bqload]

### Data schema

To load a table on BigQuery, you need to specify its schema. `CreateSchema.py` (python CLI) generates this schema for you.
Take care to set the `--prepare-names` / `--no-prepare-names` option to the value set when you serialized the data.

``` bash
python  bin/create-schema.py \
--prepare-names \
path/to/schema.json  # destination file
```

### Load table

!!! tip
    For the sake of efficiency, load the serialized files to a Google Storage bucket beforehand

    ```bash
    gsutil -m cp -r path/to/folder/ gs://your-bucket/
    ```

```bash
bq load --source_format=NEWLINE_DELIMITED_JSON \
--ignore_unknown_values \
--replace \
--max_bad_records=10 \
project:dataset.table \
path/to/EP*.jsonl \ # gs://your-bucket/EP*.jsonl recommended
path/to/schema.json
```
