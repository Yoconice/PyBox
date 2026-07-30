import os
import shutil
from pathlib import Path

TARGET_FOLDER = r"D:\Twi\Tu"

def resolve_conflict(target_dir: Path, filename: str) -> Path:
    """处理文件名冲突，重名时自动追加 (1)(2)... 后缀"""
    target_path = target_dir / filename
    if not target_path.exists():
        return target_path

    stem = target_path.stem
    suffix = target_path.suffix
    counter = 1
    while True:
        new_name = f"{stem} ({counter}){suffix}"
        target_path = target_dir / new_name
        if not target_path.exists():
            return target_path
        counter += 1


def get_unique_folder_name(parent_dir: Path, base_name: str) -> Path:
    """生成不重复的文件夹名，已存在则追加 _new"""
    target = parent_dir / base_name
    if not target.exists():
        return target

    counter = 1
    while True:
        new_name = f"{base_name}_new" if counter == 1 else f"{base_name}_new{counter}"
        target = parent_dir / new_name
        if not target.exists():
            return target
        counter += 1


def collect_all_files(root_dir: Path) -> list[Path]:
    """递归收集目录下所有文件路径（不包含文件夹本身）"""
    files = []
    for item in root_dir.rglob("*"):
        if item.is_file():
            files.append(item)
    return files


def move_to_root(root_path: str, moved_records: list):
    """模式1：所有文件移动到根目录，并记录移动轨迹"""
    root = Path(root_path).resolve()
    if not root.is_dir():
        print(f"错误：路径不存在或不是文件夹 - {root}")
        return

    all_files = collect_all_files(root)
    moved_count = 0
    fail_count = 0

    print("\n" + "=" * 40)
    print("开始执行：全部移动到根目录")
    print("=" * 40)

    for file_path in all_files:
        if file_path.parent == root:
            continue

        target_path = resolve_conflict(root, file_path.name)
        try:
            shutil.move(str(file_path), str(target_path))
            moved_records.append((file_path.resolve(), target_path.resolve()))
            moved_count += 1
            print(f"[成功] {file_path}  →  {target_path}")
        except Exception as e:
            fail_count += 1
            print(f"[失败] {file_path}  原因：{e}")

    print("\n" + "-" * 40)
    print(f"本模式执行完毕：成功移动 {moved_count} 个文件", end="")
    if fail_count > 0:
        print(f"，失败 {fail_count} 个文件")
    else:
        print()


def move_to_secondary_root(root_path: str, moved_records: list):
    """模式2：每个一级子文件夹内的所有文件移动到该一级目录下，并记录移动轨迹"""
    root = Path(root_path).resolve()
    if not root.is_dir():
        print(f"错误：路径不存在或不是文件夹 - {root}")
        return

    first_level_dirs = [d for d in root.iterdir() if d.is_dir()]
    if not first_level_dirs:
        print("根目录下没有子文件夹，无需操作")
        return

    total_moved = 0
    total_fail = 0

    print("\n" + "=" * 40)
    print("开始执行：全部移动到次级根目录")
    print("=" * 40)

    for sec_root in first_level_dirs:
        all_files = collect_all_files(sec_root)
        moved = 0
        fail = 0
        print(f"\n--- 处理次级目录：{sec_root.name} ---")

        for file_path in all_files:
            if file_path.parent == sec_root:
                continue
            target_path = resolve_conflict(sec_root, file_path.name)
            try:
                shutil.move(str(file_path), str(target_path))
                moved_records.append((file_path.resolve(), target_path.resolve()))
                moved += 1
                print(f"[成功] {file_path}  →  {target_path}")
            except Exception as e:
                fail += 1
                print(f"[失败] {file_path}  原因：{e}")

        print(f"次级目录 [{sec_root.name}] 完成：成功 {moved} 个，失败 {fail} 个")
        total_moved += moved
        total_fail += fail

    print("\n" + "-" * 40)
    print(f"本模式执行完毕：总计成功移动 {total_moved} 个文件", end="")
    if total_fail > 0:
        print(f"，失败 {total_fail} 个文件")
    else:
        print()


def move_to_specified_folder(root_path: str, folder_name: str, moved_records: list):
    """模式3：所有文件移动到指定文件夹，并记录移动轨迹"""
    root = Path(root_path).resolve()
    if not root.is_dir():
        print(f"错误：路径不存在或不是文件夹 - {root}")
        return

    if not folder_name.strip():
        base_name = f"###{root.name}"
    else:
        base_name = f"###{folder_name.strip()}"

    target_dir = get_unique_folder_name(root, base_name)
    target_dir.mkdir(parents=True, exist_ok=True)

    print("\n" + "=" * 40)
    print("开始执行：全部移动到指定文件夹")
    print(f"目标文件夹：{target_dir}")
    print("=" * 40)

    all_files = collect_all_files(root)
    moved_count = 0
    fail_count = 0

    for file_path in all_files:
        if target_dir in file_path.parents or file_path.parent == target_dir:
            continue

        target_path = resolve_conflict(target_dir, file_path.name)
        try:
            shutil.move(str(file_path), str(target_path))
            moved_records.append((file_path.resolve(), target_path.resolve()))
            moved_count += 1
            print(f"[成功] {file_path}  →  {target_path}")
        except Exception as e:
            fail_count += 1
            print(f"[失败] {file_path}  原因：{e}")

    print("\n" + "-" * 40)
    print(f"本模式执行完毕：成功移动 {moved_count} 个文件", end="")
    if fail_count > 0:
        print(f"，失败 {fail_count} 个文件")
    else:
        print()


def remove_empty_dirs(root_dir: Path) -> int:
    """递归删除空文件夹（从深层到表层），返回删除的文件夹数量"""
    removed = 0
    for dir_path in sorted(root_dir.rglob("*"), key=lambda p: len(str(p)), reverse=True):
        if dir_path.is_dir():
            try:
                if not any(dir_path.iterdir()):
                    dir_path.rmdir()
                    removed += 1
                    print(f"已删除空文件夹：{dir_path}")
            except Exception as e:
                print(f"删除失败 {dir_path}：{e}")
    return removed


def restore_files(moved_records: list) -> tuple[int, int]:
    """根据移动记录还原所有文件到原始位置，返回(成功数, 失败数)"""
    success = 0
    fail = 0
    # 倒序还原，保证后移动的文件先还原，避免目录层级冲突
    for original_path, moved_path in reversed(moved_records):
        original_path = Path(original_path)
        moved_path = Path(moved_path)

        if not moved_path.exists():
            print(f"[还原失败] 文件已不存在：{moved_path}")
            fail += 1
            continue

        # 自动重建原始目录结构
        original_path.parent.mkdir(parents=True, exist_ok=True)

        # 还原时处理重名冲突
        final_original = original_path
        if final_original.exists():
            stem = final_original.stem
            suffix = final_original.suffix
            counter = 1
            while True:
                new_name = f"{stem} (还原){suffix}" if counter == 1 else f"{stem} (还原{counter}){suffix}"
                final_original = original_path.with_name(new_name)
                if not final_original.exists():
                    break
                counter += 1

        try:
            shutil.move(str(moved_path), str(final_original))
            success += 1
            print(f"[还原成功] {moved_path}  →  {final_original}")
        except Exception as e:
            fail += 1
            print(f"[还原失败] {moved_path}  原因：{e}")

    # 还原完成后清空记录
    moved_records.clear()
    return success, fail


def main():
    print("=" * 50)
    print("          文件批量移动工具（支持循环重选）")
    print("=" * 50)


    root_path = TARGET_FOLDER
    if not os.path.isdir(root_path):
        print("路径无效，程序退出")
        return

    root = Path(root_path).resolve()
    # 全局移动记录：累计所有成功移动的 (原始路径, 移动后路径)
    moved_records = []

    # 外层循环：移动模式选择
    while True:
        print("\n" + "=" * 50)
        print("请选择移动模式：")
        print("  1 - 全部移动到根目录")
        print("  2 - 全部移动到次级根目录（一级子文件夹各自收拢）")
        print("  3 - 全部移动到指定文件夹")

        mode = input("\n输入模式编号 (1/2/3): ").strip()

        # 执行对应移动模式
        if mode == "1":
            move_to_root(root_path, moved_records)
        elif mode == "2":
            move_to_secondary_root(root_path, moved_records)
        elif mode == "3":
            folder_name = input("指定文件夹名称（留空则使用 ###根文件夹名）: ").strip()
            move_to_specified_folder(root_path, folder_name, moved_records)
        else:
            print("无效的模式编号，请重新输入")
            continue

        # 内层循环：后续操作菜单
        while True:
            print("\n" + "=" * 50)
            print("所有文件移动操作已完成，请选择后续操作：")
            print("  0 - 回到移动模式选择")
            print("  1 - 删除所有残留的空文件夹")
            print("  2 - 还原所有文件到原始位置")
            print("  3 - 结束程序")

            choice = input("\n请输入选项编号 (0/1/2/3): ").strip()

            if choice == "0":
                # 跳出内层循环，回到外层模式选择
                break

            elif choice == "1":
                print("\n===== 开始清理空文件夹 =====")
                count = remove_empty_dirs(root)
                print(f"\n清理完成，共删除 {count} 个空文件夹")

            elif choice == "2":
                if not moved_records:
                    print("当前没有可还原的移动记录")
                    continue
                print("\n===== 开始还原文件 =====")
                succ, fail = restore_files(moved_records)
                print(f"\n还原完成：成功 {succ} 个，失败 {fail} 个")

            elif choice == "3":
                print("程序已结束")
                return  # 直接退出整个程序

            else:
                print("输入无效，请重新输入 0、1、2 或 3")


if __name__ == "__main__":
    main()