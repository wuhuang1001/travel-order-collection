import os
import binascii

def get_omgid():
    random_bytes = os.urandom(16)
    random_bytes = bytearray(random_bytes)
    
    # 调整字节以符合UUID v4规范
    random_bytes[6] = (random_bytes[6] & 0x0F) | 0x40  # 设置第7个字节的高4位为4
    random_bytes[8] = (random_bytes[8] & 0x3F) | 0x80  # 设置第9个字节的高2位为1
    
    hex_str = binascii.hexlify(random_bytes).decode()
    uuid_str = f'{hex_str[:8]}-{hex_str[8:12]}-{hex_str[12:16]}-{hex_str[16:20]}-{hex_str[20:]}'
    
    return uuid_str

if __name__ == '__main__':    
    # 测试生成的UUID
    uuid = get_omgid()
    print(uuid)