import sys
import traceback
from workflow import ChangXianWorkFlow
from utils import CacheUtils
from utils.LogUtils import LogUtils


def init():
    """
    初始化并动态加载模块
    
    期望 sys.argv[1] 格式: "tools.time" (模块路径，点分格式)
    sys.argv[2:] 为搜索参数列表
    """
    global module
    global search_args
    
    if len(sys.argv) < 2:
        raise ValueError("缺少模块路径参数，期望格式: python main.py tools.time [args...]")
    
    # 解析模块路径，例如 "tools.time" -> 导入 tools.time 模块
    module_path = sys.argv[1]
    search_args = sys.argv[2:] if len(sys.argv) > 2 else []
    
    # 动态导入模块
    # 例如 "tools.time" -> 导入 tools 包，然后获取 time 模块
    path_parts = module_path.split(".")
    if len(path_parts) < 2:
        raise ValueError(f"模块路径格式错误，期望格式: package.module，实际: {module_path}")
    
    # 构建模块路径和模块名
    package_path = ".".join(path_parts[:-1])
    module_name = path_parts[-1]
    
    # 导入包
    package = __import__(package_path, fromlist=[module_name])
    # 获取模块
    module = getattr(package, module_name)
    
    # 验证模块是否包含必需的方法
    if not hasattr(module, 'getData'):
        raise AttributeError(f"模块 {module_path} 缺少必需方法: getData")
    if not hasattr(module, 'parseData'):
        raise AttributeError(f"模块 {module_path} 缺少必需方法: parseData")

def execute_module(workflow, module, args):
    """
    执行模块的业务逻辑
    
    参数:
        workflow: ChangXianWorkFlow 实例
        module: 动态加载的模块对象
        args: 搜索参数列表
    
    返回:
        data: 获取到的数据（用于日志记录）
    """
    # 1. 调用 getData 获取数据
    data = module.getData(args, workflow)
    
    # 2. 如果有数据，调用 parseData 解析数据
    if data is not None:
        module.parseData(workflow, data, args)
    else:
        # 数据为空时的处理
        if hasattr(module, 'ifNoData'):
            module.ifNoData(workflow, args)
        else:
            workflow.add_error_item(
                "查询结果为空",
                "检查输入的参数修改后重试..."
            )
    return data


def handle_module_exception(workflow, module, args, exception):
    """
    处理模块执行过程中的异常
    
    参数:
        workflow: ChangXianWorkFlow 实例
        module: 动态加载的模块对象
        args: 搜索参数列表
        exception: 异常对象
    """
    # 调用模块的 onException 方法（如果存在）
    if hasattr(module, 'onException'):
        try:
            module.onException(args, workflow)
        except Exception as e:
            LogUtils.error(f"模块 onException 方法执行失败: {str(e)}")
    
    # 显示错误信息
    workflow.add_error_item(
        "执行异常",
        f"{type(exception).__name__}: {str(exception)}"
    )


def entrance(workflow):
    """
    主入口函数
    
    参数:
        workflow: ChangXianWorkFlow 实例
    """
    global module
    global search_args
    
    data = None
    try:
        # 将 workflow 存入缓存，供其他模块使用
        CacheUtils.put('workflow', workflow)
        
        # 执行模块逻辑
        data = execute_module(workflow, module, search_args)
    except Exception as e:
        # 捕获所有异常
        LogUtils.error(f"模块 {module.__name__} 执行异常: {' '.join(search_args)}")
        LogUtils.error(traceback.format_exc())
        handle_module_exception(workflow, module, search_args, e)
    finally:
        # 发送反馈给 Alfred
        workflow.send_feedback()
        # 清理缓存
        CacheUtils.clean()
        # 记录日志
        data_str = str(data) if data is not None else "None"
        LogUtils.info(f"请求: {' '.join(search_args)} | 响应: {data_str}")


# 程序入口
if __name__ == '__main__':
    try:
        init()
        changXianWorkFlow = ChangXianWorkFlow()
        sys.exit(entrance(changXianWorkFlow))
    except Exception as e:
        # 初始化失败
        workflow = ChangXianWorkFlow()
        workflow.add_error_item(
            "Workflow初始化失败",
            f"错误信息: {type(e).__name__}: {str(e)}"
        )
        workflow.send_feedback()
        sys.exit(1)
