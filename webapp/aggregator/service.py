from webapp.external_customer_service.service import CustomerExternalService
from webapp.sfcc_service.service import SFCCService

class CustomerAggregator:
    """
    Aggregates and normalizes customer data from external DB and SFCC.
    """

    def __init__(self,
                 external_service: CustomerExternalService = None,
                 sfcc_service: SFCCService = None):
        self.external_service = external_service or CustomerExternalService()
        self.sfcc_service = sfcc_service or SFCCService()

    def fetch_customer(self,
                       email: str = None,
                       customer_no: str = None,
                       goodie_id: str = None,
                       sib_id: str = None) -> dict:
        """
        Fetches raw data, normalizes fields, and returns a dict:
          - external: normalized external data
          - sfcc:     normalized SFCC data
          - events:   raw event-list
        """

        # 1) Hent rå external-data
        raw_ext = self.external_service.fetch_external_customer(
            goodie_id=goodie_id,
            email=email,
            customer_no=customer_no,
            sib_id=sib_id
        ) or {}

        # 2) Normalize external
        external = {
            'first_name':   raw_ext.get('first_name'),
            'last_name':    raw_ext.get('last_name'),
            'goodiecard': str(raw_ext.get('customer_id')) if raw_ext.get('customer_id') is not None else None,
            'email':        raw_ext.get('email'),
            'omneo_id':     raw_ext.get('omneo_id'),
            'customer_no':  raw_ext.get('customer_no'),
            'sib_id':       raw_ext.get('sib_id'),
            'phone_home':   raw_ext.get('phone_home'),
            'phone_mobile': raw_ext.get('phone_mobile'),
            'birthday':     raw_ext.get('birthday'),
        }

        # 3) Hent og normalize SFCC-data
        sfcc = {}
        cust_no = external.get('customer_no')
        if cust_no:
            raw_sfcc = self.sfcc_service.fetch_customer_by_customer_no(cust_no) or {}
            sfcc = {
                'first_name':   raw_sfcc.get('first_name'),
                'last_name':    raw_sfcc.get('last_name'),
                'goodiecard':   raw_sfcc.get('c_goodieCardNumber'),
                'email':        raw_sfcc.get('email'),
                'omneo_id':     raw_sfcc.get('c_omneoMemberID'),
                'customer_no':  raw_sfcc.get('customer_no'),
                'sib_id':       None,
                'phone_home':   raw_sfcc.get('phone_home'),
                'phone_mobile': None,
                'birthday':     raw_sfcc.get('birthday'),
            }

        # 4) Hent events (rå)
        events = self.external_service.fetch_event_log(
            goodie_id=goodie_id,
            customer_no=customer_no or cust_no,
            email=email
        ) or []

        return {
            'external': external,
            'sfcc':     sfcc,
            'events':   events
        }
