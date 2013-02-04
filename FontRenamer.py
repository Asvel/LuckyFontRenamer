# -*- coding: utf-8 -*-

import os
import sys
import re

sys.path.append(os.path.dirname(__file__))
import freetype

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
    (1033, 3, 1),
]

def guess_sfnt_name(face, autochoose=True):
    # 获取原始字体名称
    names = [face.get_sfnt_name(i) for i in range(face.sfnt_name_count)]
    langs = {x.language_id for x in names}
    names = [x for x in names if x.name_id == 4]

    # 猜测字体名称的编码并尝试解码
    for name in names:
        try:
            encoding = freetype.sfnt_name_encoding\
                       [name.platform_id][name.encoding_id]
        except:
            encoding = 'utf_16_be'
        if encoding == 'mac_roman' and\
           {1041} <= langs <= {0,11,1033,1041}:
            encoding = 'shift_jis'
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

    # (猜测合适的字体名称并)返回字体名称
    if autochoose:
        namedict = {(x.language_id, x.platform_id, x.encoding_id):x.unicode
                for x in names}
        for info in sfnt_info_priority:
            if info in namedict:
                return namedict[info]
        return names[-1].unicode
    else:
        return {x.unicode for x in names}

sys.stdout = open(r'D:\temp\fr.txt', mode='w', encoding='utf_8_sig')

fontdir = r"D:\misc\Font\fonts"
fontfiles = [os.path.join(fontdir, x) for x in os.listdir(fontdir)]

for fontfile in fontfiles:
    print(fontfile)
    faces = [freetype.Face(fontfile)]
    faces += [freetype.Face(fontfile, i) for i in range(1, faces[0].num_faces)]
    for face in faces:
        #print("\t"*1, face.family_name, face.font_format)
        names = guess_sfnt_name(face, True)
        print(names)
        print()

sys.stdout.close()