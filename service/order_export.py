"""
滴滴订单导出服务 - 包含数据准备、字段映射和 CSV 导出功能
"""
import os
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional

COLUMN_MAPPING = {
    "total_fee": "总费用",
    "actual_pay_fee": "实付费用",
    "license_num": "车牌号码",
    "from_name": "出发地",
    "to_name": "目的地",
    "city_name": "所在城市",
    "to_city_name": "目的城市",
    "create_time": "订单创建时间戳",
    "create_date": "订单日期",
    "create_time_readable": "订单时间",
    "begin_charge_time": "开始计费时间",
    "finish_time": "行程结束时间",
    "car_type_name": "车型名称",
}

TIME_COLUMNS = ["create_time", "begin_charge_time", "finish_time"]


def _apply_column_mapping(df: pd.DataFrame) -> pd.DataFrame:
    """应用中文列名映射"""
    existing_mapping = {k: v for k, v in COLUMN_MAPPING.items() if k in df.columns}
    return df.rename(columns=existing_mapping)


def prepare_order_data(orders: List[Dict]) -> List[Dict]:
    """
    准备订单数据：生成可读时间列 + 时间戳转 Excel 格式

    Returns:
        处理后的订单列表（深拷贝，不修改原始数据）
    """
    import copy
    prepared = copy.deepcopy(orders)

    for order in prepared:
        create_ts = order.get("create_time")
        if create_ts and isinstance(create_ts, (int, float)):
            order["create_date"] = datetime.fromtimestamp(create_ts).strftime('%Y-%m-%d')
            order["create_time_readable"] = datetime.fromtimestamp(create_ts).strftime('%H:%M:%S')

        # 时间戳转 Excel 日期序列号 (UTC+8)
        for col in TIME_COLUMNS:
            if col in order and isinstance(order[col], (int, float)):
                order[col] = order[col] / 86400 + 25569 + 8 / 24

    return prepared


def export_order_to_csv_silent(
        orders: List[Dict],
        target_dir: Optional[str] = None,
        target_filename: str = "订单导出.csv"
) -> bool:
    """
    无弹窗导出滴滴订单到 CSV 文件

    Args:
        orders: 订单列表
        target_dir: 目标目录（None 则使用当前目录）
        target_filename: 目标文件名

    Returns:
        bool: 导出成功返回 True，失败返回 False
    """
    prepared = prepare_order_data(orders)
    df = pd.DataFrame(prepared)
    df = _apply_column_mapping(df)

    if target_dir is None:
        target_dir = os.getcwd()

    if not os.path.exists(target_dir):
        os.makedirs(target_dir, exist_ok=True)

    target_path = os.path.join(target_dir, target_filename)

    try:
        df.to_csv(target_path, index=False, encoding='ANSI')
        print(f"[SUCCESS] 文件已保存到: {target_path}")
        return True
    except Exception as e:
        print(f"[ERROR] 保存失败: {e}")
        return False
