#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import random
import hashlib
import shutil
import re

# 定义图片目录路径
IMAGE_DIR = 'res'
# 备份目录
BACKUP_DIR = 'res_backup'

def calculate_md5(file_path):
    """计算文件的MD5值"""
    md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            md5.update(chunk)
    return md5.hexdigest()

def modify_svg_file(file_path):
    """修改SVG文件的MD5值 - 在合适的位置添加注释"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 生成随机注释
    random_comment = f"<!-- MD5_MODIFY_{random.randint(1000000, 9999999)} -->"
    
    # 尝试在SVG标签内添加注释
    if '<svg' in content:
        # 找到第一个svg标签的结束位置
        svg_match = re.search(r'<svg[^>]*>', content)
        if svg_match:
            svg_end = svg_match.end()
            # 在svg标签后添加注释
            content = content[:svg_end] + '\n  ' + random_comment + '\n' + content[svg_end:]
        else:
            # 如果没找到svg标签，在文件开头添加
            content = random_comment + '\n' + content
    else:
        # 如果文件不包含svg标签，在开头添加
        content = random_comment + '\n' + content
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def modify_si_file(file_path):
    """修改SI文件的MD5值 - 在文件末尾添加填充字节"""
    # SI文件是二进制文件，使用二进制方式处理
    with open(file_path, 'rb') as f:
        content = f.read()
    
    # 生成随机填充字节（1-4字节）
    padding_length = random.randint(1, 4)
    padding_bytes = bytes([random.randint(0, 255) for _ in range(padding_length)])
    
    # 在文件末尾添加填充
    with open(file_path, 'ab') as f:
        f.write(padding_bytes)

def modify_binary_file(file_path):
    """修改二进制文件的MD5值 - 在文件末尾添加填充字节"""
    # 读取文件内容
    with open(file_path, 'rb') as f:
        content = f.read()
    
    # 生成随机填充字节（1-4字节）
    padding_length = random.randint(1, 4)
    padding_bytes = bytes([random.randint(0, 255) for _ in range(padding_length)])
    
    # 在文件末尾添加填充
    with open(file_path, 'ab') as f:
        f.write(padding_bytes)

def modify_file_md5(file_path):
    """修改文件的MD5值"""
    # 获取原始MD5值
    original_md5 = calculate_md5(file_path)
    
    file_extension = os.path.splitext(file_path)[1].lower()
    
    try:
        # 根据文件类型选择不同的修改方法
        if file_extension == '.svg':
            modify_svg_file(file_path)
        elif file_extension == '.si':
            modify_si_file(file_path)
        else:
            # 对于其他二进制文件，使用更安全的方法
            modify_binary_file(file_path)
        
        # 获取新的MD5值
        new_md5 = calculate_md5(file_path)
        
        # 验证MD5确实发生了变化
        if original_md5 == new_md5:
            # 如果MD5没有变化，尝试更激进的修改
            if file_extension == '.svg':
                # 对于SVG，添加更多内容
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                extra_comment = f"<!-- EXTRA_{random.randint(1000000, 9999999)} -->"
                content += '\n' + extra_comment
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            else:
                # 对于二进制文件，添加更多字节
                with open(file_path, 'ab') as f:
                    f.write(bytes([random.randint(0, 255) for _ in range(8)]))
            
            new_md5 = calculate_md5(file_path)
        
        return original_md5, new_md5
        
    except Exception as e:
        # 如果修改失败，恢复原始文件
        print(f"修改失败，正在恢复 {file_path}: {e}")
        return original_md5, original_md5

def backup_directory(src_dir, dst_dir):
    """备份目录"""
    if os.path.exists(dst_dir):
        shutil.rmtree(dst_dir)
    shutil.copytree(src_dir, dst_dir)
    print(f"已备份目录 {src_dir} 到 {dst_dir}")

def process_images():
    """处理目录下的所有图片文件"""
    # 先备份目录
    backup_directory(IMAGE_DIR, BACKUP_DIR)

    # 图片文件扩展名列表
    image_extensions = ['.png', '.jpg', '.jpeg', '.webp', '.gif', '.svg', '.si']

    # 遍历目录下的所有文件
    modified_count = 0
    failed_count = 0
    
    for root, _, files in os.walk(IMAGE_DIR):
        for file in files:
            # 跳过.DS_Store文件
            if file == '.DS_Store':
                continue

            file_path = os.path.join(root, file)
            file_extension = os.path.splitext(file)[1].lower()

            # 只处理目标文件类型
            if file_extension in image_extensions:
                try:
                    original_md5, new_md5 = modify_file_md5(file_path)
                    
                    if original_md5 != new_md5:
                        print(f"✅ 已修改: {file_path}")
                        print(f"  原MD5: {original_md5}")
                        print(f"  新MD5: {new_md5}")
                        modified_count += 1
                    else:
                        print(f"❌ 修改失败: {file_path}")
                        failed_count += 1
                        
                except Exception as e:
                    print(f"❌ 处理 {file_path} 时出错: {e}")
                    failed_count += 1

    print(f"\n📊 统计结果:")
    print(f"  成功修改: {modified_count} 个文件")
    print(f"  修改失败: {failed_count} 个文件")
    print(f"  总计处理: {modified_count + failed_count} 个文件")

if __name__ == "__main__":
    print("🚀 开始修改资源文件MD5值...")
    process_images()
    print("✅ 修改完成！")