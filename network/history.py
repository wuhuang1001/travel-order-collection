import requests
from utils.tools import send_get_request
import time

class GetHistoryList:
    def get_order_history_lists(
            self,            
            token: str,
            phone: str,
            omgid: str,
            wsgsig: str,
            access_key_id: str = '37',
            appversion: str = '6.0.19',
            pagenum: int = 0,
            timemode: str = '',  # 月份时间 格式202507
            datatype: str = 'webapp',
            apiver: str = '2.0.0',
            timestamp: str = '',
            channel: str = '1030000000',
            openid: str = '',
            daijia_token: str = '',
            daijia_pid: str = ''
        ) -> requests.Response:
        '''
        获取滴滴出行订单历史记录
        
        Args:
            access_key_id: 访问密钥ID
            appversion: 应用版本
            token: 用户token
            phone: 手机号码
            pagenum: 页码
            timemode: 时间模式，月份时间 格式202507
            datatype: 数据类型
            apiver: API版本
            timestamp: 时间戳
            channel: 渠道
            openid: openid
            daijia_token: 代驾token
            daijia_pid: 代驾pid
            omgid: omgid标识
            wsgsig: 签名
            
        Returns:
            requests.Response: 响应对象
        '''
        # 如果未提供timestamp，则使用当前时间戳
        if not timestamp:
            timestamp = str(int(time.time() * 1000))
        
        # 构建基础URL和路径
        base_url = 'https://common.diditaxi.com.cn'
        path = '/passenger/history'
        
        # 构建查询参数
        params = {
            'access_key_id': access_key_id,
            'appversion': appversion,
            'token': token,
            'phone': phone,
            'pagenum': pagenum,
            'timemode': timemode,
            'datatype': datatype,
            'apiver': apiver,
            'timestamp': timestamp,
            'channel': channel,
            'openid': openid,
            'daijia_token': daijia_token,
            'daijia_pid': daijia_pid,
            'omgid': omgid,
            'wsgsig': wsgsig
        }
            
        # 发送GET请求
        return send_get_request(base_url, path, params)


class GetHistoryDetail:

    def get_order_detail(
            self,
            token: str,
            phone: str,
            order_id: str,
            oid: str,
            omgid: str,
            wsgsig: str,
            access_key_id: str = '37',
            appversion: str = '6.0.19',
            business_id: str = '260',
            origin_id: str = '1',
            app_version: str = '6.0.19',
            client_type: str = '201',
            map_type: str = 'soso',
            channel: str = '1030000000',
            imei: str = '',
            lang: str = 'zh-CN',
            city_id: str = '11',
            from_param: str = 'standardwebapp',  # renamed from 'from' because it's a Python keyword
            Cityid: str = '11',
            Productid: str = '260',
            booking_assign_timeout: str = '1',
            nginx_cors: str = 'false'
        ) -> requests.Response:
        '''
        获取滴滴出行订单详细信息
        
        Args:
            access_key_id: 访问密钥ID
            appversion: 应用版本
            token: 用户token
            phone: 手机号码
            business_id: 业务ID
            origin_id: 来源ID
            order_id: 订单ID
            app_version: 应用版本
            client_type: 客户端类型
            map_type: 地图类型
            channel: 渠道
            imei: 设备标识
            lang: 语言
            city_id: 城市ID
            from_param: 来源参数 (原名from)
            oid: 订单ID = order_id
            Cityid: 城市ID (大写)
            Productid: 产品ID
            booking_assign_timeout: 预定分配超时
            nginx_cors: Nginx跨域设置
            omgid: omgid标识
            wsgsig: 签名
            
        Returns:
            requests.Response: 响应对象
        '''
        
        # 构建基础URL和路径
        base_url = 'https://api.udache.com'
        path = '/gulfstream/passenger/v2/core/pOrderDetail'
        
        # 构建查询参数
        params = {
            'access_key_id': access_key_id,
            'appversion': appversion,
            'token': token,
            'phone': phone,
            'business_id': business_id,
            'origin_id': origin_id,
            'order_id': order_id,
            'app_version': app_version,
            'client_type': client_type,
            'map_type': map_type,
            'channel': channel,
            'imei': imei,
            'lang': lang,
            'city_id': city_id,
            'from': from_param,
            'oid': oid,
            'Cityid': Cityid,
            'Productid': Productid,
            'booking_assign_timeout': booking_assign_timeout,
            'nginx_cors': nginx_cors,
            'omgid': omgid,
            'wsgsig': wsgsig
        }
            
        # 发送GET请求
        return send_get_request(base_url, path, params)
    
