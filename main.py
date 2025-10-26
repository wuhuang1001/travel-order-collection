import login
from parser_order import *
from tools import *
from omgid import get_omgid
import configparser


# TODO 1.添加参数生成控制，避免每次都重新生成参数/添加维持登录状态 2.添加错误处理
if __name__ == "__main__":

    config = configparser.ConfigParser()
    config.read("config.ini",encoding="utf-8")
    
    is_login = not config.get("login","token") or not config.get("login","phone") or not config.get("login","uid") or not config.get("login","traceid")
    if is_login:
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

        print(login_res_parsed)

    token = config.get("login","token") or login_res_parsed["ticket"]
    phone = config.get("login","phone") or login_res_parsed["cell"]
    uid = config.get("login","uid") or login_res_parsed["uid"]
    suid = config.get("login","suid") or login_res_parsed["suid"]
    traceid = config.get("login","traceid") or login_res_parsed["traceid"]
    omgid = get_omgid()
    wsgsig = get_wsgsig()

    start_time = config.get("range","start")
    end_time = config.get("range","end")
    choose_time = config.get("range","month")

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
    results = []
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
        results.append(order_detail_res_parsed)

    dict_in_list_to_csv(results,default_file_name=f'{choose_time}订单详情.csv')
    # print(results)

