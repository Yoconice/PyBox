import os

# ===================== 全局常量 =====================
# 默认分隔符：全角竖线 U+FF5C
# Windows系统合法，辨识度极高，极少出现在原始文件名中
DEFAULT_CONNECTOR = "｜"


def batch_rename_files(root_folder,
                       connector=DEFAULT_CONNECTOR,
                       use_root_prefix=True):
    """
    递归批量重命名文件夹内所有文件（多层级文件夹名称拼接 + 预览确认）
    :param root_folder: 目标根文件夹路径
    :param connector: 名称连接符，默认全角竖线
    :param use_root_prefix: 是否拼接根目录名称作为前缀
    """
    # ------------------- 根文件夹名称处理 -------------------
    abs_root = os.path.abspath(root_folder)
    # 根文件夹原始名称 A
    folder_name_A = os.path.basename(abs_root)

    # ===================== 自定义【新名称B】处理逻辑 =====================
    folder_name_B = folder_name_A  # 直接使用原文件夹名
    # folder_name_B = folder_name_A.upper()  # 示例：转大写
    # folder_name_B = f"前缀_{folder_name_A}"  # 示例：加前缀
    # ====================================================================

    # 待执行重命名任务列表：(旧路径, 新路径, 旧文件名, 新文件名)
    rename_tasks = []
    skip_count = 0

    print("📋 开始扫描并生成重命名预览...")

    # ------------------- 递归遍历所有文件，生成预览 -------------------
    for dirpath, _, filenames in os.walk(abs_root):
        # 跳过没有文件的文件夹
        if not filenames:
            continue

        # 按文件名自然排序，保证顺序稳定
        filenames.sort()
        total = len(filenames)
        folder_show = os.path.basename(dirpath)

        # 同时展示文件夹名称 + 完整绝对路径
        print(f"\n📂 文件夹：{folder_show} | 完整路径：{dirpath} | 文件总数：{total}")

        # ====== 核心：生成多层级拼接的前缀名称 ======
        # 计算当前文件夹相对于根目录的路径部分
        relative_path = os.path.relpath(dirpath, abs_root)

        if relative_path == ".":
            path_parts = []
        else:
            # 拆分相对路径为各个文件夹层级
            path_parts = relative_path.split(os.sep)

        # 根据开关决定是否拼接根目录名称
        if use_root_prefix:
            prefix_parts = [folder_name_B] + path_parts
        else:
            prefix_parts = path_parts

        # 拼接最终前缀
        prefix = connector.join(prefix_parts)

        # ====== 遍历文件生成重命名方案 ======
        for filename in filenames:
            old_path = os.path.join(dirpath, filename)

            # 前缀为空时无需重命名
            if not prefix:
                print(f"   ⏭️  无有效命名前缀，跳过：{filename}")
                skip_count += 1
                continue

            # 新文件名：前缀 + 连接符 + 原文件名
            new_filename = f"{prefix}{connector}{filename}"
            new_path = os.path.join(dirpath, new_filename)

            # 新旧路径一致，无需修改
            if old_path == new_path:
                print(f"   ⏭️  无需修改：{filename}")
                skip_count += 1
                continue

            # 目标文件已存在，跳过防止覆盖
            if os.path.exists(new_path):
                print(f"   ⚠️  跳过（已存在）：{new_filename}")
                skip_count += 1
                continue

            # 加入任务列表并打印预览
            rename_tasks.append((old_path, new_path, filename, new_filename))
            print(f"   ✅ {filename} → {new_filename}")

    # ===================== 末尾输出配置与统计信息 =====================
    print("\n" + "=" * 60)
    print("【执行信息汇总】")
    print(f"根文件夹原始名称：{folder_name_A}")
    print(f"处理后根目录名称：{folder_name_B}")
    print(f"使用连接符：{connector}")
    print(f"是否拼接根目录名称：{'开启' if use_root_prefix else '关闭'}")
    print(f"待重命名文件数：{len(rename_tasks)}")
    print(f"跳过文件数：{skip_count}")
    print("=" * 60)

    # 没有待执行任务，直接结束
    if not rename_tasks:
        print("\nℹ️  没有需要重命名的文件，程序结束。")
        return

    # ===================== 交互式确认执行 =====================
    while True:
        user_input = input("\n是否执行真实重命名操作？(y/n): ").strip()
        if user_input.lower() == "y":
            print("\n🚀 开始执行重命名...")
            for old_path, new_path, old_name, new_name in rename_tasks:
                os.rename(old_path, new_path)
                print(f"   ✅【已重命名】{old_name} → {new_name}")
            print(f"\n🎉 全部执行完成！共重命名 {len(rename_tasks)} 个文件。")
            break
        elif user_input.lower() == "n":
            print("\n❌ 已取消操作，未修改任何文件。")
            break
        else:
            print("⚠️  输入无效，请输入 y（执行）或 n（取消）")


# ------------------- 主程序配置区 -------------------
if __name__ == "__main__":
    # 1. 修改为你的目标文件夹路径
    TARGET_FOLDER = r"D:\Twi\Tu\神楽"

    # 2. 连接符（默认使用全局常量全角竖线，可自行覆盖）
    CONNECTOR = DEFAULT_CONNECTOR

    # 3. 是否拼接根目录名称：True=开启 / False=关闭
    USE_ROOT_PREFIX = False

    # 执行
    try:
        batch_rename_files(
            root_folder=TARGET_FOLDER,
            connector=CONNECTOR,
            use_root_prefix=USE_ROOT_PREFIX
        )
    except Exception as e:
        print(f"\n❌ 出错：{str(e)}")