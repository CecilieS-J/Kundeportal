# webapp/aggregator/service.py

from sqlalchemy import text
from clients.external_db import ExternalSession

class CustomerAggregatorService:
    """
    Henter kun data fra den eksterne DB (customer-tabellen) og returnerer et dict.
    """
    def fetch_external(self, goodie_id=None, email=None, customer_no=None):
        # Base SQL
        sql = """
            SELECT
              jsonb_pretty(data) AS data_pretty,
              customer_id,
              data->>'last_name'    AS last_name,
              data->>'email'        AS email,
              data->>'omneo_id'     AS omneo_id,
              data->>'customer_no'  AS customer_no,
              data->>'sib_id'       AS sib_id,
              data->>'clientela_id' AS clientela_id
            FROM customer
            WHERE 1=1
        """
        params = {}
        if goodie_id:
            sql += " AND data->>'c_goodieCardNumber' = :goodie_id"
            params['goodie_id'] = goodie_id
        if email:
            sql += " AND data->>'email' = :email"
            params['email'] = email
        if customer_no:
            sql += " AND data->>'customer_no' = :customer_no"
            params['customer_no'] = customer_no

        stmt = text(sql)
        with ExternalSession() as session:
            row = session.execute(stmt, params).mappings().first()

        return dict(row) if row else {}

    def aggregate(self, goodie_id=None, email=None, customer_no=None):
        return self.fetch_external(goodie_id, email, customer_no)