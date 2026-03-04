import os


def batch_rename_files(root_folder, connector="_"):
    """
    递归批量重命名文件夹内所有文件（多层级文件夹名称拼接）
    :param root_folder: 目标根文件夹路径
    :param connector: 连接符，默认下划线 _
    """
    # ------------------- 第一步：获取并处理根文件夹名称 -------------------
    abs_root = os.path.abspath(root_folder)
    # 根文件夹原始名称 A
    folder_name_A = os.path.basename(abs_root)

    # ===================== 自定义【新名称B】处理逻辑 =====================
    folder_name_B = folder_name_A  # 直接使用原文件夹名
    # folder_name_B = folder_name_A.upper()  # 示例：转大写
    # folder_name_B = f"前缀_{folder_name_A}"  # 示例：加前缀
    # ====================================================================

    print(f"✅ 根文件夹原始名称：{folder_name_A}")
    print(f"✅ 处理后新名称B：{folder_name_B}")
    print(f"✅ 使用连接符：{connector}\n")

    # ------------------- 第二步：递归遍历所有文件 -------------------
    for dirpath, _, filenames in os.walk(abs_root):
        # 跳过没有文件的文件夹
        if not filenames:
            continue

        # ====== 核心：生成多层级拼接的前缀名称 ======
        # 计算当前文件夹相对于根目录的路径部分
        relative_path = os.path.relpath(dirpath, abs_root)

        # 根目录
        if relative_path == ".":
            prefix_parts = [folder_name_B]
        else:
            # 获取从根目录下开始的所有层级文件夹名称
            prefix_parts = []
            # 拆分相对路径为各个文件夹层级
            path_parts = relative_path.split(os.sep)

            # 规则：
            # 第1层子文件夹 → 只用当前文件夹名
            # 第2层及以下 → 拼接所有上级 + 当前文件夹
            if len(path_parts) == 1:
                # 第一层子文件夹
                prefix_parts = path_parts
            else:
                # 第二层及更深文件夹：拼接所有上级文件夹名称
                prefix_parts = path_parts

        # 拼接最终前缀
        prefix = connector.join(prefix_parts)

        # ====== 遍历文件并重命名 ======
        for filename in filenames:
            old_path = os.path.join(dirpath, filename)
            # 新文件名：前缀 + 连接符 + 原文件名
            new_filename = f"{prefix}{connector}{filename}"
            new_path = os.path.join(dirpath, new_filename)

            # 安全重命名，不覆盖已存在文件
            if not os.path.exists(new_path):
                os.rename(old_path, new_path)
                print(f"✅ 重命名：{filename} → {new_filename}")
            else:
                print(f"⚠️  跳过（已存在）：{new_filename}")


# ------------------- 主程序配置 -------------------
if __name__ == "__main__":
    # 1. 修改为你的目标文件夹路径
    TARGET_FOLDER = r"F:\Downloads\A"

    # 2. 连接符（默认_，可改为-等）
    CONNECTOR = "_"

    # 执行
    try:
        batch_rename_files(TARGET_FOLDER, CONNECTOR)
        print("\n🎉 全部文件重命名完成！")
    except Exception as e:
        print(f"\n❌ 出错：{str(e)}")