import os

def batch_rename_files(root_folder, connector="_", seq_prefix="", force_digits=0):
    abs_root = os.path.abspath(root_folder)
    folder_name_A = os.path.basename(abs_root)
    folder_name_B = folder_name_A

    print("=" * 60)
    print(f"根文件夹名称：{folder_name_A}")
    print(f"连接符：{connector}")
    print(f"序号前缀：{seq_prefix if seq_prefix else '无'}")
    print(f"强制位数：{force_digits if force_digits else '自动'}")
    print("=" * 60)
    print()

    # 递归遍历所有文件夹
    for dirpath, _, filenames in os.walk(abs_root):
        # 只处理真实文件
        files = [f for f in filenames if os.path.isfile(os.path.join(dirpath, f))]
        if not files:
            continue

        total = len(files)
        folder_show = os.path.basename(dirpath)
        print(f"\n📂 文件夹：{folder_show} | 文件数量：{total}")

        # 生成文件夹层级名称
        rel_path = os.path.relpath(dirpath, abs_root)
        name_parts = [folder_name_B] if rel_path == "." else rel_path.split(os.sep)
        base_name = connector.join(name_parts)

        # ===================== 核心：新位数规则 =====================
        if total == 1:
            digits = 0  # 单个文件不加序号
        else:
            if force_digits > 0:
                digits = force_digits  # 优先使用强制位数
            else:
                # 新规则：位数 = 文件总数的字符长度 + 1
                total_str = str(total)
                digits = len(total_str) + 1
        # ===========================================================

        # 遍历重命名
        for idx, filename in enumerate(files, start=1):
            name, ext = os.path.splitext(filename)

            # 单个文件：只使用文件夹名称
            if total == 1:
                new_filename = f"{base_name}{ext}"
            else:
                # 生成序号
                seq = f"{idx:0{digits}d}"
                new_filename = f"{base_name}{connector}{seq_prefix}{seq}{ext}"

            old_path = os.path.join(dirpath, filename)
            new_path = os.path.join(dirpath, new_filename)

            if not os.path.exists(new_path):
                os.rename(old_path, new_path)
                print(f"   ✅ {filename} → {new_filename}")
            else:
                print(f"   ⚠️  跳过（已存在）：{new_filename}")

    print("\n🎉 全部处理完成！")

# ===================== 【用户配置区】在这里修改 =====================
if __name__ == "__main__":
    # 1. 目标文件夹路径
    TARGET_FOLDER = r"F:\Downloads\A"

    # 2. 连接符
    CONNECTOR = "_"

    # 3. 序号前缀（例如 P → P001）
    SEQ_PREFIX = ""

    # 4. 强制序号位数（0=自动计算，非0=固定位数）
    FORCE_DIGITS = 0

    # 执行
    try:
        batch_rename_files(
            root_folder=TARGET_FOLDER,
            connector=CONNECTOR,
            seq_prefix=SEQ_PREFIX,
            force_digits=FORCE_DIGITS
        )
    except Exception as e:
        print(f"\n❌ 错误：{e}")