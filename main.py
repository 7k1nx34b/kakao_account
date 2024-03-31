from kakao import Kakao
import json
import sys
import time


CR = '================================\r'
COUNTRY_CODE = '82'
COUNTRY_ISO = 'KR'
PHONE_NUMBER = ''
NICK_NAME = 'Hello, World!'


# Create - Kakao Account
def main():

    kakao = Kakao()
    kakao.account2_new()
    kakao.account2_terms()

    res = kakao.account2_phone_number(
        country_code=COUNTRY_CODE,
        country_iso=COUNTRY_ISO,
        phone_number=PHONE_NUMBER,
    )

    if res.get('view', None) == None:
        raise Exception('This phone-number is already registered!')
    else:
        print(json.dumps(res, indent=2, ensure_ascii=False))
        print(CR)

        if res['view'] == 'passcode':  # SMS receive Authentication
            res = kakao.account2_passcode(
                passcode=input('passcode: '),
            )
            print(json.dumps(res, indent=2, ensure_ascii=False))
            print(CR)

        elif res['view'] == 'mo-send':
            res = kakao.account2_mo_sent()
            print(json.dumps(res, indent=2, ensure_ascii=False))
            print(CR)

            mo_number = res['viewData']['moNumber']
            mo_message = res['viewData']['moMessage']
            print(mo_number + '\n')
            print(mo_message)

            # Do something via SMS APi e.g twilio

            time.sleep(10)

            res = kakao.account2_mo_confirm()
            print(json.dumps(res, indent=2, ensure_ascii=False))
            print(CR)

    res = kakao.account2_password(
        password=input('password: '),
    )
    print(json.dumps(res, indent=2, ensure_ascii=False))
    print(CR)

    res = kakao.account2_profile(
        nick_name=NICK_NAME,
    )
    print(json.dumps(res, indent=2, ensure_ascii=False))
    print(CR)

    res = kakao.export()
    print('\n' + res)

    sys.exit(0)


if __name__ == '__main__':
    main()
