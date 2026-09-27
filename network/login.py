import requests
from urllib.parse import urlencode, quote
from typing import Dict, Any, Optional, List
import json
from utils.tools import *
from utils.simple_output import info, success, error, normal
# import response_decorators

class LoginRequest:
    # @response_decorators.handle_api_response
    def send_login_request(
            self,
            phone: str,
            code: str,
            wsgsig: str = '',
            appid: int = 30004,
            app_version: str = '2.3.0',
            api_version: str = '1.0.1',
            origin_id: str = '1',
            lang: str = 'zh-CN',
            country_id: int = 156,
            country_calling_code: str = '+86',
            scene: int = 1,
            policy_id_list: Optional[List[int]] = None
        ) -> requests.Response:
        '''
        发送验证码登录POST请求
        /signInByCode
        
        Args:
            phone: 手机号
            code: 验证码
            wsgsig: 签名
            appid: 应用ID
            app_version: 应用版本
            api_version: API版本
            origin_id: 来源ID
            lang: 语言
            country_id: 国家ID
            country_calling_code: 国家区号
            scene: 场景ID
            policy_id_list: 策略ID列表
        
        Returns:
            requests.Response: 响应对象
        '''
        if policy_id_list is None:
            policy_id_list = [50000791]
        
        # 登录请求的URL和路径
        base_url = 'https://epassport.diditaxi.com.cn'
        path = '/passport/login/v5/signInByCode'
        
        # URL查询参数
        params = {}
        if wsgsig:
            params['wsgsig'] = wsgsig
        
        # 构建_referer参数
        referer_params = {
            'h': '1',
            'hash_passport_login': ''
        }
        
        referer_url = f'https://common.diditaxi.com.cn/general/webEntry?{urlencode(referer_params)}'
        
        # POST数据中的q参数
        q_data = {
            'lang': lang,
            '__method__': 'POST',
            'appid': appid,
            'wsgenv': '',
            'policy_id_list': policy_id_list,
            'api_version': api_version,
            'app_version': app_version,
            'origin_id': origin_id,
            '_source': referer_url,
            'role': 1,
            'country_id': country_id,
            'country_calling_code': country_calling_code,
            'scene': scene,
            'lat': 0,
            'lng': 0,
            'cell': phone,
            'code': code,
            'kb_events': '{\'session_id\':\'\',\'kb_width\':100,\'kb_height\':100,\'kb_hit_events\':[]}',
            'kb_session_id': ''
        }
        
        # POST数据
        post_data = {
            'q': json.dumps(q_data, separators=(',', ':'))
        }
        
        # 发送POST请求
        return send_post_request(base_url, path, params, None, post_data)

    # @response_decorators.handle_api_response
    def send_verification_code_request(
            self,
            phone: str,
            wsgsig: str = '',
            appid: int = 30004,
            app_version: str = '2.3.0',
            api_version: str = '1.0.1',
            origin_id: str = '1',
            lang: str = 'zh-CN',
            country_id: int = 156,
            country_calling_code: str = '+86',
            scene: int = 1,
            policy_id_list: Optional[List[int]] = None
        ) -> requests.Response:
        '''
        发送获取验证码POST请求
        
        Args:
            phone: 手机号
            wsgsig: 签名
            appid: 应用ID
            app_version: 应用版本
            api_version: API版本
            origin_id: 来源ID
            lang: 语言
            country_id: 国家ID
            country_calling_code: 国家区号
            scene: 场景ID
            policy_id_list: 策略ID列表
        
        Returns:
            requests.Response: 响应对象
        '''
        if policy_id_list is None:
            policy_id_list = [50000791]
        
        # 获取验证码请求的URL和路径
        base_url = 'https://epassport.diditaxi.com.cn'
        path = '/passport/login/v5/codeMT'

        # URL查询参数
        params = {}
        if wsgsig:
            params['wsgsig'] = wsgsig

        # 构建_referer参数
        enable_referer_params = True
        if not enable_referer_params:
            referer_params ={}
        else:
            referer_params = {
                'h': '1#/?hash_passport_login'
            }

        if enable_referer_params:
            referer_url = f'https://common.diditaxi.com.cn/general/webEntry?{urlencode(referer_params)}'
        else:
            referer_url = f'https://common.diditaxi.com.cn/general/webEntry'
        
        # POST数据中的q参数
        q_data = {
            'lang': lang,
            '__method__': 'POST',
            'appid': appid,
            'wsgenv': '',
            'policy_id_list': policy_id_list,
            'api_version': api_version,
            'app_version': app_version,
            'origin_id': origin_id,
            '_source': referer_url,
            'role': 1,
            'country_id': country_id,
            'country_calling_code': country_calling_code,
            'scene': scene,
            'lat': 0,
            'lng': 0,
            'cell': f'{phone}',
            'kb_events': '{\'session_id\':\'\',\'kb_width\':100,\'kb_height\':100,\'kb_hit_events\':[]}',
            'kb_session_id': ''
        }
        
        # POST数据
        post_data = {
            'q': json.dumps(q_data, separators=(',', ':'))
        }
        
        # 发送POST请求
        return send_post_request(base_url, path, params, None, post_data)

    # 验证码最多允许尝试的次数
    MAX_CODE_ATTEMPTS = 3

    @staticmethod
    def parse_login_response(response: requests.Response) -> Optional[Dict[str, Any]]:
        '''
        解析登录响应体

        Args:
            response: 登录接口响应

        Returns:
            Dict: 解析后的字典；响应不是合法 JSON 对象时返回 None
        '''
        try:
            data = json.loads(response.text.strip())
        except (ValueError, AttributeError):
            return None
        return data if isinstance(data, dict) else None

    @staticmethod
    def is_login_success(data: Optional[Dict[str, Any]]) -> bool:
        '''
        判断登录响应是否成功

        服务端即使登录失败也会返回 HTTP 200，必须通过 errno 与 ticket 判断，
        否则会把失败响应当成成功，导致后续解析 ticket 时抛出 KeyError。
        '''
        return bool(data) and data.get('errno') == 0 and bool(data.get('ticket'))

    @staticmethod
    def login_error_reason(data: Optional[Dict[str, Any]]) -> str:
        '''
        从失败的登录响应中提取给用户看的错误原因
        '''
        if not isinstance(data, dict):
            return '服务器返回内容无法解析'
        for key in ('error', 'errmsg', 'prompt', 'message'):
            value = data.get(key)
            if value:
                return str(value)
        errno = data.get('errno')
        return f'未知错误（errno={errno}）' if errno is not None else '未知错误'

    def send_verification_code(self, phone: str, wsgsig: str) -> bool:
        '''
        请求短信验证码

        Args:
            phone: 手机号
            wsgsig: 签名

        Returns:
            bool: 是否发送成功
        '''
        info('正在获取验证码...')
        code_res = self.send_verification_code_request(phone, wsgsig)
        if code_res.status_code == 200:
            success('验证码已发送，请检查手机短信')
            return True
        error(f'验证码发送失败（HTTP {code_res.status_code}），请稍后重试')
        return False

    @staticmethod
    def prompt_code() -> str:
        '''
        读取用户输入的验证码，空输入时重新提示
        '''
        while True:
            code = input('请输入验证码：\n').strip()
            if code:
                return code
            error('验证码不能为空，请重新输入')

    def login_by_code(self, phone: str, code: Optional[str]=None, max_attempts: int = MAX_CODE_ATTEMPTS):
        '''
        使用手机号和验证码登录

        验证码错误时不会直接报错退出，而是提示服务端返回的错误原因并允许重新输入，
        超过 max_attempts 次后返回 None，由调用方决定后续处理。

        Args:
            phone: 手机号
            code: 验证码，为空时先请求短信验证码
            max_attempts: 验证码最多尝试次数

        Returns:
            requests.Response: 登录成功的响应；失败返回 None
        '''
        # 配置wsgsig是否启用
        enable_wsgsig = True
        wsgsig = ''
        if enable_wsgsig:
            wsgsig = get_wsgsig()

        # 如果没有验证码就先获取验证码
        if not code:
            if not self.send_verification_code(phone, wsgsig):
                return None
            code = self.prompt_code()

        for attempt in range(1, max_attempts + 1):
            info('正在登录...')
            login_res = self.send_login_request(phone, code, wsgsig)

            if login_res.status_code != 200:
                error(f'登录请求失败（HTTP {login_res.status_code}），请稍后重试')
                return None

            data = self.parse_login_response(login_res)
            if self.is_login_success(data):
                return login_res

            error(f'登录失败：{self.login_error_reason(data)}')

            remaining = max_attempts - attempt
            if remaining <= 0:
                error(f'验证码已连续错误 {max_attempts} 次，本次登录终止')
                return None

            normal(f'请重新输入验证码（剩余 {remaining} 次机会，直接回车可重新获取验证码）')
            code = input('请输入验证码：\n').strip()
            if not code:
                if not self.send_verification_code(phone, wsgsig):
                    return None
                code = self.prompt_code()

        return None

    

if __name__ == '__main__':
    phone = input('请输入手机号：\n')
    login_res_ = LoginRequest()
    login_res = login_res_.login_by_code(phone)
    if login_res is not None:
        print(login_res.text)  # type: ignore
    else:
        print('登录失败')

def login():
    login_req = LoginRequest()
    phone = input('请输入手机号：\n')
    login_res = login_req.login_by_code(phone)
    return login_res