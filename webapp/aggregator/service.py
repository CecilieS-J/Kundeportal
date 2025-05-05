# webapp/aggregator/service.py

from sqlalchemy import text
from clients.external_db import ExternalSession

class CustomerAggregatorService:
    """
    Henter kun data fra den eksterne DB (customer-tabellen) og returnerer et dict.
    """
    def fetch_external(self,
                       goodie_id=None,
                       email=None,
                       customer_no=None,
                       sib_id=None,
                       phone=None):
        sql = """
            SELECT
              jsonb_pretty(data)       AS data_pretty,
              customer_id,
              data->>'last_name'       AS last_name,
              data->>'email'           AS email,
              data->>'omneo_id'        AS omneo_id,
              data->>'customer_no'     AS customer_no,
              data->>'sib_id'          AS sib_id,
              data->>'phone_home'      AS phone_home,
              data->>'phone_mobile'    AS phone_mobile,
              data->>'phone_business'  AS phone_business,
              data->>'clientela_id'    AS clientela_id
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
            sql += """
              AND ltrim(data->>'customer_no','0')
                  = ltrim(:customer_no,'0')
            """
            params['customer_no'] = customer_no
        if sib_id:
            sql += " AND data->>'sib_id' = :sib_id"
            params['sib_id'] = sib_id
        if phone:
            sql += """
              AND (
                data->>'phone_home'   = :phone OR
                data->>'phone_mobile' = :phone OR
                data->>'phone_business' = :phone
              )
            """
            params['phone'] = phone

        stmt = text(sql)
        with ExternalSession() as session:
            row = session.execute(stmt, params).mappings().first()
        return dict(row) if row else {}

    def aggregate(self, **kwargs):
        return self.fetch_external(**kwargs)