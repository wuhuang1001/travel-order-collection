import requests
from urllib.parse import urlencode, quote
from typing import Dict, Any, Optional, List
import json
from tools import *
import response_decorators

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

    def login_by_code(self, phone: str, code: Optional[str]=None):
        '''
        使用手机号和验证码登录

        Args:
            phone: 手机号
            code: 验证码

        Returns:
            requests.Response: 登录响应
        '''
        # 配置wsgsig是否启用
        enable_wsgsig = True
        wsgsig = ''
        if enable_wsgsig:
            wsgsig = get_wsgsig()
        
        # 如果没有验证码就先获取验证码
        if not code:
            print('正在获取验证码...')
            cod_res = self.send_verification_code_request(phone, wsgsig)
            if cod_res.status_code == 200:    
                    # 在实际应用中，这里可能需要解析响应以确认验证码已发送
                    print('验证码已发送，请检查手机短信')
                    # print(cod_res.text)
            else:
                print('验证码发送失败')
                return None
            code = input('请输入验证码：\n')
        print('正在登录...')
        login_res = self.send_login_request(phone, code, wsgsig)
        return login_res

    

if __name__ == '__main__':
    phone = input('请输入手机号：\n')
    login_res_ = LoginRequest()
    login_res = login_res_.login_by_code(phone)
    print(login_res.text)  # type: ignore

def login():
    login_req = LoginRequest()
    phone = input('请输入手机号：\n')
    login_res = login_req.login_by_code(phone)
    return login_res