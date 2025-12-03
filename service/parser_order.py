from typing import Dict, Any, Optional, Callable
from utils.tools import send_get_request
from response_decorators import handle_api_response
import time
from service.parse_response import ResponseParser
from network.history import *
import json


class ParserOrderHistoryList:
    
    # TODO 继续完成 1.增加get必要参数的函数 2.合并所有必要参数到新函数get_req_params 3.完善注释 
    def parse_order_history_order_done(self, response_text: str) -> Dict[str, Any]:
        parse = ResponseParser()
        order_history_order_done = parse.parse_response(response_text)['order_done']
        
        return order_history_order_done
    
    def get_order_history_order_done_orderId(self, response_text: str) -> str:
        parse = self._create_history_order_done_item_handlers()
        return parse.parse_response(response_text)['orderId']
    
    def get_order_history_order_done_area(self, response_text: str) -> str:
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

    def parse_order_detail(self, response_text: str) -> Dict[str, Any]:
        """
        解析获取订单详细信息
        
        Args:
            response_text: 响应文本
        
        Returns:
            Dict[str, Any]: 解析后的订单详细信息
        """
        parse = ResponseParser()
        parser_data = self._create_order_data_handlers()
        parser_data_basic_data = self._create_order_data_basic_data_handlers()

        order_data = parse.parse_response(response_text)['data']
        order_data_basic_data = parser_data.parse_response(order_data)['basic_data']
        order_data_basic_data_detail = parser_data_basic_data.parse_response(order_data_basic_data)
        
        result = {}
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

# TODO 有时候使用from_name字段返回，有时候使用from_address字段返回
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
                'from_name': value['from_name'] if value['from_address'] else value['from_address'],
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
    '''
    整合连接订单与订单详细信息
    '''
    def __init__(self):
        self.history_list_res = GetHistoryList()
        self.history_detail_res = GetHistoryDetail()

    def get_order_history_IDs(self, response_text: str):
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
    def get_login_res(self, response_text: str) -> Dict[str, Any]:
        parse = ResponseParser()
        return parse.parse_response(response_text)