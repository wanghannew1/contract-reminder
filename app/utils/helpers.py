"""
工具函数 - 日期解析、脱敏等
"""
from datetime import datetime
import re


def parse_date(date_str):
    """
    解析日期字符串，支持多种格式
    支持格式：YYYY/MM/DD, YYYY-MM-DD, YYYYMMDD
    返回datetime.date对象，解析失败返回None
    """
    if not date_str:
        return None

    date_str = str(date_str).strip()

    # YYYYMMDD 格式（无分隔符，8位数字）
    if re.match(r'^\d{8}$', date_str):
        try:
            return datetime.strptime(date_str, '%Y%m%d').date()
        except ValueError:
            return None

    # YYYY/MM/DD 或 YYYY-MM-DD 格式
    for fmt in ['%Y/%m/%d', '%Y-%m-%d']:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue

    return None


def format_date(date_obj, fmt='%Y-%m-%d'):
    """
    格式化日期对象为字符串
    """
    if date_obj is None:
        return ''
    if isinstance(date_obj, str):
        return date_obj
    return date_obj.strftime(fmt)


def mask_id_number(id_number):
    """
    身份证号脱敏：显示前4后4位，中间替换为****
    例如：220102199001011234 -> 2201****1234
    """
    if not id_number or len(id_number) < 8:
        return id_number
    return id_number[:4] + '****' + id_number[-4:]


def mask_phone(phone):
    """
    手机号脱敏：显示前3后4位
    例如：13800138000 -> 138****8000
    """
    if not phone or len(phone) < 7:
        return phone
    return phone[:3] + '****' + phone[-4:]


def mask_name(name):
    """
    姓名脱敏：显示第一个字，后面替换为*
    例如：张三 -> 张*
    """
    if not name or len(name) < 2:
        return name
    return name[0] + '*' * (len(name) - 1)


def days_between(date1, date2=None):
    """
    计算两个日期之间的天数
    如果date2为None，则计算date1与今天之间的天数
    """
    if date2 is None:
        date2 = datetime.now().date()
    if isinstance(date1, datetime):
        date1 = date1.date()
    if isinstance(date2, datetime):
        date2 = date2.date()
    delta = date2 - date1
    return delta.days


def get_weekday_name(weekday_int, lang='zh'):
    """
    将星期数字转换为星期名称
    0=周一, 1=周二, ..., 6=周日
    """
    names_zh = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    names_en = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    if lang == 'zh':
        return names_zh[weekday_int] if 0 <= weekday_int <= 6 else ''
    return names_en[weekday_int] if 0 <= weekday_int <= 6 else ''


def get_weekday_abbr(weekday_int, lang='zh'):
    """
    将星期数字转换为星期缩写
    0=周一, 1=周二, ..., 6=周日
    """
    abbr_zh = ['一', '二', '三', '四', '五', '六', '日']
    abbr_en = ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU']

    if lang == 'zh':
        return abbr_zh[weekday_int] if 0 <= weekday_int <= 6 else ''
    return abbr_en[weekday_int] if 0 <= weekday_int <= 6 else ''
