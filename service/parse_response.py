import json
from typing import Any, Dict, List, Optional, Callable

class ResponseParser:
    '''
    通用响应包解析器
    
    '''
    # class 

    def __init__(
            self,
            custom_handlers: Optional[Dict[str, Callable]] = None,
            separate_metadata: bool = False, 
            is_other_data: bool = True,
            storage_level: str = 'ALL'
        ):
        '''
        初始化解析器

        Args:
            custom_handlers: 自定义字段处理器字典
            separate_metadata: 是否将其他数据存储在字段中
            storage_level: 存储数据的级别
                        - ALL 所有数据都存储在字段中

        '''
        self.separate_metadata = separate_metadata
        self.is_other_data = is_other_data
        # self.storage_level = storage_level
        
        # 基础字段处理器映射
        self.field_handlers = self._create_default_handlers()
        
        # 自定义字段处理器
        self.custom_handlers = custom_handlers or {}
    
    def _create_default_handlers(self) -> Dict[str, Callable]:
        '''创建默认字段处理器'''
        return {
            'errno': self._handle_errno,
            'error': self._handle_error,
            'requestid': self._handle_requestid,
            'traceid': self._handle_traceid,
            'time': self._handle_time,
            'code_type': self._handle_code_type,
            'prompt': self._handle_prompt,
            'ticket': self._handle_ticket,
            'uid': self._handle_uid,
            'suid': self._handle_suid,
            'cell': self._handle_cell,
            'country_id': self._handle_country_id,
            'role': self._handle_role,
            'usertype': self._handle_usertype,
            'data': self._handle_data
        }

    def parse_response(self, response_data: str) -> Dict[str, Any]:
        '''
        解析响应包
        
        Args:
            response_text: 响应包文本，支持json与字典（处理过的响应包）
            
        Returns:
            解析后的数据字典
        '''
        try:

            # 字典
            if isinstance(response_data, dict):
                processe_response_data = response_data
            else:
            # 解析JSON
                processe_response_data = json.loads(response_data.strip())
            result = {}
            
            # 处理每个字段
            for field, value in processe_response_data.items():
                handler = self._get_handler(field)

                # 如果没有处理器，则直接存储字段
                if not handler:
                    if self.is_other_data:
                        result[field] = value
                    continue

                # 使用处理器处理字段
                processe_data = handler(value)

                # 如果处理器返回字典，则存储字段和元数据
                if isinstance(processe_data, dict) and 'value' in processe_data:
                    result[field]=processe_data["value"]
                    if self.separate_metadata:
                        result[f"{field}_meta"] = {key: value  for key, value in processe_data.items() if key != 'value'}
                else:
                    # 处理器返回普通值直接存储
                        result[field] = processe_data
            
            return result
            
        except json.JSONDecodeError as e:
            return {'error': f'JSON解析失败: {str(e)}', 'raw_text': response_data}
        except Exception as e:
            return {'error': f'解析异常: {str(e)}', 'raw_text': response_data}
    
    def _get_handler(self, field: str) -> Optional[Callable]:
        '''获取字段处理器'''
        # 优先使用自定义处理器
        if field in self.custom_handlers:
            return self.custom_handlers[field]
        # 使用基础处理器
        return self.field_handlers.get(field)
    
    def add_custom_handler(self, field: str, handler: Callable):
        '''添加自定义字段处理器'''
        self.custom_handlers[field] = handler
    
    def remove_custom_handler(self, field: str):
        '''移除自定义字段处理器'''
        self.custom_handlers.pop(field, None)
    
    def add_field_handler(self, field: str, handler: Callable):
        '''添加字段处理器（会覆盖已存在的）'''
        self.field_handlers[field] = handler
    
    ''' 
    基础字段处理方法

    要求返回一个字典，必须包含value字段。
    字典的格式为：{'value': field_value, ...}
    '''
    def _handle_errno(self, value):
        return {'value': value, 'type': 'num'}
    
    def _handle_error(self, value):
        return value
    
    def _handle_requestid(self, value):
        return value
    
    def _handle_traceid(self, value):
        return value
    
    def _handle_time(self, value):
        return {'value': value, 'format': 'YYYY-MM-DD HH:MM:SS'}
    
    def _handle_code_type(self, value):
        type_mapping = {0: '正常'}
        return {'value': value, 'type': 'num', 'meaning': type_mapping.get(value, '未知')}
    
    def _handle_ticket(self, value):
        return {'value': value, 'length': len(value), 'first_8_chars': value[:8]}
    
    def _handle_uid(self, value):
        return {'value': value, 'type': 'num', 'uid_str': str(value)}
    
    def _handle_suid(self, value):
        return {'value': value, 'type': 'num', 'suid_str': str(value)}
    
    def _handle_cell(self, value):
        return value
    
    def _handle_country_id(self, value):
        country_mapping = {156: '中国', 1: '美国', 81: '日本'}
        return {'value': value, 'type': 'num', 'country': country_mapping.get(value, '未知')}
    
    def _handle_prompt(self, value):
        return value

    def _handle_role(self, value):
        role_mapping = {0: '普通用户', 1: '管理员', 2: '超级管理员'}
        return {'value': value, 'type':'num', 'meaning': role_mapping.get(value, '未知')}
    
    def _handle_usertype(self, value):
        return {'value': value, 'type': 'num'}

    def _handle_data(self, value):
        return value


# # 使用示例
# def create_parser() -> ResponseParser:
#     '''创建并配置解析器'''
#     parser = ResponseParser()
    
#     # 示例：添加自定义字段处理器
#     def handle_data_field(value):
#         '''处理data字段'''
#         if isinstance(value, dict):
#             result = {}
#             if 'code_len' in value:
#                 result['code_length'] = value['code_len']
#             if 'code_tag' in value:
#                 result['code_tag'] = value['code_tag'].strip('【】')
#             return result
#         return value
    
#     parser.add_custom_handler('data', handle_data_field)
    
#     # 示例：添加新的字段处理器
#     def handle_support_voice(value):
#         return {'value': value, 'meaning': '支持语音' if value else '不支持语音'}
    
#     parser.add_field_handler('support_voice', handle_support_voice)
    
#     return parser


# # 批量处理多个响应包
# def parse_multiple_responses(responses: List[str], parser: ResponseParser = None) -> List[Dict[str, Any]]:
#     '''批量解析多个响应包'''
#     if parser is None:
#         parser = ResponseParser()
    
#     results = []
#     for response in responses:
#         result = parser.parse_response(response)
#         results.append(result)
    
#     return results


# # 快捷函数
# def parse_response(response_text: str, **custom_handlers) -> Dict[str, Any]:
#     '''
#     快捷解析函数
    
#     Args:
#         response_text: 响应包文本
#         **custom_handlers: 自定义处理器
        
#     Returns:
#         解析后的数据
#     '''
#     parser = ResponseParser()
    
#     # 添加临时自定义处理器
#     for field, handler in custom_handlers.items():
#         parser.add_custom_handler(field, handler)
    
#     return parser.parse_response(response_text)