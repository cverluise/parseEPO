[gs-quickstart]:https://cloud.google.com/storage/docs/quickstarts-console
[poetry]:https://python-poetry.org/

# Set up

## Google Cloud Platform

To get access to the data you need:

* [x] A Google Cloud Platform (GCP) account
* [x] A GCP project with enabled billing


!!! info
    In case you are new to GCP and want to learn the basics of Google Storage (the storage service of GCP), you can take the
    Google Storage [Quickstart][gs-quickstart]. This should not take more than 2 minutes and might help a lot !

## Parse EPO

* [x] Clone the repository

``` bash
git clone  https://github.com/cverluise/parseEPO.git
```

* [x] Install requirements

``` bash tab="poetry"
cd parseEPO/
poetry install
```

``` bash tab="requirements.txt"
# create and activate virtual environment first
cd parseEPO/
pip install -r requirements.txt
```

!!! tip "poetry - Recommended!"
    [Poetry][poetry] is a tool for dependency management and packaging in Python. It guarantees that all dependencies and sub-dependencies
    are exactly the same as those of the initial project. It also manages the virtual environment for you.
