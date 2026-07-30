import os

# ===================== 全局常量 =====================
# 默认分隔符：全角竖线 U+FF5C
# Windows系统合法，辨识度极高，极少出现在原始文件名中
DEFAULT_CONNECTOR = "｜"


def batch_rename_files(root_folder,
                       connector=DEFAULT_CONNECTOR,
                       seq_prefix="",
                       force_digits=0,
                       use_root_prefix=True):
    """
    批量递归文件重命名（先预览后确认执行）
    :param root_folder: 目标根目录路径
    :param connector: 层级/序号分隔符，默认使用全角竖线
    :param seq_prefix: 序号前缀文本
    :param force_digits: 强制序号位数，0=自动计算（总数位数+1）
    :param use_root_prefix: True=拼接根目录名称；False=仅使用子目录层级命名
    """
    abs_root = os.path.abspath(root_folder)
    root_dir_name = os.path.basename(abs_root)

    rename_tasks = []  # 待执行的重命名任务列表：(旧路径, 新路径, 旧文件名, 新文件名)
    skip_count = 0

    print("📋 开始扫描并生成重命名预览...\n")

    # 递归遍历所有子目录，生成预览并收集任务
    for dirpath, _, filenames in os.walk(abs_root):
        # 按文件名自然排序，保证序号顺序稳定
        filenames.sort()
        if not filenames:
            continue

        total = len(filenames)
        folder_show = os.path.basename(dirpath)
        # 同时展示文件夹名称 + 完整绝对路径
        print(f"\n📂 文件夹：{folder_show} | 完整路径：{dirpath} | 文件总数：{total}")

        # 计算相对路径与命名前缀
        rel_path = os.path.relpath(dirpath, abs_root)
        path_parts = [] if rel_path == "." else rel_path.split(os.sep)

        if use_root_prefix:
            name_parts = [root_dir_name] + path_parts
        else:
            name_parts = path_parts

        base_name = connector.join(name_parts)

        # 计算序号位数
        if total == 1:
            digits = 0
        else:
            digits = force_digits if force_digits > 0 else len(str(total)) + 1

        # 逐个处理文件
        for idx, filename in enumerate(filenames, start=1):
            _, ext = os.path.splitext(filename)
            old_path = os.path.join(dirpath, filename)

            # 预警：原文件名包含分隔符，可能影响后续层级拆分
            if connector in filename:
                print(f"   ⚠️  原文件名含分隔符，易产生歧义：{filename}")

            # 生成新文件名
            if total == 1:
                if not base_name:
                    print(f"   ⏭️  无有效命名前缀，跳过：{filename}")
                    skip_count += 1
                    continue
                new_filename = f"{base_name}{ext}"
            else:
                seq = f"{idx:0{digits}d}"
                seq_part = f"{seq_prefix}{seq}"
                if base_name:
                    new_filename = f"{base_name}{connector}{seq_part}{ext}"
                else:
                    new_filename = f"{seq_part}{ext}"

            new_path = os.path.join(dirpath, new_filename)

            # 新旧路径一致，无需修改
            if old_path == new_path:
                print(f"   ⏭️  无需修改：{filename}")
                skip_count += 1
                continue

            # 目标文件已存在，跳过
            if os.path.exists(new_path):
                print(f"   ⚠️  目标已存在，跳过：{new_filename}")
                skip_count += 1
                continue

            # 加入任务列表并打印预览
            rename_tasks.append((old_path, new_path, filename, new_filename))
            print(f"   ✅ {filename} → {new_filename}")

    # ===================== 末尾输出配置与统计信息 =====================
    print("\n" + "=" * 60)
    print("【执行信息汇总】")
    print(f"根文件夹：{root_dir_name}")
    print(f"根目录完整路径：{abs_root}")
    print(f"分隔符：{connector}")
    print(f"序号前缀：{seq_prefix if seq_prefix else '无'}")
    print(f"序号位数：{force_digits if force_digits else '自动'}")
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


# ===================== 【用户配置区】 =====================
if __name__ == "__main__":
    # 目标文件夹路径
    TARGET_FOLDER = r"D:\Twi\Tu\神楽"

    # 分隔符（默认使用全局常量，可自行覆盖）
    CONNECTOR = DEFAULT_CONNECTOR

    # 序号前缀（如 "P" → P001）
    SEQ_PREFIX = ""

    # 强制序号位数，0=自动计算
    FORCE_DIGITS = 0

    # 是否拼接根目录名称
    USE_ROOT_PREFIX = False

    # 执行
    try:
        batch_rename_files(
            root_folder=TARGET_FOLDER,
            connector=CONNECTOR,
            seq_prefix=SEQ_PREFIX,
            force_digits=FORCE_DIGITS,
            use_root_prefix=USE_ROOT_PREFIX
        )
    except Exception as e:
        print(f"\n❌ 运行错误：{e}")