from ..external_customer_service.service import CustomerExternalService
from ..sfcc_service.service import SFCCService
from ..brevo_service.service import BrevoService

class CustomerAggregator:
    """
    Aggregates and normalizes customer data from External DB, SFCC, and Brevo.
    """
    def __init__(self,
                 external_service: CustomerExternalService = None,
                 sfcc_service:     SFCCService           = None,
                 brevo_service:    BrevoService          = None):
        self.external_service = external_service or CustomerExternalService()
        self.sfcc_service     = sfcc_service     or SFCCService()
        self.brevo_service    = brevo_service    or BrevoService()

    def fetch_customer(self,
                       email:       str = None,
                       customer_no: str = None,
                       goodie_id:   str = None,
                       sib_id:      str = None) -> dict:
        """
        Fetches and normalizes data. Searches by customer_no first,
        then uses returned email to fetch Brevo profile.
        """
        # 1) Fetch from External by customer_no (primary key)
        raw_ext = {}
        if customer_no:
            raw_ext = self.external_service.fetch_external_customer(
                customer_no=customer_no
            ) or {}
        # 2) Determine email from External
        ext_email = raw_ext.get('email')
        # 3) Fetch SFCC if we have customer_no
        raw_sfcc = {}
        if customer_no:
            raw_sfcc = self.sfcc_service.fetch_customer_by_customer_no(customer_no) or {}
        # 4) Fetch Brevo by email
        raw_brevo = {}
        if ext_email:
            raw_brevo = self.brevo_service.fetch_contact(ext_email) or {}

        # Define common fields
        fields = [
            'first_name', 'last_name', 'goodiecard', 'email',
            'omneo_id', 'customer_no', 'sib_id',
            'phone_home', 'phone_mobile', 'birthday'
        ]

        # Normalize External
        external = {key: None for key in fields}
        if raw_ext:
            external.update({
                'first_name':   raw_ext.get('first_name'),
                'last_name':    raw_ext.get('last_name'),
                'goodiecard':   str(raw_ext.get('customer_id')) if raw_ext.get('customer_id') is not None else None,
                'email':        raw_ext.get('email'),
                'omneo_id':     raw_ext.get('omneo_id'),
                'customer_no':  raw_ext.get('customer_no'),
                'sib_id':       raw_ext.get('sib_id'),
                'phone_home':   raw_ext.get('phone_home'),
                'phone_mobile': raw_ext.get('phone_mobile'),
                'birthday':     raw_ext.get('birthday'),
            })

        # Normalize SFCC
        sfcc = {key: None for key in fields}
        if raw_sfcc:
            sfcc.update({
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
            })

        # Normalize Brevo
        brevo = {key: None for key in fields}
        if raw_brevo:
            brevo.update({
                'first_name':   raw_brevo.get('first_name'),
                'last_name':    raw_brevo.get('last_name'),
                'goodiecard':   raw_brevo.get('goodiecard'),
                'email':        raw_brevo.get('email'),
                'omneo_id':     None,
                'customer_no':  raw_brevo.get('customer_no'),
                'sib_id':       raw_brevo.get('sib_id'),
                'phone_home':   raw_brevo.get('phone_home'),
                'phone_mobile': raw_brevo.get('phone_mobile'),
                'birthday':     None,
            })

        # Fetch events
        events = self.external_service.fetch_event_log(
            customer_no=customer_no,
            email=ext_email
        ) or []

        return {
            'external': external,
            'sfcc':     sfcc,
            'brevo':    brevo,
            'events':   events
        }