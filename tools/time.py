import re
import time


# 图标路径常量
CLOCK_ICON = {"path": "./logo/clock.png"}


def getData(args, workflow):
    """
    获取时间数据
    
    支持的输入格式:
    - 'now': 当前时间戳
    - '2024-01-01': 日期格式
    - '2024-01-01 12:00:00': 日期时间格式
    - '1234567890': 时间戳（秒或毫秒）
    
    参数:
        args: 参数列表，第一个参数为时间输入
        workflow: ChangXianWorkFlow 实例
    
    返回:
        时间戳（秒），如果输入无效返回 None
    """
    if not args or not args[0]:
        return None
    input_time = args[0].strip()
    return _format_time(input_time)

def parseData(workflow, data, args):
    """
    解析时间数据并添加到 workflow
    
    参数:
        workflow: ChangXianWorkFlow 实例
        data: 时间戳（秒）
        args: 参数列表
    """
    if data is None:
        return
    
    timestamp = int(data)
    time_array = time.localtime(timestamp)
    
    # 秒
    seconds = str(timestamp)
    workflow.add_item(
        f"秒: {seconds}",
        "时间戳（秒）",
        True,
        CLOCK_ICON,
        seconds
    )
    
    # 毫秒
    milliseconds = str(timestamp * 1000)
    workflow.add_item(
        f"毫秒: {milliseconds}",
        "时间戳（毫秒）",
        True,
        CLOCK_ICON,
        milliseconds
    )
    
    # 日期
    date_str = time.strftime("%Y-%m-%d", time_array)
    workflow.add_item(
        f"日期: {date_str}",
        "日期格式",
        True,
        CLOCK_ICON,
        date_str
    )
    
    # 完整时间
    datetime_str = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
    workflow.add_item(
        f"时间: {datetime_str}",
        "日期时间格式",
        True,
        CLOCK_ICON,
        datetime_str
    )


def onException(args, workflow):
    """
    处理异常
    
    参数:
        args: 参数列表
        workflow: ChangXianWorkFlow 实例
    """
    # 可以在这里添加自定义的异常处理逻辑
    pass


def ifNoData(workflow, args):
    """
    数据为空时的处理
    
    参数:
        workflow: ChangXianWorkFlow 实例
        args: 参数列表
    """
    workflow.add_error_item(
        "时间格式错误",
        "支持的格式: now | 2024-01-01 | 2024-01-01 12:00:00 | 时间戳"
    )


def _format_time(input_time):
    """
    格式化时间输入为时间戳（秒）
    
    参数:
        input_time: 时间输入字符串
    
    返回:
        时间戳（秒），如果格式无效返回 None
    """
    if not input_time:
        return None
    
    input_time = input_time.strip()
    
    # 当前时间
    if input_time == 'now':
        return time.time()
    
    # 日期格式: 2024-01-01
    if re.match(r"^\d{4}-\d{2}-\d{2}$", input_time):
        try:
            return time.mktime(time.strptime(input_time, '%Y-%m-%d'))
        except ValueError:
            return None
    
    # 日期时间格式: 2024-01-01 12:00:00
    if re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$", input_time):
        try:
            return time.mktime(time.strptime(input_time, '%Y-%m-%d %H:%M:%S'))
        except ValueError:
            return None
    
    # 时间戳格式: 纯数字
    if re.match(r"^\d+$", input_time):
        try:
            timestamp = int(input_time)
            # 如果时间戳大于 253402185600（约 1978年），可能是毫秒，转换为秒
            # 253402185600 是 1978-01-01 00:00:00 的时间戳（秒）
            if timestamp > 253402185600:
                timestamp = timestamp / 1000
            return timestamp
        except ValueError:
            return None
    
    return None