# -*- coding: utf-8 -*-
"""Research helper: dump attributes / tabular sections / dimensions of 1C dump XML objects."""
import io, os, re, sys

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")

OBJ = {
    "Catalogs": ["ar_Диалоги", "ar_Агенты", "ar_ДополнительныеНастройки", "ar_ПрофилиЗапуска", "ar_ПодпискиАгентов"],
    "InformationRegisters": ["ar_СообщенияДиалога", "ar_Запуски", "ar_ОчередьApproval", "ar_Сессии", "ar_СобытияЗапуска"],
    "Enums": ["ar_КаналУведомления", "ar_РольОтветственного", "ar_СтатусЗапуска"],
}


def child_text(block, tag):
    m = re.search(r"<%s>(.*?)</%s>" % (tag, tag), block, re.S)
    return m.group(1).strip() if m else ""


def dump_obj(kind, name):
    path = os.path.join(SRC, kind, name, name + ".xml")
    if not os.path.exists(path):
        path = os.path.join(SRC, kind, name + ".xml")
    if not os.path.exists(path):
        print("## %s.%s — NOT FOUND" % (kind, name))
        return
    s = io.open(path, encoding="utf-8-sig").read()
    print("## %s.%s" % (kind, name))
    # synthetic flag, parents for enums
    syn = child_text(s, "InternalInfo")
    m = re.search(r"<synthetic>([^<]+)</synthetic>", s)
    for kindname, inner in (("Attribute", r"<Attribute>(.*?)</Attribute>"),
                            ("TabularSection", r"<TabularSection>(.*?)</TabularSection>"),
                            ("Dimension", r"<Dimension>(.*?)</Dimension>"),
                            ("Resource", r"<Resource>(.*?)</Resource>")):
        for m in re.finditer(inner, s, re.S):
            b = m.group(1)
            nm = child_text(b, "Name")
            types = re.findall(r"<Type>([^<]+)</Type>", b)
            strn = re.search(r"<StringLength>(\d+)</StringLength>", b)
            idx = child_text(b, "Indexing")
            kind_of = child_text(b, "Type")
            leading = child_text(b, "Leading")
            main = child_text(b, "Main")
            master = child_text(b, "Master")
            extra = []
            if strn: extra.append("len=%s" % strn.group(1))
            if idx and idx.lower() != "nonedontindex": extra.append("index=%s" % idx)
            if leading.lower() == "true": extra.append("leading")
            if master: extra.append("master=%s" % master)
            print("  %s %s: %s %s" % (kindname, nm, ",".join(types), " ".join(extra)))
    # standard attributes: use standard commands?
    std = re.findall(r"<(StandardAttribute)>(.*?)</\1>", s, re.S)
    # for enums: value list
    for m in re.finditer(r"<Value>(.*?)</Value>", s, re.S):
        print("  EnumValue:", child_text(m.group(1), "Name"), "|", child_text(m.group(1), "Name"))
    print()


for kind, names in OBJ.items():
    for n in names:
        dump_obj(kind, n)
