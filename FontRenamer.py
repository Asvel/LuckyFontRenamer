# -*- coding: utf-8 -*-

import os
import sys
import re

sys.path.append(os.path.dirname(__file__))
import freetype

def paser_sfnt_name(face, autochoose=True):
    names = [face.get_sfnt_name(i) for i in range(face.sfnt_name_count)]
    langs = {x.language_id for x in names}
    names = [x for x in names if x.name_id == 4]
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
        name.unicode = s
    if autochoose:
        pass
    else:
        return names#{x.unicode for x in names}

sys.stdout = open(r'D:\temp\fr.txt', mode='w', encoding='utf_8_sig')

fontdir = r"D:\misc\Font\fonts"
fontfiles = [os.path.join(fontdir, x) for x in os.listdir(fontdir)]

for fontfile in fontfiles:
    print(fontfile)
    faces = [freetype.Face(fontfile)]
    faces += [freetype.Face(fontfile, i) for i in range(1, faces[0].num_faces)]
    for face in faces:
        print("\t"*1, face.family_name, face.font_format)
        names = paser_sfnt_name(face, False)
        for name in names:
            print("\t"*2,
                str(name.name_id).rjust(2),
                str(name.platform_id).rjust(2),
                str(name.encoding_id).rjust(2),
                str(name.language_id).rjust(4),
                name.encoding.ljust(10),
                name.unicode.ljust(100),
                name.string)
        print()

sys.stdout.close()