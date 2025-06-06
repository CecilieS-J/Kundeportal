from ..mdm_service.service import MdmService
from ..sfcc_service.service import SFCCService
from ..brevo_service.service import BrevoService
from ..omneo_service.service import OmneoService

class CustomerAggregator:
    """
    Aggregates and normalizes customer data from MDM, SFCC, Brevo, and Omneo.
    Supports lookup by customer_no, email, goodie_id, or sib_id.
    """
    def __init__(self,
                 mdm_service: MdmService = None,
                 sfcc_service:     SFCCService           = None,
                 brevo_service:    BrevoService          = None,
                 omneo_service:    OmneoService          = None):
        self.mdm_service = mdm_service or MdmService()
        self.sfcc_service     = sfcc_service     or SFCCService()
        self.brevo_service    = brevo_service    or BrevoService()
        self.omneo_service    = omneo_service    or OmneoService()

    def fetch_customer(self,
                       email:       str = None,
                       customer_no: str = None,
                       goodie_id:   str = None,
                       sib_id:      str = None) -> dict:
        """
        Fetch and normalize data in this order:
        1) Use customer_no if provided.
        2) Else use goodie_id.
        3) Else use email.
        4) Else use sib_id.
        Fetch mdm first to obtain customer_no and email for other systems.
        Then fetch SFCC by customer_no, Brevo by email, and Omneo by email or goodiecard.
        """
        # --- MDM lookup ---
        lookup_kwargs = {}
        if customer_no:
            lookup_kwargs['customer_no'] = customer_no
        elif goodie_id:
            lookup_kwargs['goodie_id'] = goodie_id
        elif email:
            lookup_kwargs['email'] = email
        elif sib_id:
            lookup_kwargs['sib_id'] = sib_id

        raw_ext = self.mdm_service.fetch_mdm_customer(**lookup_kwargs) or {}
        customer_no = customer_no or raw_ext.get('customer_no')
        email       = email       or raw_ext.get('email')

        # --- SFCC lookup ---
        raw_sfcc = {}
        if customer_no:
            raw_sfcc = self.sfcc_service.fetch_customer_by_customer_no(customer_no) or {}

        # --- Brevo lookup ---
        raw_brevo = {}
        if email:
            raw_brevo = self.brevo_service.fetch_contact(email) or {}

        # --- Omneo lookup ---
        raw_omneo = {}
        if goodie_id:
            omneo_profiles = self.omneo_service.fetch_by_card_pos(goodie_id)
            raw_omneo = omneo_profiles[0] if omneo_profiles else {}
        elif email:
            omneo_profiles = self.omneo_service.fetch_by_email(email)
            raw_omneo = omneo_profiles[0] if omneo_profiles else {}
            

        # --- Standardized fields ---
        fields = [
            'first_name', 'last_name', 'goodiecard', 'email',
            'omneo_id', 'customer_no', 'sib_id',
            'phone_home', 'phone_mobile'
        ]

        # --- Normalize mdm ---
        mdm = {k: None for k in fields}
        if raw_ext:
            mdm.update({
                'first_name':   raw_ext.get('first_name'),
                'last_name':    raw_ext.get('last_name'),
                'goodiecard':   str(raw_ext.get('customer_id')) if raw_ext.get('customer_id') else None,
                'email':        raw_ext.get('email'),
                'omneo_id':     raw_ext.get('omneo_id'),
                'customer_no':  raw_ext.get('customer_no'),
                'sib_id':       raw_ext.get('sib_id'),
                'phone_home':   raw_ext.get('phone_home'),
                'phone_mobile': raw_ext.get('phone_mobile'),
                
            })

        # --- Normalize SFCC ---
        sfcc = {k: None for k in fields}
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
                
            })

        # --- Normalize Brevo ---
        brevo = {k: None for k in fields}
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
                
            })

        # --- Normalize Omneo ---
        omneo = {k: None for k in fields}
        if raw_omneo:
            identities = { 
                'card_pos':     raw_omneo.get('card_pos'),
                'sfcc_customer': raw_omneo.get('sfcc_customer')
            }
            omneo.update({
                'first_name':    raw_omneo.get('first_name'),
                'last_name':     raw_omneo.get('last_name'),
                'goodiecard':    identities.get('card_pos'),
                'email':         raw_omneo.get('email'),
                'omneo_id':      raw_omneo.get('id'),
                'customer_no':   identities.get('sfcc_customer'),
                'sib_id':        None,
                'phone_home':    None,
                'phone_mobile':  raw_omneo.get('phone'),
                
            })

        # --- Event log ---
        events = self.mdm_service.fetch_event_log(
            customer_no=customer_no,
            email=email
        ) or []

        return {
            'mdm': mdm,
            'sfcc':     sfcc,
            'brevo':    brevo,
            'omneo':    omneo,
            'events':   events
        }
