import os
import re

# ===================== 可配置常量（根据需求修改） =====================
TARGET_FOLDER = r"H:\Tes"  # Windows文件夹路径
SERIAL_PAD = 3  # 序号补位位数（3=001、002；2=01、02；1=1、2）
CONNECTOR = ". "  # 序号与原内容的连接符
PREFIX_CHAR = "No."  # 最终文件名的前缀字符
BASE_SERIAL = 0  # 基准常量（默认10，新序号在此基础上累加计算）
SEPARATORS = ['.', '、', ' ']  # 抽离的分隔符常量，支持灵活添加新分隔符


# ====================================================================

def is_sequence_file(filename):
    """
    判断文件名是否符合序号格式（无前缀，匹配数字+配置分隔符格式）
    返回：(是否符合格式, 提取的序号数字, 序号后的文件内容, 文件扩展名)
    """
    # 分离文件名和扩展名
    name_without_ext, ext = os.path.splitext(filename)

    try:
        # 步骤1：将分隔符列表转为正则兼容的字符集（自动转义特殊字符）
        # 对每个分隔符进行转义，避免.等特殊正则字符失效
        escaped_separators = [re.escape(sep) for sep in SEPARATORS]
        # 拼接为正则字符集：如 [\.、\s]（注：空格转义后仍为空格，不影响匹配）
        separator_pattern = ''.join(escaped_separators)

        # 步骤2：构建正则表达式，使用配置的分隔符
        # ^(\d+)：以数字开头并捕获序号
        # [{separator_pattern}]+：匹配1个及以上配置的分隔符
        # (.*)：捕获分隔符后的文件原内容
        pattern = rf"^(\d+)[{separator_pattern}]+(.*)$"
        match = re.match(pattern, name_without_ext, re.IGNORECASE)

        if match:
            # 提取并验证序号有效性
            serial_str = match.group(1)
            if not serial_str.isdigit():
                return False, None, None, ext
            serial_num = int(serial_str)
            # 提取并清理原内容（去除首尾空白）
            content = match.group(2).strip()
            return True, serial_num, content, ext
    except Exception as e:
        # 捕获正则匹配异常，输出调试信息
        print(f"调试：文件名 {filename} 匹配正则时出错 - {str(e)}")

    return False, None, None, ext


def main():
    # 1. 验证目标文件夹是否存在
    if not os.path.exists(TARGET_FOLDER):
        print(f"错误：目标文件夹 {TARGET_FOLDER} 不存在！")
        return

    # 2. 遍历文件夹，筛选符合序号格式的文件（包含重复序号）
    sequence_files = []
    for filename in os.listdir(TARGET_FOLDER):
        file_path = os.path.join(TARGET_FOLDER, filename)
        if os.path.isdir(file_path):  # 跳过文件夹，只处理文件
            continue

        # 判断是否为序号格式文件
        is_seq, serial_num, content, ext = is_sequence_file(filename)
        if is_seq:
            sequence_files.append({
                "old_path": file_path,
                "serial_num": serial_num,
                "content": content,
                "ext": ext
            })

    # 3. 若没有符合条件的文件，直接退出
    if not sequence_files:
        print("未找到符合序号格式的文件！")
        return

    # 4. 基于基准常量实现序号反转+累加（核心功能）
    # 步骤1：提取所有不重复的原序号，按升序排序
    unique_serials = sorted(list(set([f["serial_num"] for f in sequence_files])))
    # 步骤2：先对真实序号进行精准反转（保留原数值倒序）
    reversed_unique_serials = unique_serials[::-1]
    # 步骤3：建立 原序号 -> 基准累加后新序号 的映射（核心逻辑）
    serial_reverse_map = {}
    for original, reversed_serial in zip(unique_serials, reversed_unique_serials):
        new_serial = BASE_SERIAL + reversed_serial  # 基准值累加反转序号
        serial_reverse_map[original] = new_serial

    # 步骤4：为每个文件分配最终新序号（重复原序号对应相同新序号）
    for file_info in sequence_files:
        original_serial = file_info["serial_num"]
        file_info["final_serial"] = serial_reverse_map[original_serial]

    # 5. 执行重命名操作
    success_count = 0
    for file_info in sequence_files:
        try:
            # 格式化最终序号（按配置补位）
            formatted_serial = f"{file_info['final_serial']:0{SERIAL_PAD}d}"

            # 拼接新文件名：前缀 + 补位序号 + 连接符 + 原内容 + 扩展名
            new_name = (
                f"{PREFIX_CHAR}{formatted_serial}{CONNECTOR}"
                f"{file_info['content']}{file_info['ext']}"
            )
            new_path = os.path.join(TARGET_FOLDER, new_name)

            # 安全防护：避免新文件名重复，自动添加(1)、(2)...后缀
            counter = 1
            temp_new_path = new_path
            while os.path.exists(temp_new_path):
                temp_new_name = (
                    f"{PREFIX_CHAR}{formatted_serial}{CONNECTOR}"
                    f"{file_info['content']}({counter}){file_info['ext']}"
                )
                temp_new_path = os.path.join(TARGET_FOLDER, temp_new_name)
                counter += 1

            # 执行重命名
            os.rename(file_info["old_path"], temp_new_path)
            success_count += 1
            old_filename = os.path.basename(file_info["old_path"])
            new_filename = os.path.basename(temp_new_path)
            print(f"成功：{old_filename[:8]} -----> {new_filename}")
        except Exception as e:
            old_filename = os.path.basename(file_info["old_path"])
            print(f"失败：处理 {old_filename} 时出错 - {str(e)}")

    # 6. 输出最终统计信息
    print(f"\n重命名完成！成功：{success_count} 个，失败：{len(sequence_files) - success_count} 个")
    print(f"基准常量：{BASE_SERIAL}")
    print(f"配置分隔符：{SEPARATORS}")
    print(f"原唯一序号：{unique_serials}")
    print(f"反转后序号：{reversed_unique_serials}")
    print(f"基准累加后最终序号：{[serial_reverse_map[s] for s in unique_serials]}")


if __name__ == "__main__":
    print("===== Windows文件序号倒序重命名程序（可配置分隔符） =====")
    print(f"目标文件夹：{TARGET_FOLDER}")
    print(f"序号补位：{SERIAL_PAD} 位")
    print(f"连接符：{CONNECTOR}")
    print(f"文件名前缀：{PREFIX_CHAR}")
    print(f"基准常量（新序号累加基础）：{BASE_SERIAL}")
    print(f"配置的匹配分隔符：{SEPARATORS}")
    print("==================================================================")
    main()