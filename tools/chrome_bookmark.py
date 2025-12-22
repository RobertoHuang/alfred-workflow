import json
import os

# 图标路径常量
BOOKMARK_ICON = {"path": "./logo/book_mark.png"}  # 可以后续替换为书签图标

def getData(args, workflow):
    """
    获取 Chrome 书签数据
    
    参数:
        args: 参数列表，第一个参数为搜索关键词（可选）
        workflow: ChangXianWorkFlow 实例
    
    返回:
        书签数据列表（已转换为指定格式），如果出错返回 None
    """
    try:
        # 获取 Chrome 书签文件路径
        bookmark_path = _get_chrome_bookmark_path()
        
        if not bookmark_path or not os.path.exists(bookmark_path):
            return None
        
        # 读取并解析书签文件
        with open(bookmark_path, 'r', encoding='utf-8') as f:
            chrome_bookmarks = json.load(f)
        
        # 转换为指定格式
        converted_bookmarks = _convert_bookmarks(chrome_bookmarks)
        
        # 如果有搜索关键词，进行过滤
        search_keyword = args[0].strip() if args and args[0] else ""
        
        if search_keyword:
            converted_bookmarks = _filter_bookmarks(converted_bookmarks, search_keyword)
        
        return converted_bookmarks
    except Exception as e:
        return None


def parseData(workflow, data, args):
    """
    解析书签数据并添加到 workflow
    
    参数:
        workflow: ChangXianWorkFlow 实例
        data: getData() 返回的书签数据列表
        args: 参数列表
    """
    if data is None or not data:
        ifNoData(workflow, args)
        return
    
    # 展平书签树，提取所有链接
    links = _flatten_links(data)
    
    # 如果展平后没有链接，调用 ifNoData
    if len(links) == 0:
        ifNoData(workflow, args)
        return
    
    # 限制显示数量（避免结果过多）
    max_results = 10
    for link in links[:max_results]:
        title = link.get('title', '无标题')
        url = link.get('url', '')
        
        # 构建副标题（显示路径和 URL）
        subtitle_parts = []
        if link.get('path'):
            subtitle_parts.append(f"路径: {link['path']}")
        if url:
            subtitle_parts.append(url)
        subtitle = " | ".join(subtitle_parts) if subtitle_parts else "无 URL"
        
        workflow.add_item(
            title=title,
            subtitle=subtitle,
            valid=True,
            icon=BOOKMARK_ICON,
            arg=url
        )
    
    if len(links) > max_results:
        workflow.add_item(
            title=f"还有 {len(links) - max_results} 个结果未显示...",
            subtitle="请输入更精确的搜索关键词",
            valid=False,
            icon=BOOKMARK_ICON
        )


def onException(args, workflow):
    """
    处理异常
    
    参数:
        args: 参数列表
        workflow: ChangXianWorkFlow 实例
    """
    workflow.add_error_item(
        "书签读取失败",
        "请确保 Chrome 已安装且书签文件存在"
    )


def ifNoData(workflow, args):
    """
    数据为空时的处理
    
    参数:
        workflow: ChangXianWorkFlow 实例
        args: 参数列表
    """
    search_keyword = args[0].strip() if args and args[0] else ""
    if search_keyword:
        workflow.add_error_item(
            "未找到匹配的书签",
            f"搜索关键词: {search_keyword}"
        )
    else:
        workflow.add_error_item(
            "未找到书签",
            "请检查 Chrome 书签文件路径"
        )


def _get_chrome_bookmark_path():
    """
    获取 Chrome 书签文件路径
    
    返回:
        书签文件路径，如果不存在返回 None
    """
    home = os.path.expanduser("~")
    # macOS Chrome 书签路径
    bookmark_path = os.path.join(
        home,
        "Library/Application Support/Google/Chrome/Default/Bookmarks"
    )
    
    if os.path.exists(bookmark_path):
        return bookmark_path
    
    return None


def _convert_bookmarks(chrome_bookmarks):
    """
    将 Chrome 书签格式转换为指定格式
    
    参数:
        chrome_bookmarks: Chrome 原始书签 JSON 对象
    
    返回:
        转换后的书签列表
    """
    result = []
    
    # Chrome 书签结构: {"roots": {"bookmark_bar": {...}, "other": {...}, "synced": {...}}}
    roots = chrome_bookmarks.get('roots', {})
    
    # 处理各个根节点
    for root_name, root_node in roots.items():
        if root_node and isinstance(root_node, dict):
            converted = _convert_node(root_node)
            if converted:
                result.append(converted)
    
    return result


def _convert_chrome_timestamp(chrome_timestamp):
    """
    将 Chrome 书签时间戳转换为 Unix 时间戳（毫秒）
    
    Chrome 书签时间戳是从 1601-01-01 00:00:00 UTC 开始的微秒数
    需要转换为 Unix 时间戳（从 1970-01-01 00:00:00 UTC 开始的毫秒数）
    
    参数:
        chrome_timestamp: Chrome 时间戳（微秒），可能是字符串或整数
    
    返回:
        Unix 时间戳（毫秒）
    """
    if not chrome_timestamp:
        return 0
    
    try:
        # 如果 time_timestamp 是字符串，先转换为整数
        if isinstance(chrome_timestamp, str):
            chrome_timestamp = int(chrome_timestamp)
        elif not isinstance(chrome_timestamp, (int, float)):
            return 0
        
        # Chrome 时间戳起点：1601-01-01 00:00:00 UTC
        # Unix 时间戳起点：1970-01-01 00:00:00 UTC
        # 差值：11644473600 秒 = 11644473600000 毫秒 = 11644473600000000 微秒
        chrome_epoch_microseconds = 11644473600000000
        
        # 转换为 Unix 时间戳（毫秒）
        unix_timestamp_ms = (chrome_timestamp - chrome_epoch_microseconds) // 1000
        
        return unix_timestamp_ms
    except (ValueError, TypeError):
        return 0


def _convert_node(node):
    """
    递归转换书签节点
    
    参数:
        node: Chrome 书签节点对象
    
    返回:
        转换后的节点对象
    """
    if not node or not isinstance(node, dict):
        return None
    
    node_type = node.get('type', '')
    
    # 文件夹节点
    if node_type == 'folder':
        result = {
            'type': 'folder',
            'title': node.get('name', ''),
            'addDate': _convert_chrome_timestamp(node.get('date_added', 0)),
            'children': []
        }
        
        # 递归处理子节点
        children = node.get('children', [])
        for child in children:
            converted_child = _convert_node(child)
            if converted_child:
                result['children'].append(converted_child)
        
        return result
    
    # 链接节点
    elif node_type == 'url':
        return {
            'type': 'link',
            'title': node.get('name', ''),
            'addDate': _convert_chrome_timestamp(node.get('date_added', 0)),
            'url': node.get('url', '')
        }
    
    return None


def _filter_bookmarks(bookmarks, keyword):
    """
    过滤书签（支持书签名和 URL 搜索）
    
    参数:
        bookmarks: 书签列表
        keyword: 搜索关键词
    
    返回:
        过滤后的书签列表
    """
    if not keyword:
        return bookmarks
    
    keyword_lower = keyword.lower()
    filtered = []
    
    for bookmark in bookmarks:
        filtered_bookmark = _filter_node(bookmark, keyword_lower)
        if filtered_bookmark:
            filtered.append(filtered_bookmark)
    
    return filtered


def _filter_node(node, keyword):
    """
    递归过滤书签节点（只按 title 和 url 过滤，不按文件夹名称过滤）
    
    参数:
        node: 书签节点对象
        keyword: 搜索关键词（小写）
    
    返回:
        过滤后的节点对象，如果不匹配返回 None
    """
    if not node:
        return None
    
    node_type = node.get('type', '')
    
    # 文件夹节点：只检查子节点，不检查文件夹名称
    if node_type == 'folder':
        # 检查子节点
        children = node.get('children', [])
        filtered_children = []
        for child in children:
            filtered_child = _filter_node(child, keyword)
            if filtered_child:
                filtered_children.append(filtered_child)
        
        # 如果有匹配的子节点，返回包含这些子节点的文件夹
        if filtered_children:
            result = node.copy()
            result['children'] = filtered_children
            return result

        return None
    
    # 链接节点：检查标题和 URL
    elif node_type == 'link':
        title = node.get('title', '').lower()
        url = node.get('url', '').lower()
        
        # 检查标题或 URL 是否包含关键词
        if keyword in title or keyword in url:
            return node
        
        return None
    
    return None


def _flatten_links(bookmarks, path=""):
    """
    展平书签树，提取所有链接
    
    参数:
        bookmarks: 书签列表
        path: 当前路径（用于构建完整路径）
    
    返回:
        链接列表，每个链接包含 title, url, path
    """
    links = []
    
    for bookmark in bookmarks:
        bookmark_type = bookmark.get('type', '')
        
        if bookmark_type == 'link':
            # 直接添加链接
            link = {
                'title': bookmark.get('title', ''),
                'url': bookmark.get('url', ''),
                'path': path
            }
            links.append(link)
        
        elif bookmark_type == 'folder':
            # 递归处理文件夹
            folder_title = bookmark.get('title', '')
            new_path = f"{path}/{folder_title}" if path else folder_title
            children = bookmark.get('children', [])
            links.extend(_flatten_links(children, new_path))
    
    return links


