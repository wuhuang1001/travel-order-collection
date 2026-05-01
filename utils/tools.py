from datetime import datetime
import requests
from typing import Dict, Any, Optional, List
from utils.wsgsig import generate_wsgsig
import pandas
from tkinter import Tk, filedialog
import os



def send_post_request(
    base_url: str,
    path: str,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    data: Optional[Dict[str, Any]] = None
) -> requests.Response:
    '''
    发送POST请求到指定URL
    
    Args:
        base_url: 基础URL
        path: 路径
        params: URL查询参数字典
        headers: 请求头字典
        data: POST数据字典
    
    Returns:
        requests.Response: 响应对象
    '''
    # 构建完整URL
    url = f'{base_url}{path}'
    
    # TODO 不要使用默认参数，改成必填参数
    # 设置默认headers
    default_headers = {
        'Sec-Ch-Ua': '"Chromium";v="91", " Not;A Brand";v="99"',
        'Accept': 'application/json',
        'Sec-Ch-Ua-Mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://common.diditaxi.com.cn',
        'Sec-Fetch-Site': 'same-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://common.diditaxi.com.cn/',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'close'
    }
    
    # 合并自定义headers
    if headers:
        default_headers.update(headers)
     
    # 发送POST请求
    response = requests.post(
        url=url,
        params=params,
        data=data,
        headers=default_headers
    )

    return response

def send_get_request(
    base_url: str,
    path: str,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None
) -> requests.Response:
    '''
    发送GET请求到指定URL
    
    Args:
        base_url: 基础URL (如: https://common.diditaxi.com.cn)
        path: 路径 (如: /passenger/history)
        params: 查询参数字典
        headers: 请求头字典
    
    Returns:
        requests.Response: 响应对象
    '''
    # 构建完整URL
    url = f'{base_url}{path}'
    
    # 设置默认headers
    default_headers = {
        'Sec-Ch-Ua': '"Chromium";v="91", " Not;A Brand";v="99"',
        'Accept': 'application/json, text/plain, */*',
        'Sec-Ch-Ua-Mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://common.diditaxi.com.cn/general/webEntry?h=1',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'close'
    }
    
    # 合并自定义headers
    if headers:
        default_headers.update(headers)
    
    # 发送GET请求
    response = requests.get(
        url=url,
        params=params,
        headers=default_headers
    )
    
    return response

def get_wsgsig() -> str:
    '''
    获取wsgsig
    '''
    return generate_wsgsig()

def dict_to_csv(
        data: Dict[str, Any],
        default_dir: str = os.getcwd(),
        default_file_name: str = 'output.csv'
):
    '''
    将字典转换为CSV格式的字符串
    
    Args:
        data: 字典数据
        
    '''
    # 将字典转换为DataFrame
    df = pandas.DataFrame([data])

    # 创建 Tkinter 根窗口并隐藏
    root = Tk()
    root.withdraw()

    # 打开"保存文件"对话框，指定默认文件名和文件类型
    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV 文件", "*.csv"), ("所有文件", "*.*")],
        title="保存 CSV 文件",
        initialdir=default_dir,
        initialfile=default_file_name
    )

    # 如果用户没有取消对话框，则保存文件
    if file_path:
        df.to_csv(file_path, index=False, encoding='utf-8')
        print(f"文件已保存到: {file_path}")
    else:
        print("用户取消了保存操作")

def dict_in_list_to_csv(
        data: List[Dict[str, Any]],
        default_dir: str = os.getcwd(),
        default_file_name: str = 'output.csv'
):
    '''
    将字典列表转换为CSV格式的字符串
    
    Args:
        data: 字典列表数据
        default_dir: 默认保存路径
        default_file_name：默认文件名称
        
    '''

    if not all(isinstance(item, dict) for item in data):
        raise ValueError("列表中的每一项都必须是字典类型")
    
    column_mapping = {
        "total_fee": "总费用",
        "actual_pay_fee": "实付费用",
        "license_num": "车牌号码",
        # "from_address": "出发地址",
        "from_name": "出发地",
        "to_name": "目的地",
        "city_name": "所在城市",
        "to_city_name": "目的城市",
        "create_time": "订单创建时间戳",
        "create_date": "订单日期",
        "create_time_readable": "订单时间",
        "begin_charge_time": "开始计费时间",
        "finish_time": "行程结束时间",
        "car_type_name": "车型名称"
    }
    # 将字典列表转换为DataFrame
    df = pandas.DataFrame(data)

    # 新增：生成可读日期时间列
    if "create_time" in df.columns:
        df["create_date"] = df["create_time"].apply(
            lambda ts: datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
        )
        df["create_time_readable"] = df["create_time"].apply(
            lambda ts: datetime.fromtimestamp(ts).strftime('%H:%M:%S')
        )

    # 检查是否有缺失的列
    missing_columns = set(column_mapping.keys()) - set(df.columns)
    if missing_columns:
        pass
        # print(f"警告: 数据中缺少以下列: {missing_columns}")

    # 把秒级时间戳处理成excel可以识别的时间戳（日期序列号）
    # Excel 日期序列号 = (Unix时间戳 / 86400) + 25569
    # +8 时区 东八区
    time_columns = ["create_time", "begin_charge_time", "finish_time"]
    for col in time_columns:
        if col in df.columns:
            df[col] = df[col] / 86400 + 25569
            df[col] = df[col] + 8 / 24  # 调整时区到东八区 
    
    df.rename(
        columns=column_mapping,
        inplace=True
    )


    print("开始保存操作")
    # 创建 Tkinter 根窗口并隐藏
    root = Tk()
    # root.withdraw()

    # 创建一个临时的顶层窗口，确保在任务栏显示并获得焦点
    root.title("保存文件")  # 设置窗口标题
    root.geometry("1x1+10000+10000")  # 将窗口移到屏幕外，避免闪烁
    root.attributes('-topmost', True)  # 置顶显示
    root.deiconify()  # 显示窗口
    root.lift()  # 提升窗口层级
    root.focus_force()  # 强制获得焦点

    # 初始化文件路径变量
    file_path = None

    # 定义窗口关闭事件处理函数
    def on_closing():
        nonlocal file_path
        file_path = None  # 设置文件路径为None表示用户取消操作
        root.quit()  # 退出主循环

    # 绑定窗口关闭事件
    root.protocol("WM_DELETE_WINDOW", on_closing)

    # 更新窗口以确保属性生效
    root.update()

    # 打开"保存文件"对话框，指定默认文件名和文件类型
    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV 文件", "*.csv"), ("所有文件", "*.*")],
        title="保存 CSV 文件",
        initialdir=default_dir,
        initialfile=default_file_name
    )

    # 销毁临时窗口
    root.destroy()

    # 如果用户没有取消对话框，则保存文件
    if file_path:
        df.to_csv(file_path, index=False, encoding='ANSI')
        print(f"文件已保存到: {file_path}")
    else:
        print("用户取消了保存操作")

# TODO 输出两位时分秒
def safe_convert_timestamp(ts):
    """安全转换时间戳"""
    try:
        # 检查时间戳是否合理（假设在 2000-2030 年之间）
        if 946684800 < ts < 2208988800:  # 2000-2030 范围
            return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    except:
        pass
    return ts

from datetime import datetime
from dateutil.relativedelta import relativedelta

def month_diff(start_month, end_month):
    """计算两个月份之间的间隔"""
    start = datetime.strptime(start_month, "%Y%m")
    end = datetime.strptime(end_month, "%Y%m")
    
    diff = (end.year - start.year) * 12 + (end.month - start.month)
    return diff

def month_generator(start_month, end_month, fmt="%Y%m"):
    """生成从start_month到end_month的月份序列，闭区间"""
    current = datetime.strptime(start_month, fmt)
    end = datetime.strptime(end_month, fmt)
    
    while current <= end:
        yield current.strftime(fmt)
        current += relativedelta(months=1)

