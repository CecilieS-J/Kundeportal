# webapp/aggregator/service.py

from sqlalchemy import text
from clients.external_db import ExternalSession

class CustomerExternalService:
    """
    Retrieves data from the external database (customer table) and returns it as a dictionary.
    """
    def fetch_external(self,
                       goodie_id=None,
                       email=None,
                       customer_no=None,
                       sib_id=None):
        sql = """
            SELECT
              jsonb_pretty(data)       AS data_pretty,
              customer_id,
              data->>'first_name'      AS First_name,
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

        stmt = text(sql)
        with ExternalSession() as session:
            row = session.execute(stmt, params).mappings().first()
        return dict(row) if row else {}

    def fetch_external_customer(self, **kwargs):
        return self.fetch_external(**kwargs)
    
    

    def fetch_event_log(self, goodie_id=None, customer_no=None, email=None):
         # Determine which parameter to use in WHERE clause
        if goodie_id:
            where = "event_data->>'c_goodieCardNumber' = :val"
            val   = goodie_id
        elif customer_no:
            where = "event_data->>'customer_no' = :val"
            val   = customer_no
        elif email:
            where = "event_data->>'email' = :val"
            val   = email
        else:
            return []

        sql = f"""
            SELECT
              event_id,
              ts                             AS timestamp,
              type::text                     AS type,       -- cast enum to text
              src_system::text               AS system,     -- also cast enum to text
              event_data->>'email'           AS email,
              event_data->>'first_name'            AS First_name,
              event_data                     AS data_json
            FROM "event"
            WHERE {where}
            ORDER BY ts DESC
        """
        stmt = text(sql)
        with ExternalSession() as session:
            rows = session.execute(stmt, {"val": val}).mappings().all()

        return [dict(r) for r in rows]
