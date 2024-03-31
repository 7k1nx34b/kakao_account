import secrets
import requests
import uuid
import random
import json
import time
import os


class Kakao:
    def __init__(self) -> None:

        self.ss = ''
        self.duuid = secrets.token_hex(32)
        self.ssaid = secrets.token_hex(20)
        self.adid = str(uuid.uuid4())
        self.c = str(uuid.uuid4())

        self.sess = requests.session()
        self.device_info = f'android/33; uuid={self.duuid}; '  # android/API Level
        # spoof #TODO random?
        self.device_info += f'ssaid={self.ssaid}; model=SM-S918; screen_resolution=3088×1440; sim=45006/1/kr; onestore=false; '
        # https://wiki.melissadata.com/index.php?title=Global_Phone:Premium_and_CallerID_Coverage
        # << sim_operator, network_operator list
        self.fingerprint = {
            'volume': random.randrange(5, 12),  # spoof
            'network_operator': '45006',
            'is_roaming': 'false',
            'va': [],
            'brightness': random.randrange(32, 100),  # spoof
            'totalMemory': 16717008,
            'batteryPct': round(random.random(), 2),  # float, 1=100%  0.5=50% # spoof
            'webviewVersion': '122.0.6261.120',
            'supportMultiSim': True,
            'sims': [
                {
                    'tpn_eq_sim': '',
                    'sim_operator': '45006',
                    'network_operator': '45006',
                    'is_roaming': True,
                    'phone_type': '1',
                    'gid1': '',
                }
            ],
        }
        self.device_info += f'uvc2={json.dumps(self.fingerprint)}'
        self.sess.headers.update(
            {
                'User-Agent': 'KT/10.6.1 An/14 ko',
                'Device-Info': self.device_info,
                'A': 'android/10.6.1/ko',
                'Adid': self.adid,
                'C': self.c,
                'Content-Type': 'application/json',
                'Connection': 'close',
            }
        )
        self.phone_number = ''
        self.password = ''
        self.nick_name = ''
        self.signup_data = {}
        self.oauth_2_token = {}
        self.nonce = ''
        pass

    def account2_new(self) -> dict:  # Set-headers 'Ss'
        r1 = self.sess.get(
            url='https://katalk.kakao.com/android/account2/new',
        )
        self.ss = r1.headers['Set-SS']
        self.sess.headers.update({'Ss': self.ss})

        # print(self.sess.headers)
        return r1.json()

    def account2_terms(self) -> list:  # return ISO code book
        r1 = self.sess.post(
            url='https://katalk.kakao.com/android/account2/terms',
            json={
                'codes': [
                    'IS_OVER_14_YEARS_OLD',
                    'TERM_ACCOUNT',
                    'TERM_KAKAO_UNIFIED',
                    'PR_T_PTC_1904',
                ]
            },
        )
        if os.path.isfile('./iso_code_book.json') == False:
            iso = r1.json()['viewData']['countries']['all']
            with open('./iso_code_book.json', 'w') as fd:
                json.dump(
                    iso,
                    fd,
                    ensure_ascii=False,
                    indent=2,
                )
        '''
        [...]
        {
            'iso':'NI','code':'505','name':'니카라과'
        },
        {
            'iso':'TW','code':'886','name':'대만'
        },
        {
            'iso':'KR','code':'82','name':'대한민국'
        }, 
        [...]
        '''

        return r1.json()

    def account2_phone_number(
        self, phone_number: str, country_code='82', country_iso='KR', method='sms'
    ) -> dict:
        r1 = self.sess.post(
            url='https://katalk.kakao.com/android/account2/phone-number',
            json={
                'countryCode': country_code,
                'countryIso': country_iso,
                'phoneNumber': f'+{country_code}{phone_number}',
                'method': method,
                'termCodes': [],
                'simPhoneNumber': f'+{country_code}{phone_number}',
            },
        )
        self.phone_number = f'+{country_code}{phone_number}'
        return r1.json()

    def account2_passcode(self, passcode: str) -> None:
        r1 = self.sess.post(
            url='https://katalk.kakao.com/android/account2/passcode',
            json={'passcode': passcode},
        )
        return r1.json()

    def account2_mo_sent(self) -> None:
        r1 = self.sess.post(
            url='https://katalk.kakao.com/android/account2/mo-sent',
        )
        return r1.json()

    def account2_mo_confirm(self) -> None:
        r1 = self.sess.post(
            url='https://katalk.kakao.com/android/account2/mo-confirm',
        )
        return r1.json()

    def account2_password(self, password: str) -> dict:
        r1 = self.sess.post(
            url='https://katalk.kakao.com/android/account2/password',
            json={'password': password},
        )
        self.password = password
        return r1.json()

    def account2_profile(self, nick_name: str) -> dict:
        r1 = self.sess.post(
            url='https://katalk.kakao.com/android/account2/profile',
            json={
                'nickname': nick_name,
                'profileImageFlag': 1,
                'friendAutomation': True,
            },
        )
        self.nick_name = nick_name
        self.oauth_2_token = r1.json()['oauth2Token']
        self.signup_data = r1.json()['signupData']
        self.nonce = r1.json()['nonce']
        return r1.json()

    def export(self) -> str:
        path = f'./{self.phone_number}_{round(time.time() * 1000)}.json'
        res = {
            'phone_number': self.phone_number,
            'nick_name': self.nick_name,
            'password': self.password,
            'signup_data': self.signup_data,
            'oauth_2_token': self.oauth_2_token,
            'authorization': self.oauth_2_token['accessToken'] + '-' + self.duuid,
            'nonce': self.nonce,
            'c': self.c,
            'ss': self.ss,
            'duuid': self.duuid,
            'ssaid': self.ssaid,
            'adid': self.adid,
            'fingerprint': self.fingerprint,
        }
        with open(path, 'w') as fd:
            json.dump(
                res,
                fd,
                ensure_ascii=False,
                indent=2,
            )

        return path
