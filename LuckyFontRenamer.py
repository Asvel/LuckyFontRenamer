# -*- coding: utf-8 -*-

import os
import sys
import re
import logging

if '__file__' in globals():
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import freetype

sfnt_info_encoding = {
    0:{
        0:'utf_16_be',
        1:'utf_16_be',
        2:'utf_16_be',
        3:'utf_16_be',
        4:'utf_16_be',
        5:'utf_16_be',
        },
    1:{
        0:'mac_roman',
        1:'shift_jis',
        2:'big5',
        3:'euc_kr',
        4:'iso8859_6',
        5:'iso8859_8',
        6:'mac_greek',
        7:'iso8859_5',
        8:'ascii',
        9:'ascii',
        10:'ascii',
        11:'ascii',
        12:'ascii',
        13:'ascii',
        14:'ascii',
        15:'ascii',
        16:'ascii',
        17:'ascii',
        18:'ascii',
        19:'ascii',
        20:'ascii',
        21:'cp874',
        22:'ascii',
        23:'ascii',
        24:'ascii',
        25:'euc_cn',
        26:'ascii',
        27:'ascii',
        28:'ascii',
        29:'ascii',
        30:'cp1258',
        31:'ascii',
        32:'ascii',
        },
    2:{
        0:'ascii',
        1:'utf_16_be',
        2:'latin_1',
        },
    3:{
        0:'utf_16_be',
        1:'utf_16_be',
        2:'shift_jis',
        3:'gb2312',
        4:'big5',
        5:'cp949',
        6:'johab',
        10:'utf_32_be',
        },
    4:{
        0:'ascii',
        },
    7:{
        0:'utf_16_be',
        1:'utf_16_be',
        2:'utf_16_be',
        3:'utf_16_be',
        },
}

sfnt_info_priority = [
    (2052, 3, 3),
    (2052, 3, 1),
    (33, 1, 25),
    (1028, 3, 4),
    (1028, 3, 1),
    (19, 1, 2),
    (1041, 3, 2),
    (1041, 3, 1),
    (11, 1, 1),
    (1042, 3, 5),
    (1042, 3, 1),
    (2066, 3, 6),
    (2066, 3, 1),
    (23, 1, 3),
    (1033, 3, 1),
]

def guess_sfnt_name(face, autochoose=True):
    # 获取原始字体名称
    names = [face.get_sfnt_name(i) for i in range(face.sfnt_name_count)]
    names = [x for x in names if x.name_id == 4]

    # 猜测字体名称的编码并尝试解码
    for name in names:
        try:
            encoding = sfnt_info_encoding[name.platform_id][name.encoding_id]
        except:
            encoding = 'utf_16_be'
        try:
            s = name.string.decode(encoding)
            if "\x00" in s.strip("\x00"):
                raise Exception()
        except:
            try:
                if re.match(br'^\x00[\x00-\xFF]*$', name.string):
                    s = name.string.replace(b'\x00', b'').decode(encoding)
                else:
                    raise Exception()
            except:
                try:
                    encoding = 'utf_16_be'
                    s = name.string.decode(encoding)
                except:
                    try:
                        encoding = 'ascii'
                        s = name.string.decode(encoding)
                    except:
                        encoding = None
                        s = ""
        name.encoding = encoding
        name.unicode = s.strip("\x00")
        if name.unicode == "":
            logging.warning("\t无法解码字体名称".format(name.string))
        logging.debug("\t{0.platform_id} {0.encoding_id:>2} {0.language_id:>4}"
                " {0.encoding:<10} {0.unicode:<80} {0.string}".format(name))

    # (猜测合适的字体名称并)返回字体名称
    if autochoose:
        namedict = {(x.language_id, x.platform_id, x.encoding_id):x.unicode
                for x in names}
        for info in sfnt_info_priority:
            if info in namedict:
                return namedict[info]
        if len(names) > 0:
            return names[-1].unicode
        else:
            logging.warning("没有从SFNT表中取得字体名称")
            return ""
    else:
        return {x.unicode for x in names}

def guess_names(fontfilename):
    names = []
    try:
        faces = [freetype.Face(fontfilename)]
        faces += [freetype.Face(fontfilename, i)
                  for i in range(1, faces[0].num_faces)]
    except freetype.ft_errors.FT_Exception as e:
        faces = []
        logging.error("无法载入文件 {} - {}".format(fontfilename, e))
    for face in faces:
        name = ""
        if face.sfnt_name_count > 0:
            name = guess_sfnt_name(face, True)
        if name == "":
            try:
                name = face.family_name.decode('ascii')
            except:
                name = ""
        if name == "":
            try:
                name = face.postscript_name.decode('ascii')
            except:
                name = ""
        if name != "":
            if name not in names:
                names.append(name)
        else:
            logging.error("无法获取字体文件 {} 中某一字体的名称".format(
                fontfilename))
        logging.debug("\t\t{}".format(name))
    return names

def try_to_rename(fontfilename, preview=False):
    logging.info("\n{}".format(fontfilename))
    names = guess_names(fontfilename)
    newfilemain = " & ".join(names)
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