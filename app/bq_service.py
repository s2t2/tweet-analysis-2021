from google.cloud import bigquery
from pandas import DataFrame

def split_into_batches(my_list, batch_size=10_000):
    """Splits a list into evenly sized batches"""
    # h/t: https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
    for i in range(0, len(my_list), batch_size):
        yield my_list[i : i + batch_size]

class BigQueryService():
    def __init__(self):
        self.client = bigquery.Client()

    def execute_query(self, sql):
        job = self.client.query(sql)
        return job.result()

    def query_to_df(self, sql):
        records = [dict(row) for row in list(self.execute_query(sql))]
        return DataFrame(records)

    def insert_records_in_batches(self, table, records):
        """
        Inserts records in batches because attempting to insert too many rows at once
            may result in google.api_core.exceptions.BadRequest: 400

        Params:
            table (table ID string, Table, or TableReference)
            records (list of dictionaries)
        """
        rows_to_insert = [list(d.values()) for d in records]
        #errors = self.client.insert_rows(table, rows_to_insert)
        errors = []
        batches = list(split_into_batches(rows_to_insert, batch_size=5_000))
        for batch in batches:
            errors += self.client.insert_rows(table, batch)
        return errors
