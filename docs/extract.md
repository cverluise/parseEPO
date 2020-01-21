[gs-quickstart-gsutil]:https://cloud.google.com/storage/docs/quickstart-gsutil
[requester-pays]:https://cloud.google.com/storage/docs/using-requester-pays
[epo-bulk]:https://console.cloud.google.com/storage/browser/epo-patentinformation/
[doc-gcsfuse]:https://cloud.google.com/storage/docs/gcs-fuse
# Extract data

## Preview with the Google Storage User Interface (optional)

Navigate to the [epo-patentinformation bucket][epo-bulk] to have a preview of the dataset.

!!! warning
    The total size of the bulk data exceeds 200Gb. Do not even think about downloading the full dataset using the UI.
    It will fail.

## Download the dataset with `gsutil`

To download the EPO bulk dataset using the console:

* [x] Install `gsutil`, the google cloud Command Line Interface (CLI) to interact with Google Storage. [Quickstart and Installation guide][gs-quickstart-gsutil].
* [x] Download the dataset to `your/destination/folder`

``` bash hl_lines="1"
gsutil  -u <your-billing-project> \
        -m cp -r gs://epo-patentinformation/ \
        <your/destination/folder>
```

!!! tip
    - The EPO dataset is made of **uncompressed** `.txt` files. Hence, you can divide its size 5-folds by compressing `.txt` files
    in `.gz` files. Execute `gzip your/destination/folder/EP*.txt`. Note: the rest of the pipeline supports `.gz` files natively.
    - If you are a frequent user of the Google Cloud Platform, you can set `your/destination/folder` to a Google Storage bucket.
    The rest of the pipeline can be executed from a **compute instance** with the **bucket mounted**, see [`gcsfuse`][doc-gcsfuse] instructions.
