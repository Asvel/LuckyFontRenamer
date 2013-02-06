# -*- coding: utf-8 -*-

import os
import sys
import re

sys.path.append(os.path.dirname(__file__))
import freetype

output_normal = sys.stdout
output_error = sys.stdout
output_debug = sys.stdout
sys.stdout = None

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
            print("\t", "无法解码字体名称", name.string, file=output_error)
        print("\t",
            str(name.platform_id).rjust(1),
            str(name.encoding_id).rjust(2),
            str(name.language_id).rjust(4),
            name.encoding.ljust(10),
            name.unicode.ljust(80),
            name.string,
            file=output_debug
        )

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
            print("没有从SFNT表中取得字体名称", file=output_error)
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
        print("无法载入文件", fontfilename, "-", e, file=output_error)
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
            print("无法获取字体名称", fontfilename, file=output_error)
        print("\t"*2, name, file=output_debug)
    return names

def try_to_rename(fontfilename, preview=False):
    print(fontfilename, file=output_normal)
    names = guess_names(fontfilename)
    newfilename = " & ".join(names)
    if newfilename != "":
        newfilename += os.path.splitext(fontfilename)[1].lower()
        print("重命名为", newfilename, file=output_normal)
        newfilepath = os.path.join(os.path.dirname(fontfilename), newfilename)
        if not os.path.exists(newfilename):
            try:
                if not preview:
                    os.rename(fontfilename, newfilepath)
            except OSError as e:
                print("重命名失败", e, file=output_error)
        else:
            print("重命名失败", "目标文件已存在", file=output_error)
    else:
        print("重命名失败", "没有取得有效的字体文件名", file=output_error)
    print(file=output_normal)

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
        description='猜测字体的本地化名称并重命名字体',
        epilog="""\
备注：
    字体文件名使用 * 开头表示这是一个含有文件名列表的文本文件(UTF-8编码)
    字体文件名使用 \ 开头表示这是一个含有文件的目录

示例：
    %(prog)s msyh.ttc
    %(prog)s *fontlist.txt
    %(prog)s \\C:\\test\\ -o debug -p
""",
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('file', nargs='+',help="字体文件名")
    parser.add_argument('-o', '--output', default='normal',
        choices=['none', 'error', 'normal', 'debug'],
        help="输出信息，后面的选项包含前面所有选项，默认为 normal")
    parser.add_argument('-p', '--preview', action="store_true",
        help="预览，只输出信息而不重命名文件")
    args = parser.parse_args()

    output = args.output.lower()
    global output_error, output_normal, output_debug
    if output == 'none':
        output_error = output_normal = output_debug = None
    elif output == 'error':
        output_normal = output_debug = None
    elif output == 'normal':
        output_debug = None

    preview = args.preview

    filelist = []
    for filename in args.file:
        if filename.startswith("*"):
            with open(filename[1:], encoding='utf-8') as f:
                for filename in f:
                    filelist.append(filename[:-1])
        elif filename.startswith("\\"):
            for fn in os.listdir(filename[1:]):
                filelist.append(os.path.join(filename[1:], fn))
        else:
            filelist.append(filename)

    for file in filelist:
        try_to_rename(file, preview)

if __name__ == '__main__':
    main()
