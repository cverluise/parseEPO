from google.cloud import bigquery as bq
from wasabi import Printer

msg = Printer()


# TODO doc


def conflict_msg(e, job):
    msg.warn(
        f"JOB ERROR: {e}. This kind of error is usually raised when the destination table already "
        f"exists. If you want to replace the table, execute the same function with "
        f"job_config.write_disposition='WRITE_TRUNCATE'. The query will process "
        f"{int(job.total_bytes_processed / 1e9)}Gb. Otherwise, just use the existing target table. "
        f"table."
    )


def safe_query(query, client, job_config=None):
    """
    A simple wrapper for BQ jobs.
    Return an Error message when the destination table defined in job_config already exists and
    does not execute the query.
    The goal is to avoid large queries generating tables which _already_ exist.
    :param query: str
    :param client: google.cloud.bigquery.client.Client
    :job_config: bq.QueryJobConfig
    """
    job = client.query(query, job_config=job_config)
    if job.error_result:
        if job.error_result["reason"] == "duplicate":
            dry_config = bq.QueryJobConfig(dry_run=True)
            dry_job = client.query(query, job_config=dry_config)
            conflict_msg(job.error_result["reason"], dry_job)
        else:
            print(job.error_result)
    else:
        job.result()


query_famid_nonepo = f"""
SELECT
  DISTINCT(family_id) as family_id
FROM
  `patents-public-data.patents.publications`,
  UNNEST(description_localized) AS description
WHERE
  description.text IS NOT NULL
  AND description.text!=''
  AND description.language="en"
"""


def query_epo_desc_table(src_table: str):
    """
    Return the query generating the aggregate table to compute descriptive statistics on the EPO
    full text database
    :param src_table: str, table path to EPO full-text database on BigQuery e.g.
    'project.dataset.table'
    :return: str
    """
    query = f"""
    WITH
      tmp AS (
      SELECT
        publication_number AS publication_number,
        publication_date,
        title.text IS NOT NULL AS has_title,
        title.LANGUAGE AS title_language,
        abstract.text IS NOT NULL AS has_abstract,
        abstract.LANGUAGE AS abstract_language,
        description.text IS NOT NULL AS has_description,
        description.LANGUAGE AS description_language,
        claims.text IS NOT NULL AS has_claims,
        claims.LANGUAGE AS claims_language,
        amendment.text IS NOT NULL AS has_amendment,
        amendment.LANGUAGE AS amendment_language,
        url.text IS NOT NULL AS has_url,
        url.LANGUAGE AS url_language,
      FROM
        `{src_table}`)
    SELECT
      family_id AS family_id,
      tmp.*
    FROM
      tmp,
      `patents-public-data.patents.publications` AS p
    WHERE
      tmp.publication_number = p.publication_number
    """
    return query


def query_nb_pubnum_epo(src_table):
    return f"""SELECT
      (EXTRACT (YEAR
        FROM
          publication_date)) AS year,
      COUNT(publication_number) AS nb_pubnum
    FROM
      `{src_table}`
    GROUP BY
      year
    ORDER BY
      year DESC"""


def query_nb_full_text_epo(src_table, english_bool=False):
    english_clause = "WHERE description_language LIKE 'en'" if english_bool else ""
    return f"""
    WITH
      tmp AS (
      SELECT
        family_id,
        MIN(EXTRACT(YEAR
          FROM
            publication_date)) AS year,
        SUM(CAST(has_title AS INT64)) > 1 AS has_title,
        SUM(CAST(has_abstract AS INT64)) > 1 AS has_abstract,
        SUM(CAST(has_description AS INT64)) > 1 AS has_description,
        SUM(CAST(has_claims AS INT64)) > 1 AS has_claims,
        SUM(CAST(has_amendment AS INT64)) > 1 AS has_amendment,
        SUM(CAST(has_url AS INT64)) > 1 AS has_url
      FROM
        `{src_table}`
      {english_clause}
      GROUP BY
        family_id )
    SELECT
      year,
      SUM(CAST(has_title AS INT64)) AS nb_has_title,
      SUM(CAST(has_abstract AS INT64)) AS nb_has_abstract,
      SUM(CAST(has_description AS INT64)) AS nb_has_description,
      SUM(CAST(has_claims AS INT64)) AS nb_has_claims,
      SUM(CAST(has_amendment AS INT64)) AS nb_has_amendment,
      SUM(CAST(has_url AS INT64)) AS nb_has_url
    FROM
      tmp
    GROUP BY
      year
    ORDER BY
      year
    """


def query_nb_famid_epo(src_table):
    return f"""
    WITH
      tmp AS (
      SELECT
        family_id,
        MIN(EXTRACT(YEAR
          FROM
            publication_date)) AS year
      FROM
        `{src_table}`
      GROUP BY
        family_id )
    SELECT
      year,
      COUNT(family_id) AS nb_family
    FROM
      tmp
    GROUP BY
      year
    ORDER BY
      year
    """


def query_nb_fam_with_desc_from_nonepo(src_table):
    return f"""
    SELECT
      count(distinct(p.family_id)) as count,
      country_code,
      CAST(publication_date/10000 AS INT64) as year
    FROM
      `patents-public-data.patents.publications` AS p,
      `{src_table}` AS tmp
    WHERE
      tmp.family_id = p.family_id
    GROUP BY
      country_code,
      year
  """


def query_nb_fam_with_desc_from_epo(src_table):
    return f"""
    WITH
      tmp AS (
      SELECT
        family_id,
        SUM(CAST(has_description AS INT64)) > 1 AS fam_has_description
      FROM
        `{src_table}`
      GROUP BY
        family_id )
    SELECT
      COUNT(DISTINCT(p.family_id)) AS count,
      country_code,
      CAST(publication_date/10000 AS INT64) AS year
    FROM
      `patents-public-data.patents.publications` AS p,
      tmp
    WHERE
      tmp.family_id = p.family_id
      AND tmp.fam_has_description
    GROUP BY
      country_code,
      year
    """


query_nb_fam_cnt_yr = """
    SELECT
      COUNT(distinct(p.family_id)) AS count,
      country_code,
      CAST(publication_date/10000 AS INT64) AS year
    FROM
      `patents-public-data.patents.publications` AS p
    GROUP BY
      country_code,
      year"""


def query_famid_en_fulltext(epo_src_table, nonepo_src_table):
    return f"""WITH
      extra_epo AS (
      WITH
        tmp AS (
        SELECT
          family_id,
          SUM(CAST(has_description AS INT64)) > 1 AS fam_has_description
        FROM
          `{epo_src_table}`
        WHERE
          description_language = "en"
        GROUP BY
          family_id )
      SELECT
        tmp.family_id
      FROM
        tmp
      WHERE
        tmp.fam_has_description IS TRUE
        AND tmp.family_id NOT IN (
        SELECT
          family_id
        FROM
          `{nonepo_src_table}`) )
    SELECT
      *
    FROM
      `{nonepo_src_table}`
    UNION ALL
    SELECT
      *
    FROM
      extra_epo"""
