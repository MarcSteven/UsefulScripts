import os
import hashlib
from collections import defaultdict

def get_file_hash(filepath):
    """计算文件的 MD5 哈希值"""
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        # 分块读取文件，适合大文件
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def find_duplicate_files(directory):
    """查找指定目录中的重复文件"""
    # 存储文件哈希值与文件路径的映射
    hash_dict = defaultdict(list)
    
    # 遍历目录
    for root, _, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            try:
                # 获取文件的哈希值
                file_hash = get_file_hash(filepath)
                # 将文件路径添加到对应的哈希值列表中
                hash_dict[file_hash].append(filepath)
            except (IOError, PermissionError) as e:
                print(f"无法访问文件 {filepath}: {e}")
    
    # 筛选出重复的文件（哈希值对应多个文件路径）
    duplicates = {hash_val: paths for hash_val, paths in hash_dict.items() if len(paths) > 1}
    return duplicates

def print_duplicates(duplicates):
    """打印重复文件的信息"""
    if not duplicates:
        print("没有找到重复文件。")
        return
    
    print("找到以下重复文件：")
    for hash_val, file_list in duplicates.items():
        print(f"\n哈希值: {hash_val}")
        total_size = 0
        for filepath in file_list:
            size = os.path.getsize(filepath)
            total_size += size
            print(f"  文件: {filepath} ({size / 1024:.2f} KB)")
        print(f"  总大小: {total_size / 1024:.2f} KB")

def main():
    # 获取用户输入的目录
    directory = input("请输入要扫描的目录路径（例如 C:/Users/YourName/Documents）：")
    
    # 验证目录是否存在
    if not os.path.isdir(directory):
        print("错误：指定的目录不存在！")
        return
    
    print(f"正在扫描目录：{directory}")
    duplicates = find_duplicate_files(directory)
    print_duplicates(duplicates)

if __name__ == "__main__":
    main()