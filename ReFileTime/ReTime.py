import os
import sys
import time
import platform
from datetime import datetime, timezone
import pywintypes
import win32file
import win32con


def convert_to_timestamp(time_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> float:
    """将时间字符串转换为时间戳（秒级）"""
    try:
        dt = datetime.strptime(time_str, format_str)
        return time.mktime(dt.timetuple())
    except ValueError as e:
        raise ValueError(f"时间格式错误！请按照 {format_str} 格式输入，错误信息：{e}")


def modify_file_times(
        file_path: str,
        create_time: str = None,
        modify_time: str = None,
        access_time: str = None,
        time_format: str = "%Y-%m-%d %H:%M:%S"
):
    """
    修改文件的创建时间、修改时间、访问时间
    :param file_path: 文件路径（绝对/相对路径）
    :param create_time: 新创建时间（字符串，仅Windows有效）
    :param modify_time: 新修改时间（字符串）
    :param access_time: 新访问时间（字符串）
    :param time_format: 时间格式，默认 "%Y-%m-%d %H:%M:%S"
    """
    # 基础校验
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在：{file_path}")
    if not os.path.isfile(file_path):
        raise IsADirectoryError(f"目标路径不是文件：{file_path}")

    # 转换时间为时间戳（空则保留None）
    new_create_ts = convert_to_timestamp(create_time, time_format) if create_time else None
    new_modify_ts = convert_to_timestamp(modify_time, time_format) if modify_time else None
    new_access_ts = convert_to_timestamp(access_time, time_format) if access_time else None

    system = platform.system()
    try:
        if system == "Windows":
            # Windows：支持修改创建/修改/访问时间
            def ts_to_pywintime(ts):
                """时间戳转pywintypes.Time对象（避免整数溢出）"""
                local_dt = datetime.fromtimestamp(ts)
                return pywintypes.Time(local_dt)

            # 打开文件句柄
            handle = win32file.CreateFile(
                file_path,
                win32con.GENERIC_WRITE,
                win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
                None,
                win32con.OPEN_EXISTING,
                win32con.FILE_ATTRIBUTE_NORMAL | win32con.FILE_FLAG_BACKUP_SEMANTICS,
                None
            )

            # 获取原时间（pywintypes.Time类型）
            original_create, original_access, original_modify = win32file.GetFileTime(handle)

            # 替换需修改的时间（空则保留原始值）
            final_create = ts_to_pywintime(new_create_ts) if new_create_ts else original_create
            final_access = ts_to_pywintime(new_access_ts) if new_access_ts else original_access
            final_modify = ts_to_pywintime(new_modify_ts) if new_modify_ts else original_modify

            # 设置新时间
            win32file.SetFileTime(handle, final_create, final_access, final_modify)
            handle.close()

        else:
            # Linux/macOS：仅支持修改修改/访问时间（创建时间无法修改）
            if new_create_ts:
                print("⚠️ 警告：Linux/macOS不支持修改创建时间，该参数已忽略")

            # 构造utime的时间元组（空则用当前时间戳）
            utime_access = new_access_ts or time.time()
            utime_modify = new_modify_ts or time.time()
            os.utime(file_path, (utime_access, utime_modify))

        # 输出结果
        print(f"✅ 文件时间修改成功！")
        print(f"📄 文件路径：{file_path}")
        print(f"🗓️ 创建时间：{create_time if create_time else '未修改'}")
        print(f"🔄 修改时间：{modify_time if modify_time else '未修改'}")
        print(f"👀 访问时间：{access_time if access_time else '未修改'}")

    except Exception as e:
        raise RuntimeError(f"修改失败：{e}")


if __name__ == "__main__":
    # 示例配置（根据需求修改）
    TARGET_FILE = r"D:\Temp\快乐.mp4"  # 目标文件（用r避免转义）
    NEW_CREATE_TIME = "2022-12-31 14:03:50"  # 新创建时间（Windows有效）
    # NEW_MODIFY_TIME = "2022-12-31 14:03:50"  # 新修改时间
    NEW_MODIFY_TIME = NEW_CREATE_TIME  # 新修改时间
    NEW_ACCESS_TIME = None  # 新访问时间（可设为None表示不修改）

    try:
        modify_file_times(
            file_path=TARGET_FILE,
            create_time=NEW_CREATE_TIME,
            modify_time=NEW_MODIFY_TIME,
            access_time=NEW_ACCESS_TIME  # 新增的访问时间参数
        )
    except Exception as e:
        print(f"❌ 错误：{e}", file=sys.stderr)