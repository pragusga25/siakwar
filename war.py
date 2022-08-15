import requests
import ssl
import re
from urllib3 import poolmanager
import sys
from termcolor import colored, cprint

class TLSAdapter(requests.adapters.HTTPAdapter):

    def init_poolmanager(self, connections, maxsize, block=False):
        """Create and initialize the urllib3 PoolManager."""
        ctx = ssl.create_default_context()
        ctx.set_ciphers('DEFAULT@SECLEVEL=1')
        self.poolmanager = poolmanager.PoolManager(
                num_pools=connections,
                maxsize=maxsize,
                block=block,
                ssl_version=ssl.PROTOCOL_TLS,
                ssl_context=ctx)

BASE_URL = "https://academic.ui.ac.id/main"
AUTH_URL = f"{BASE_URL}/Authentication/Index"
CHANGEROLE_URL = f"{BASE_URL}/Authentication/ChangeRole"
WELCOME_URL = f"{BASE_URL}/welcome"
UBAH_IRS_URL = f"{BASE_URL}/CoursePlan/CoursePlanEdit"
SAVE_IRS_URL = f"{BASE_URL}/CoursePlan/CoursePlanSave"
CHECK_IRS_URL = f"{BASE_URL}/CoursePlan/CoursePlanViewCheck"

class LoginError(Exception):
    pass

class NoTokensError(Exception):
    pass

creds = { 'u': 'pou.kentang', 'p': 'pass1234567' }

while True:
    try:
        # Login
        print(colored('[+] Logging In...', 'blue'))
        req = requests.Session()
        req.mount('https://', TLSAdapter())
        req.post(AUTH_URL, data=creds)
        req.get(CHANGEROLE_URL)
        r = req.get(WELCOME_URL)
        if 'Logout Counter' not in r.text:
            raise LoginError

        # Get Tokens
        print(colored('[+] Getting a token...', 'blue'))
        r = req.get(UBAH_IRS_URL)
        tokens = re.search('name="tokens" value="\d+"', r.text)
        if not tokens:
            raise NoTokensError
        tokens = tokens.group()
        tokens = tokens.replace('name="tokens" value="', '').replace('"', '')
        print(colored(f'[+] Got a token: {tokens}', 'green'))

        # Choose Courses
        print(colored(f'[+] Prepare to select courses', 'blue'))

        data = dict()
        data['tokens'] = tokens
        data['submit'] = 'Simpan IRS'
        data['comment'] = ''
        # c[<kode MK>_<kurikulum>] = <cc>-<sks>
        data['c[CSGE602012_01.00.12.01-2020]'] = '696042-3'
        data['c[CSGE602012_01.00.12.01-2021]'] = '696042-3'
        data['c[CSGE602012_01.00.12.01-2022]'] = '696042-3'

        req.post(SAVE_IRS_URL, data=data)
        print(colored(f'[+] Courses have been selected', 'green'))

        r = req.get(CHECK_IRS_URL)
        positions = re.findall('Kapasitas \w+: \d+, posisi: \d+', r.text)

        win = 0
        lose = 0

        for pos in positions:
            nums = re.findall('\d+', pos)
            capacity, your_pos = nums
            capacity = int(capacity)
            your_pos = int(your_pos)

            if(your_pos <= capacity): win+=1
            else: lose+=1

            print(colored(f'[+] {pos}', 'yellow'))
        
        color = 'green'
        if lose > win: color = 'red'

        print(colored(f'[+] Win: {win}, Lose: {lose}', color))
        break
    except LoginError:
        print(colored('[!] Login failed', 'red'))
    except NoTokensError:
        print(colored('[!] Siak War has not started yet', 'red'))
    except:
        print(colored('[!] Something went wrong', 'red'))

print(colored('[-] Program has ended', 'blue'))