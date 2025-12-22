import requests

'''
装饰器文件

待使用
'''


class ResponseHandler:
    '''通用响应处理器'''
    
    @staticmethod
    def check_success(response: requests.Response) -> bool:
        '''检查请求是否成功'''
        return response.status_code == 200
    
    @staticmethod
    def get_json_safe(response: requests.Response, default=None):
        '''安全获取JSON数据'''
        try:
            return response.json()
        except ValueError:
            return default
    
    @staticmethod
    def log_response(response: requests.Response, prefix=''):
        '''记录响应日志'''
        print(f'{prefix}状态码: {response.status_code}')
        print(f'{prefix}响应头: {dict(response.headers)}')
        print(f'{prefix}响应内容: {response.text}')
        return response
    
    @staticmethod
    def handle_common_errors(response: requests.Response):
        '''处理通用错误'''
        if response.status_code >= 500:
            raise Exception(f'服务器错误: {response.status_code}')
        elif response.status_code == 404:
            raise Exception('接口不存在')
        return response

# response_decorators.py
def handle_api_response(func):
    '''API响应处理装饰器'''
    def wrapper(*args, **kwargs):
        try:
            response = func(*args, **kwargs)
            
            # 通用响应处理
            print(f'API: {func.__name__}')
            print(f'状态码: {response.status_code}')
            print(f'响应: {response.text[:200]}...')
            
            # 检查HTTP状态
            if response.status_code != 200:
                return {
                    'success': False,
                    'error_type': 'http_error',
                    'status_code': response.status_code,
                    'message': f'HTTP错误: {response.status_code}'
                }
            
            # 尝试解析JSON
            try:
                json_data = response.json()
                return {
                    'success': True,
                    'data': json_data,
                    'raw_response': response.text
                }
            except ValueError:
                return {
                    'success': False,
                    'error_type': 'parse_error',
                    'message': '响应不是有效的JSON格式',
                    'raw_response': response.text
                }
                
        except requests.RequestException as e:
            return {
                'success': False,
                'error_type': 'request_error',
                'message': f'请求异常: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error_type': 'unknown_error',
                'message': f'未知错误: {str(e)}'
            }
    
    return wrapper
