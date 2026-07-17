    def check_sso_login(username, password):
        if username and password:
            try:
                api_request = {
                    'requestSystem': 'NANZI_API_DATA_PLATFORM',
                    'requestBusiness': 'USER-LOGIN',
                    'operationType': 'LOGIN',
                    'userName': username,
                    'password': password
                }

                headers = dict()
                headers['YOVOLE-LAPLACE-API-ACCESS-TOKEN'] = 'laplace'
                headers['Content-Type'] = 'application/json;charset=UTF-8'
                api_url = 'https://yovole.net/api/v1/user/check/login'

                resp = requests.post(url=api_url, headers=headers, data=json.dumps(api_request), timeout=30000,
                                     verify=False)
                if resp.status_code == 200:
                    response = json.loads(resp.content)
                    return response.get('data', False)
            except Exception as e:
                logger.error("auth_user error£º%s" % e)
        return False