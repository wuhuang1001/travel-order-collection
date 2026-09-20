# type: ignore

import base64
import hashlib
import random
import struct
import time
from urllib.parse import urlparse, unquote, quote, urlencode


# 用 Python 重构 JS 的 wsgsig 生成逻辑，无需 Node.js 环境
def custom_base64_encode(data: bytes) -> str:
    """
    重构 JS 的 i(t) 函数: 自定义 Base64 编码
    JS 中 alphabet: "ABCDEFG0123456789abcdefgHIJKLMN+/hijklmnOPQRSTopqrstUVWXYZuvwxyz"
    """
    alphabet = "ABCDEFG0123456789abcdefgHIJKLMN+/hijklmnOPQRSTopqrstUVWXYZuvwxyz"
    result = []
    i = 0
    while i < len(data):
        b1 = data[i] if i < len(data) else 0
        b2 = data[i + 1] if i + 1 < len(data) else 0
        b3 = data[i + 2] if i + 2 < len(data) else 0

        combined = (b1 << 16) | (b2 << 8) | b3

        idx1 = (combined >> 18) & 0x3F
        idx2 = (combined >> 12) & 0x3F
        idx3 = (combined >> 6) & 0x3F
        idx4 = combined & 0x3F

        result.append(alphabet[idx1])
        result.append(alphabet[idx2])
        result.append(alphabet[idx3] if i + 1 < len(data) else '=')
        result.append(alphabet[idx4] if i + 2 < len(data) else '=')

        i += 3

    return ''.join(result).rstrip('=')


def xor_bytes(key_bytes: bytes, data: bytes) -> bytes:
    """
    重构 JS 的 r(t, e) 函数: XOR 运算
    """
    result = bytearray(len(data))
    key_len = len(key_bytes)
    for i in range(len(data)):
        result[i] = key_bytes[i % key_len] ^ data[i]
    return bytes(result)


def get_wsgsig(content: str) -> str:
    """
    生成 wsgsig 值
    """
    rand_int = random.randint(0, 0xFFFFFFFF)
    rand_bytes = struct.pack('>I', rand_int)

    content_bytes = content.encode('latin-1')
    xor_result = xor_bytes(rand_bytes, content_bytes)
    combined = rand_bytes + xor_result

    encoded = custom_base64_encode(combined)
    # 不要在这里 quote：调用方用 requests 的 params 传参，requests 会再编码一次，
    # 双重编码会把 %2B/%2F 变成字面量，服务端解码后得到非法 base64 -> HTTP 501
    return "dd03-" + encoded


def get_sig(url):
    query = get_query(url)
    query_dict = query_string_to_map(query)
    map_string = sign_map_to_string(query_dict)
    return str(len(map_string)) + "&sig=" + encrypt_to_md5("R4doMFFeMNlliIWM" + map_string)


def get_query(url):
    parsed_url = urlparse(url)
    return parsed_url.query


def query_string_to_map(query_str):
    query_dict = {}
    try:
        for param in query_str.split('&'):
            if param:
                key, value = map(unquote, param.split('=', 1))
                query_dict[key + value] = ''
    except Exception as e:
        print(e)
    return query_dict


def sign_map_to_string(query_dict):
    try:
        sorted_params = sorted(query_dict.keys(), reverse=True)
        result = ''
        for param in sorted_params:
            if not param.startswith("__x_") and param.lower() != "wsgsig":
                result += param
                result += query_dict[param]
        return result
    except Exception as e:
        print(e)


def encrypt_to_md5(data):
    return hashlib.md5(data.encode()).hexdigest()


def generate_wsgsig(params=None)->str:
    '''
    获取wsgsig

    params: 本次请求真正会发出去的 query 参数（dict 或已序列化的 query string）。

    签名对象必须是「本次请求的参数」，而不是固定 URL：服务端会用收到请求重算
    map_string 并比对 md5，签名错一个字节就返回 HTTP 501。
    因此每个请求都要单独调用一次，不能整个会话复用同一个签名。
    '''
    if params is None:
        query = ''
    elif isinstance(params, str):
        query = params
    else:
        query = urlencode(params)

    timestamp = str(int(time.time()))
    # 复用已有的 get_sig：把本次请求的 query 当作签名对象
    sig = get_sig('http://x/?' + query)
    content = 'ts=' + timestamp + '&v=1&os=web&av=02&kv=0000010001&vl=' + sig
    wsgsig = get_wsgsig(content)
    return wsgsig

if __name__ == '__main__':
    print(generate_wsgsig())
