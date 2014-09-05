# -*- coding: utf-8 -*-

import os
import sys
import logging

from fontname import guess_font_name

if '__file__' in globals():
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def try_to_rename(fontfilename, preview=False):
    """尝试重命名一个字体文件

    fontfilename 字体文件路径
    preview 是否仅预览而不是真正重命名文件
    """

    logging.info("\n{}".format(fontfilename))
    newfilemain = guess_font_name(fontfilename)
    if newfilemain != "":
        oldfiledir, oldfilename = os.path.split(fontfilename)
        oldfilemain, oldfileext = os.path.splitext(oldfilename)
        newfilename = newfilemain + oldfileext.lower()
        newfilepath = os.path.join(oldfiledir, newfilename)
        logging.info("重命名为 {}".format(newfilename))
        if not os.path.exists(newfilepath) or oldfilemain == newfilemain:
            try:
                if not preview:
                    os.rename(fontfilename, newfilepath)
            except OSError as e:
                logging.error("重命名文件 {} 失败, {}".format(fontfilename, e))
        else:
            logging.error("重命名文件 {} 失败, 目标文件 {} 已存在".format(
                fontfilename, newfilename))
    else:
        logging.error("重命名文件 {} 失败, 没有取得有效的字体文件名".format(
            fontfilename))

def main():
    """主函数，提供命令行用户界面
    """

    import argparse
    class ArgumentParser(argparse.ArgumentParser):
        def format_usage(self):
            return argparse.ArgumentParser.format_usage(self)\
            .replace("usage:", "用法：")
        def format_help(self):
            return argparse.ArgumentParser.format_help(self)\
            .replace("usage:", "用法：")\
            .replace("positional arguments:", "参数：")\
            .replace("\n\noptional arguments:", "")\
            .replace("show this help message and exit", "显示此帮助并退出")

    parser = ArgumentParser(
        description='猜测字体的本地化名称并重命名字体文件',
        epilog="""\
备注：
    字体文件名使用 * 开头表示这是一个含有字体文件名列表的文本文件(UTF-8编码)
    字体文件名使用 \ 或 / 结尾表示这是一个含有字体文件的目录

示例：
    %(prog)s msyh.ttc
    %(prog)s *fontlist.txt
    %(prog)s C:\\test\\ -l debug -o debug.txt -p
""",
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('file', nargs='+',help="字体文件名")
    parser.add_argument('-l', '--loglevel', default='info',
        choices=['none', 'error', 'warning', 'info', 'debug'],
        help="输出信息，后面的选项包含前面所有的选项，默认为 info")
    parser.add_argument('-o', '--output', default=None,
        help="输出文件，默认输出至 stderr")
    parser.add_argument('-p', '--preview', action="store_true",
        help="预览，只输出信息而不重命名文件")
    args = parser.parse_args()

    output = args.output
    if output is None:
        output = sys.stderr
    else:
        output = open(output, mode='w', encoding='utf-8')

    loglevel = getattr(logging, args.loglevel.upper(), logging.CRITICAL)
    logging.basicConfig(format='%(message)s', level=loglevel, stream=output)

    preview = args.preview

    filelist = []
    for filename in args.file:
        if filename.startswith("*"):
            with open(filename[1:], encoding='utf-8') as f:
                for filename in f:
                    filelist.append(filename[:-1])
        elif filename.endswith("\\") or filename.endswith("/"):
            for fn in os.listdir(filename):
                filelist.append(os.path.join(filename, fn))
        else:
            filelist.append(filename)

    for file in filelist:
        try_to_rename(file, preview)

    logging.shutdown()
    output.close()

if __name__ == '__main__':
    main()
