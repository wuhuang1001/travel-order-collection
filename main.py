import network.login as login
from service.parser_order import *
from utils.tools import *
from utils.omgid import get_omgid
from utils.simple_output import info, success, verbose, error, separator, section, normal
from utils.updater import check_update_async, check_update_sync, show_update_notice
import configparser
from rich.progress import track
import sys
import argparse

def get_result(token,phone,omgid,wsgsig,choose_time,pagenum=0):
    """
    获取订单历史记录的主函数（多页面支持）
    
    该函数通过调用历史订单接口获取订单列表，循环遍历所有页面，
    然后逐个获取每个订单的详细信息，并将订单数据解析后返回
    
    Args:
        token (str): 用户认证令牌，用于身份验证
        phone (str): 用户手机号，用于身份验证
        omgid (str): 用户唯一标识符
        wsgsig (str): 请求签名参数，用于安全验证
        choose_time (str): 选择的时间范围，用于筛选特定时间段的订单
        pagenum (int, optional): 起始页码，默认为0，用于分页获取数据
    
    Returns:
        tuple: (订单详情列表, 总订单数) - 第一个元素是包含订单详细信息的列表，
               第二个元素是总订单数
    
    Example:
        >>> result, total = get_result("token123", "13800138000", "omgid123", "wsgsig123", "202512")
        >>> print(f"总共查询到{total}条订单")
    """
    # 初始化变量
    get_history = GetHistoryList()
    parser_history = OrderManager()
    get_history_detail = GetHistoryDetail()
    parser_history_detail = ParserOrderHistoryDetail()
    
    all_history_list = []  # 存储所有页面的订单ID
    total_orders = 0  # 总订单数
    current_pagenum = pagenum  # 当前页码
    
    info(f"获取 {choose_time} 的订单数据")
    separator()
    
    # 循环获取所有页面数据，直到order_done为空
    while True:
        print_pagenum = current_pagenum + 1
        verbose(f"第 {print_pagenum} 页")
        
        # 获取当前页的历史订单列表
        history_list_res = get_history.get_order_history_lists(
            token=token,
            phone=phone,
            omgid=omgid,
            wsgsig=wsgsig,
            timemode=choose_time,
            pagenum=current_pagenum
        )
        
        # 解析当前页的订单数据
        history_list_parsed = parser_history.get_order_history_IDs(history_list_res.text)
        
        # 如果当前页没有数据，说明已经到达最后一页
        if not history_list_parsed:
            break
        
        # 累加订单数
        page_count = len(history_list_parsed)
        total_orders += page_count
        verbose(f"第 {print_pagenum} 页: {page_count} 条 (累计 {total_orders})")
        
        # 添加到总列表
        all_history_list.extend(history_list_parsed)
        
        # 页码递增，继续获取下一页
        current_pagenum += 1

    separator()
    success(f"共获取 {total_orders} 条订单")
    separator()
    
    # 获取历史订单详情
    result = []
    for history_item in track(all_history_list, description="(　д ) ﾟ ﾟ  Soooooooo much..."):
        order_detail_res = get_history_detail.get_order_detail(
            token=token,
            phone=phone,
            omgid=omgid,
            wsgsig=wsgsig, 
            order_id=history_item["orderId"],
            oid=history_item["orderId"], 
            city_id=history_item["city_id"],
            Cityid=history_item["city_id"],
        )

        order_detail_res_parsed = parser_history_detail.parse_order_detail(order_detail_res.text)
        result.append(order_detail_res_parsed)

    # 静默过滤空白金额订单
    result = OrderFilter().filter_non_empty_amount(result)

    return result, total_orders

def create_default_config():
    """创建默认的配置文件"""
    config = configparser.ConfigParser()
    
    # 添加登录部分
    config["login"] = {
        "phone": "",
        "token": "",
        "uid": "",
        "suid": "",
        "traceid": ""
    }
    
    # 添加范围部分
    config["range"] = {
        "start": "",
        "end": "",
        "month": ""
    }
    
    # 写入配置文件
    with open("config.ini", "w", encoding="utf-8") as configfile:
        config.write(configfile)


# TODO 添加登录失败校验，如果登录失败/token过期就重新登录
# TODO 添加错误处理
def main(*args, **kwargs):
    # 1. 显示缓存的更新提示（如果有）
    show_update_notice()

    # 2. 后台异步检查更新（不阻塞主流程）
    check_update_async()

    if not os.path.exists("config.ini"):
        create_default_config()

    config = configparser.ConfigParser()
    config.read("config.ini",encoding="utf-8")
    
    is_login = not config.get("login","token") or not config.get("login","phone") or not config.get("login","uid") or not config.get("login","traceid")
    if is_login:
        section("登录")
        login_res = login.login()
        if not login_res:
            error("登录失败，程序终止")
            sys.exit(1)
        common_parser = ParserLoginRes()
        login_res_parsed = common_parser.get_login_res(login_res.text)
        config["login"]["token"] = login_res_parsed["ticket"]
        config["login"]["phone"] = login_res_parsed["cell"]
        config["login"]["uid"] = str(login_res_parsed["uid"])
        config["login"]["suid"] = str(login_res_parsed["suid"])
        config["login"]["traceid"] = login_res_parsed["traceid"]

        with open("config.ini", "w") as configfile:
            config.write(configfile)

        success("登录成功")
    else:
        info("使用已保存的登录状态")
        verbose("若需退出登录，请删除 config.ini 文件")

    token = config.get("login","token") or login_res_parsed["ticket"]
    phone = config.get("login","phone") or login_res_parsed["cell"]
    uid = config.get("login","uid") or login_res_parsed["uid"]
    suid = config.get("login","suid") or login_res_parsed["suid"]
    traceid = config.get("login","traceid") or login_res_parsed["traceid"]
    omgid = get_omgid()
    wsgsig  = get_wsgsig()

    is_range = config.get("range","start") and config.get("range","end")
    is_time = config.get("range","month")

    if is_time or is_range:
        if is_time:
            info(f"当前时间范围: {config.get('range', 'month')}")
        else:
            info(f"当前时间范围: {config.get('range', 'start')} - {config.get('range', 'end')}")
        use_config = input("是否使用？(y/n): ").strip().lower() or 'y'
        if use_config != 'y':
            is_range = False
            is_time = False

    if not is_range and not is_time:
        while True:
            time_input = input("请输入时间范围(格式: 202510-202511)或时间(格式: 202511): ").strip()
            if '-' in time_input:
                parts = time_input.split('-')
                if len(parts) == 2 and len(parts[0]) == 6 and len(parts[1]) == 6 and parts[0].isdigit() and parts[1].isdigit():
                    start_time = parts[0]
                    end_time = parts[1]
                    choose_time = None
                    is_range = True
                    config["range"]["start"] = start_time
                    config["range"]["end"] = end_time
                    with open("config.ini", "w") as configfile:
                        config.write(configfile)
                    break
            elif len(time_input) == 6 and time_input.isdigit():
                start_time = None
                end_time = None
                choose_time = time_input
                is_time = True
                config["range"]["month"] = choose_time
                with open("config.ini", "w") as configfile:
                    config.write(configfile)
                break
            error("格式错误，请重新输入")
    
    start_time = config.get("range", "start") if is_range else None
    end_time = config.get("range", "end") if is_range else None
    choose_time = config.get("range", "month") if is_time else None

    results = []
    pagenum = 0
    total_count = 0
    if "pagenum" in kwargs:
        pagenum = kwargs["pagenum"]
    # 优先使用单月份
    if not choose_time:
        for month in month_generator(start_time, end_time):
            result, month_count = get_result(token,phone,omgid,wsgsig,month)
            results.extend(result)
            total_count += month_count
        success(f"共获取 {len(results)} 条订单")
        default_file_name=f'{start_time}-{end_time}订单详情.csv'
    else: # 单月份
        results, total_count = get_result(token,phone,omgid,wsgsig,choose_time,pagenum=pagenum)
        success(f"共获取 {total_count} 条订单")
        default_file_name=f'{choose_time}订单详情.csv'

    dict_in_list_to_csv(results, default_file_name=default_file_name)

if __name__ == "__main__":
    import utils.check_deps as check_deps
    if not check_deps.check_requirements(): sys.exit(1) # 检查依赖

    # 解析命令行参数
    parser = argparse.ArgumentParser(description="滴滴订单导出工具")
    parser.add_argument("--check-update", action="store_true", help="检查版本更新")
    args = parser.parse_args()

    # 如果指定了 --check-update，只检查更新并退出
    if args.check_update:
        check_update_sync()
        sys.exit(0)

    try:
        main()
    except KeyboardInterrupt as key:
        print()
        error("用户退出")
        sys.exit(1)
