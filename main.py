import network.login as login
from service.parser_order import *
from utils.tools import *
from utils.omgid import get_omgid
import configparser


def get_result(token,phone,omgid,wsgsig,choose_time):
    # 获取历史订单列表
    get_history = GetHistoryList()
    history_list_res = get_history.get_order_history_lists(
        token=token,
        phone=phone,
        omgid=omgid,
        wsgsig=wsgsig,
        timemode=choose_time,
    )
   
    parser_history = OrderManager()
    history_list_parsed = parser_history.get_order_history_IDs(history_list_res.text)
    # print(history_list_parsed)
    # print("-----------------------------------------------------------------------------------------------------------")


    # 获取历史订单详情
    get_history_detail = GetHistoryDetail()
    parser_history_detail = ParserOrderHistoryDetail()
    result = []
    print(f"查询到{choose_time}有",len(history_list_parsed),"条记录")
    # history_list_parsed = history_list_parsed[:2]
    print("--------------------")
    for history_item in history_list_parsed:
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
    
    return result
    # print(results)

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


# TODO 1.添加登录失败校验，如果登录失败/token过期就重新登录 2.添加错误处理
if __name__ == "__main__":
    if not os.path.exists("config.ini"):
        create_default_config()

    config = configparser.ConfigParser()
    config.read("config.ini",encoding="utf-8")
    
    is_login = not config.get("login","token") or not config.get("login","phone") or not config.get("login","uid") or not config.get("login","traceid")
    if is_login:
        print("未检测到登录状态，请先登录...")
        print("--------------------")
        login_res = login.login()
        if not login_res:
            print("登录失败")
            exit()
        common_parser = ParserLoginRes()
        login_res_parsed = common_parser.get_login_res(login_res.text)
        config["login"]["token"] = login_res_parsed["ticket"]
        config["login"]["phone"] = login_res_parsed["cell"]
        config["login"]["uid"] = str(login_res_parsed["uid"])
        config["login"]["suid"] = str(login_res_parsed["suid"])
        config["login"]["traceid"] = login_res_parsed["traceid"]

        with open("config.ini", "w") as configfile:
            config.write(configfile)

        # print(login_res_parsed)
    else:
        print("已检测到登录状态，如需退出登录，请删除config.ini文件后重新运行程序")
        print("--------------------")

    token = config.get("login","token") or login_res_parsed["ticket"]
    phone = config.get("login","phone") or login_res_parsed["cell"]
    uid = config.get("login","uid") or login_res_parsed["uid"]
    suid = config.get("login","suid") or login_res_parsed["suid"]
    traceid = config.get("login","traceid") or login_res_parsed["traceid"]
    omgid = get_omgid()
    wsgsig = get_wsgsig()

    is_range = config.get("range","start") and config.get("range","end")
    is_time = config.get("range","month")

    if is_time or is_range:
        if is_time:
            print(f"当前使用的时间范围为: {config.get('range', 'month')}")
        else:
            print(f"当前使用的时间范围为: {config.get('range', 'start')} - {config.get('range', 'end')}")
        use_config = input("是否使用？(y/n): ").strip().lower()
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
            print("格式错误，请重新输入")
    
    start_time = config.get("range", "start") if is_range else None
    end_time = config.get("range", "end") if is_range else None
    choose_time = config.get("range", "month") if is_time else None

    results = []
    # 优先使用单月份
    if not choose_time:
        for month in month_generator(start_time, end_time):
            result = get_result(token,phone,omgid,wsgsig,month)
            results.extend(result)
        dict_in_list_to_csv(results,default_file_name=f'{start_time}-{end_time}订单详情.csv')
    else:
        result = get_result(token,phone,omgid,wsgsig,choose_time)
        dict_in_list_to_csv(result,default_file_name=f'{choose_time}订单详情.csv')
