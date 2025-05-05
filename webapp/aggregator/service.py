# webapp/aggregator/service.py

from sqlalchemy import text
from clients.external_db import ExternalSession

class CustomerAggregatorService:
    """
    Henter kun data fra den eksterne DB (customer-tabellen) og returnerer et dict.
    """
    def fetch_external(self, goodie_id):
        # Definer SQL med parametisering
        stmt = text("""
            -- Basic info for customer
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
            WHERE customer_id = :cid
        """
        )
        # Udfør forespørgsel mod ekstern DB
        with ExternalSession() as session:
            row = session.execute(stmt, {"cid": goodie_id}).mappings().first()
        return dict(row) if row else {}

    def aggregate(self, goodie_id):
        """
        Wrapper for fetch_external så den følger samme interface som tidligere.
        """
        return self.fetch_external(goodie_id)