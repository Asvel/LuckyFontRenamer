# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import fontname
from os import path
from argparse import ArgumentParser, RawTextHelpFormatter

__version__ = '0.3.0'



def rename(file, preview=False):
    logging.info("\n字体文件 %s", file)

    try:
        font_name = fontname.get_display_names(file)
    except Exception as e:
        return logging.error("重命名文件 %s 失败，%s", file, e)
    if not font_name:
        return logging.error("重命名文件 %s 失败，没有取得有效的字体文件名", file)

    old_dir, old_name = path.split(file)
    old_main, old_ext = path.splitext(old_name)
    new_name = font_name + old_ext.lower()
    new_path = path.join(old_dir, new_name)
    logging.info("重命名为 {}".format(new_name))

    if not preview and new_name != old_name:
        try:
            os.rename(file, new_path)
        except OSError as e:
            logging.error("重命名文件 %s 失败，%s", file, e)


def _patch_argparse_to_chinese():
    texts = {
        "usage: ": "用法: ",
        "positional arguments": "必须参数",
        "optional arguments": "可选参数",
        "show this help message and exit": "显示此帮助并退出",
        "%(prog)s: error: %(message)s\n": "%(prog)s: 错误: %(message)s\n",
        "the following arguments are required: %s": "下列参数是必须的: %s",
        "unrecognized arguments: %s": "无法识别的参数: %s",
        "invalid choice: %(value)r (choose from %(choices)s)":
            "无效的选择: %(value)r (从 %(choices)s 中选择)",
    }
    gettext = lambda *args: texts.get(args[0], args[0])
    import argparse
    argparse._ = argparse.ngettext = gettext


def main():
    _patch_argparse_to_chinese()

    parser = ArgumentParser(
        description='解析字体的本地化名称并重命名字体文件',
        epilog="""\
备注:
    字体文件名可以使用 * 开头，表示这是一个含有字体文件名列表的文本文件 (UTF-8 编码)

示例:
    %(prog)s msyh.ttc
    %(prog)s *fontlist.txt
    %(prog)s C:\\font-dir -l debug -o debug.txt -p
""",
        formatter_class=RawTextHelpFormatter)
    parser.add_argument(
        'file', nargs='+',
        help="字体文件或目录")
    parser.add_argument(
        '-v', '--version', action='version', version=__version__,
        help="显示版本")
    parser.add_argument(
        '-l', '--loglevel', default='warning',
        choices=['none', 'error', 'warning', 'info', 'debug'],
        help="日志等级，默认为 warning")
    parser.add_argument(
        '-o', '--logfile', default=None,
        help="输出日志到文件而不是 stderr")
    parser.add_argument(
        '-p', '--preview', action="store_true",
        help="使用预览模式，只输出日志而不重命名文件")

    args = parser.parse_args()

    loglevel = getattr(logging, args.loglevel.upper(), logging.WARNING)
    logging.basicConfig(format='%(message)s', level=loglevel, filename=args.logfile)

    preview = args.preview

    files = []
    for item in args.file:
        if item.startswith("*"):
            with open(item[1:], encoding='utf-8') as f:
                files.extend(file.strip() for file in f)
        elif path.isdir(item):
            files.extend(path.join(item, file) for file in os.listdir(item))
        else:
            files.append(item)

    for file in files:
        rename(file, preview)

    logging.shutdown()

if __name__ == '__main__':
    main()
