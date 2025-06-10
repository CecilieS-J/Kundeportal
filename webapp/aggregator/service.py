from ..mdm_service.service import MdmService
from ..sfcc_service.service import SFCCService
from ..brevo_service.service import BrevoService
from ..omneo_service.service import OmneoService
from concurrent.futures import ThreadPoolExecutor
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CustomerAggregator:
    """
    Aggregates and normalizes customer data from MDM, SFCC, Brevo, and Omneo.
    Supports lookup by customer_no, email, goodie_id, or sib_id.
    """
    def __init__(self,
                 mdm_service: MdmService = None,
                 sfcc_service: SFCCService = None,
                 brevo_service: BrevoService = None,
                 omneo_service: OmneoService = None):
        self.mdm_service = mdm_service or MdmService()
        self.sfcc_service = sfcc_service or SFCCService()
        self.brevo_service = brevo_service or BrevoService()
        self.omneo_service = omneo_service or OmneoService()

    def fetch_customer(self,
                       email: str = None,
                       customer_no: str = None,
                       goodie_id: str = None,
                       sib_id: str = None) -> dict:
        """
        Fetch and normalize data in this order:
        1) Use customer_no if provided.
        2) Else use goodie_id.
        3) Else use email.
        4) Else use sib_id.
        Fetch mdm first to obtain customer_no and email, then fetch other systems in parallel.
        """
        start_time = time.time()

        # --- MDM lookup (must be sequential to get customer_no and email) ---
        lookup_kwargs = {}
        if customer_no:
            lookup_kwargs['customer_no'] = customer_no
        elif goodie_id:
            lookup_kwargs['goodie_id'] = goodie_id
        elif email:
            lookup_kwargs['email'] = email
        elif sib_id:
            lookup_kwargs['sib_id'] = sib_id

        mdm_start = time.time()
        raw_ext = self.mdm_service.fetch_mdm_customer(**lookup_kwargs) or {}
        logger.info(f"MDM fetch took {time.time() - mdm_start:.2f} seconds")
        
        customer_no = customer_no or raw_ext.get('customer_no')
        email = email or raw_ext.get('email')

        # --- Define functions for parallel execution ---
        def fetch_sfcc():
            if customer_no:
                sfcc_start = time.time()
                result = self.sfcc_service.fetch_customer_by_customer_no(customer_no) or {}
                logger.info(f"SFCC fetch took {time.time() - sfcc_start:.2f} seconds")
                return result
            return {}

        def fetch_brevo():
            if email:
                brevo_start = time.time()
                result = self.brevo_service.fetch_contact(email) or {}
                logger.info(f"Brevo fetch took {time.time() - brevo_start:.2f} seconds")
                return result
            return {}

        def fetch_omneo():
            omneo_start = time.time()
            if goodie_id:
                profiles = self.omneo_service.fetch_by_card_pos(goodie_id)
                result = profiles[0] if profiles else {}
            elif email:
                profiles = self.omneo_service.fetch_by_email(email)
                result = profiles[0] if profiles else {}
            else:
                result = {}
            logger.info(f"Omneo fetch took {time.time() - omneo_start:.2f} seconds")
            return result

        # --- Parallel execution ---
        with ThreadPoolExecutor(max_workers=3) as executor:
            sfcc_future = executor.submit(fetch_sfcc)
            brevo_future = executor.submit(fetch_brevo)
            omneo_future = executor.submit(fetch_omneo)
            raw_sfcc = sfcc_future.result()
            raw_brevo = brevo_future.result()
            raw_omneo = omneo_future.result()

        # --- Event log (sequential due to dependency on customer_no/email) ---
        # event_start = time.time()
        # events = self.mdm_service.fetch_event_log(
        #     customer_no=customer_no,
        #     email=email
        # ) or []
        # logger.info(f"Event log fetch took {time.time() - event_start:.2f} seconds")

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
                'first_name': raw_ext.get('first_name'),
                'last_name': raw_ext.get('last_name'),
                'goodiecard': str(raw_ext.get('customer_id')) if raw_ext.get('customer_id') else None,
                'email': raw_ext.get('email'),
                'omneo_id': raw_ext.get('omneo_id'),
                'customer_no': raw_ext.get('customer_no'),
                'sib_id': raw_ext.get('sib_id'),
                'phone_home': raw_ext.get('phone_home'),
                'phone_mobile': raw_ext.get('phone_mobile'),
            })

        # --- Normalize SFCC ---
        sfcc = {k: None for k in fields}
        if raw_sfcc:
            sfcc.update({
                'first_name': raw_sfcc.get('first_name'),
                'last_name': raw_sfcc.get('last_name'),
                'goodiecard': raw_sfcc.get('c_goodieCardNumber'),
                'email': raw_sfcc.get('email'),
                'omneo_id': raw_sfcc.get('c_omneoMemberID'),
                'customer_no': raw_sfcc.get('customer_no'),
                'sib_id': None,
                'phone_home': raw_sfcc.get('phone_home'),
                'phone_mobile': None,
            })

        # --- Normalize Brevo ---
        brevo = {k: None for k in fields}
        if raw_brevo:
            brevo.update({
                'first_name': raw_brevo.get('first_name'),
                'last_name': raw_brevo.get('last_name'),
                'goodiecard': raw_brevo.get('goodiecard'),
                'email': raw_brevo.get('email'),
                'omneo_id': None,
                'customer_no': raw_brevo.get('customer_no'),
                'sib_id': raw_brevo.get('sib_id'),
                'phone_home': raw_brevo.get('phone_home'),
                'phone_mobile': raw_brevo.get('phone_mobile'),
            })

        # --- Normalize Omneo ---
        omneo = {k: None for k in fields}
        if raw_omneo:
            identities = {
                'card_pos': raw_omneo.get('card_pos'),
                'sfcc_customer': raw_omneo.get('sfcc_customer')
            }
            omneo.update({
                'first_name': raw_omneo.get('first_name'),
                'last_name': raw_omneo.get('last_name'),
                'goodiecard': identities.get('card_pos'),
                'email': raw_omneo.get('email'),
                'omneo_id': raw_omneo.get('id'),
                'customer_no': identities.get('sfcc_customer'),
                'sib_id': None,
                'phone_home': None,
                'phone_mobile': raw_omneo.get('phone'),
            })

        total_time = time.time() - start_time
        logger.info(f"Total fetch_customer took {total_time:.2f} seconds")

        return {
            'mdm': mdm,
            'sfcc': sfcc,
            'brevo': brevo,
            'omneo': omneo,
            #'events': events
        }

    def find_differences(self, brevo: dict, mdm: dict, omneo: dict, sfcc: dict) -> list:
        """
        Find differences between brevo, mdm, omneo, and sfcc datasets for each field.
        Excludes unsupported fields and the 'birthday' field.
        """
        unsupported = {
            'brevo': ['omneo_id'],
            'mdm': [],
            'omneo': ['sib_id', 'phone_home'],
            'sfcc': ['sib_id', 'phone_mobile']
        }

        keys = [k for k in mdm.keys() if k not in ['data_pretty', 'birthday']]
        for sys in ['brevo', 'omneo', 'sfcc']:
            sys_data = brevo if sys == 'brevo' else omneo if sys == 'omneo' else sfcc
            for key in sys_data.keys():
                if key not in keys and key != 'birthday':
                    keys.append(key)

        diffs = []
        for key in keys:
            vals = []
            if key not in unsupported['brevo']:
                vals.append(brevo.get(key))
            if key not in unsupported['mdm']:
                vals.append(mdm.get(key))
            if key not in unsupported['omneo']:
                vals.append(omneo.get(key))
            if key not in unsupported['sfcc']:
                vals.append(sfcc.get(key))

            uniq = []
            for v in vals:
                vs = '' if v is None else str(v)
                if vs and vs not in uniq:
                    uniq.append(vs)

            if len(uniq) > 1:
                diffs.append({
                    'field': key,
                    'brevo': '' if brevo.get(key) is None else str(brevo.get(key)),
                    'mdm': '' if mdm.get(key) is None else str(mdm.get(key)),
                    'omneo': '' if omneo.get(key) is None else str(omneo.get(key)),
                    'sfcc': '' if sfcc.get(key) is None else str(sfcc.get(key))
                })

        return diffs

# Optional caching setup (requires flask-caching)
# from flask_caching import Cache
# cache = Cache()
# def init_cache(app):
#     cache.init_app(app, config={'CACHE_TYPE': 'simple'})
# @cache.memoize(timeout=300)  # Cache for 5 minutes
# def fetch_customer(self, email: str = None, customer_no: str = None, goodie_id: str = None, sib_id: str = None) -> dict:
#     ... (rest of the method)