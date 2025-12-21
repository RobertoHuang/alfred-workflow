import sys;
import json;


"""
Script Filter JSON格式参考:

https://www.alfredapp.com/help/workflows/inputs/script-filter/json/
"""
class ChangXianWorkFlow:
    items = [];
    
    def add_item(self, title, subtitle='', valid=True, icon=None, arg=None):
        """
        添加一个结果项
        
        参数:
            title: 条目标题（必需）
            subtitle: 条目副标题（可选）
            valid: 条目是否有效，是否可操作（可选，默认True）
            icon: 条目图标（可选）
            arg: 传递给下一个操作的参数（可选）
        """
        item = {
            'title': title,
            'subtitle': subtitle,
            'valid': valid,
            'icon': icon,
            'arg': arg
        }
        # 移除 None 值的字段，保持 JSON 简洁
        item = {k: v for k, v in item.items() if v is not None}
        self.items.append(item)
        
    def add_error_item(self, title, subtitle=''):
        """
        添加一个错误提示项
        
        参数:
            title: 错误标题
            subtitle: 错误副标题（可选）
        """
        item = {
            'title': title,
            'subtitle': subtitle,
            'valid': False,
            'icon': {
                "path": "./logo/error_logo.png"
            }
        }
        self.items.append(item)

    def send_feedback(self):
        """
        发送反馈结果给 Alfred
        """
        sys.stdout.write('')
        ret = {
            'items': self.items
        }
        sys.stdout.write(json.dumps(ret))
        sys.stdout.flush()