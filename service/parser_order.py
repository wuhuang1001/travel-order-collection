from typing import Dict, Any, Optional, Callable
from utils.tools import send_get_request
# from response_decorators import handle_api_response
import time
from service.parse_response import ResponseParser
from network.history import *
import json


class ParserOrderHistoryList:
    """
    订单历史列表解析器类
    用于解析订单历史列表的响应数据，提取订单相关信息
    """
    
    # TODO 继续完成 1.增加get必要参数的函数 2.合并所有必要参数到新函数get_req_params 3.完善注释 4.清除空值
    def parse_order_history_order_done(self, response_text: str) -> Dict[str, Any]:
        """
        解析订单历史中的已完成订单信息
        
        Args:
            response_text: 响应文本数据
            
        Returns:
            Dict: 解析后的订单完成信息字典
        """
        parse = ResponseParser()
        order_history_order_done = parse.parse_response(response_text)['order_done']
        
        return order_history_order_done
    
    def get_order_history_order_done_orderId(self, response_text: str) -> str:
        """
        从订单历史响应中提取订单ID
        
        Args:
            response_text: 包含订单信息的响应文本
            
        Returns:
            str: 订单ID
        """
        parse = self._create_history_order_done_item_handlers()
        return parse.parse_response(response_text)['orderId']
    
    def get_order_history_order_done_area(self, response_text: str) -> str:
        """
        从订单历史响应中提取区域信息
        
        Args:
            response_text: 包含订单信息的响应文本
            
        Returns:
            str: 区域信息
        """
        parse = self._create_history_order_done_item_handlers()
        return parse.parse_response(response_text)['extra_data']['area']

    def _create_history_order_done_item_handlers(self) -> ResponseParser:
        '''
        传入order_done数组的某个json数据，处理order_done下的每个json
        '''

        def _handle_order_Id(value):
            return {
                'value': value,
                'meaning': '订单ID'
            }
        def _handle_order(value):
            return {
                'value': value,
                'meaning': '未知'
            }
        def _handle_from_address(value):
            return {
                'value': value,
                'meaning': '出发地址,fromAddress'
            }
        def _handle_to_address(value):
            return {
                'value': value,
                'meaning': '到达地址,toAddress'
            }
        def _handle_product_type(value):
            return {
                'value': value,
                'meaning': '不知道什么类型'
            }
        def _handle_product_id(value):
            return {
                'value': value,
                'meaning': '不知道什么ID'
            }
        def _handler_setuptime(value):
            return {
                'value': value,
                'meaning': '订单创建时间' 
            }
        def _handle_setuptimestamp(value):
            return {
                'value': value,
                'meaning': '订单创建时间戳'
            }
        def _handle_product_name(value):
            return {
                'value': value,
                'meaning': '出租车类型'
            }
        def _handle_extra_data(value):
            return {
                'value': value,
                'meaning': '额外数据组',
                'area': value['area'],
            }

        _history_order_done_item = {
            'orderId': _handle_order_Id,
            'order': _handle_order,
            'fromAddress': _handle_from_address,
            'toAddress': _handle_to_address,
            'product_type': _handle_product_type,
            'productId': _handle_product_id,
            'setuptime': _handler_setuptime,
            'setuptimestamp': _handle_setuptimestamp,
            'product_name': _handle_product_name,
            'extra_data': _handle_extra_data
        }
        parse = ResponseParser(
            custom_handlers=_history_order_done_item,
            is_other_data=False,
            separate_metadata=True
        )
        return parse


class ParserOrderHistoryDetail:
    """
    订单历史详情解析器类
    用于解析订单历史详情的响应数据，提取详细的订单信息
    """

    def parse_order_detail(self, response_text: str) -> Dict[str, Any]:
        """
        解析获取订单详细信息
        
        Args:
            response_text: 响应文本
        
        Returns:
            Dict: 解析后的订单详细信息
        """
        parse = ResponseParser()
        parser_data = self._create_order_data_handlers()
        parser_data_basic_data = self._create_order_data_basic_data_handlers()

        order_data = parse.parse_response(response_text)['data']
        order_data_basic_data = parser_data.parse_response(order_data)['basic_data']
        order_data_basic_data_detail = parser_data_basic_data.parse_response(order_data_basic_data)
        
        result = {}
        # 提取所有元数据字段（包含"meta"关键字且值为字典类型的字段）
        # 将这些元数据字段的内容合并到结果字典中返回
        # 这是因为ResponseParser在separate_metadata=True时会将元数据存为*_meta字段
        for key,value in order_data_basic_data_detail.items():
            if "meta" in key and isinstance(value, dict):
                result.update(value)
        return result

    def _create_order_data_handlers(self) -> ResponseParser:
        '''
        传入data层，处理data层的数据
        '''
        def _handler_basic_data(value):
            return value
        
        _order_data_handlers: Dict[str, Callable] = {
            'basic_data': _handler_basic_data
        }
        parser = ResponseParser(custom_handlers=_order_data_handlers,is_other_data=False)

        return parser

    def _create_order_data_basic_data_handlers(self) -> ResponseParser:
        '''
        传入data.basic_data，处理data.basic_data层数据
        '''

        def _handler_pay_result(value):
            return {
                'value': value, 
                'total_fee':value['total_fee'], 
                'actual_pay_fee':value['actual_pay_fee']
            }
        def _handler_driver_info(value):
            car_level_mapping = {500: '快车'}
            return {
                'value': value,
                # 'car_level': car_level_mapping.get(value['car_level'], '未找到'),
                'license_num': value['license_num'],
            }
        def _handler_order_info(value):
            return {
                'value': value,
                'from_name': value['from_name'] if value['from_name'] else value['from_address'],
                # 'from_address': value['from_address'],
                # 'from_name': value['from_name'],
                'to_name': value['to_name'],
                'city_name': value['city_name'],
                'to_city_name': value['to_city_name'],
                'create_time': value['create_time'], # 下单时间
                'begin_charge_time': value['begin_charge_time'], # 订单开始计费时间
                'finish_time': value['finish_time'], # 订单完成时间
                'car_type_name': value['car_type_name'],

            }
        
        _order_data_basic_data_handlers: Dict[str, Callable] = {
            'pay_result': _handler_pay_result,
            'driver_info': _handler_driver_info,
            'order_info': _handler_order_info
        }
        parser = ResponseParser(
            custom_handlers=_order_data_basic_data_handlers,
            is_other_data=False,
            separate_metadata=True
        )
        return parser

# TODO：1.更新所需要的参数列表 2.完善注释
class OrderManager:
    """
    订单管理器类
    整合连接订单与订单详细信息，提供订单ID和城市ID的提取功能
    """
    def __init__(self):
        """
        初始化订单管理器，创建历史列表和详情请求实例
        """
        self.history_list_res = GetHistoryList()
        self.history_detail_res = GetHistoryDetail()

    def get_order_history_IDs(self, response_text: str):
        """
        从响应文本中提取订单ID和城市ID
        
        Args:
            response_text: 包含订单历史的响应文本
            
        Returns:
            list: 包含订单ID和城市ID的字典列表
        """
        parse = ParserOrderHistoryList()
        order_done = parse.parse_order_history_order_done(response_text)
        result = []
        for order in order_done:
            order_Id = parse.get_order_history_order_done_orderId(order)
            city_id = parse.get_order_history_order_done_area(order)

            result.append({
                'orderId': order_Id,
                'city_id': city_id
            })

        return result

class ParserLoginRes:
    """
    登录响应解析器类
    用于解析登录请求的响应数据
    """
    def get_login_res(self, response_text: str) -> Dict[str, Any]:
        """
        解析登录响应数据
        
        Args:
            response_text: 登录响应文本
            
        Returns:
            Dict: 解析后的登录响应数据
        """
        parse = ResponseParser()
        return parse.parse_response(response_text)