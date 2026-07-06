"""登录状态服务 — token 有效性校验"""

import json
import time
from utils.tools import send_get_request


def check_login_status(token: str, phone: str, omgid: str, wsgsig: str) -> bool:
    """
    校验 token 是否仍然有效

    用已有 token 调用订单历史 API，根据 errno 判断登录状态。
    使用 202001 (很久以前) 作为 timemode 确保空结果、最小响应体。

    Args:
        token: 用户认证令牌
        phone: 用户手机号
        omgid: 用户唯一标识符
        wsgsig: 请求签名

    Returns:
        True: token 有效 (errno == 0)
        False: token 已失效，需重新登录
    """
    timestamp = str(int(time.time() * 1000))

    resp = send_get_request(
        'https://common.diditaxi.com.cn',
        '/passenger/history',
        {
            'access_key_id': '37',
            'appversion': '6.0.19',
            'token': token,
            'phone': phone,
            'pagenum': 0,
            'timemode': '200013',
            'datatype': 'webapp',
            'apiver': '2.0.0',
            'timestamp': timestamp,
            'channel': '1030000000',
            'omgid': omgid,
            'wsgsig': wsgsig,
        }
    )

    try:
        data = json.loads(resp.text)
        return data.get('errno') == 0
    except json.JSONDecodeError:
        return False
