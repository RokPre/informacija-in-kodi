slovenski_znaki = "čšžČŠŽ"

encodings = {
    "IBM-852": "cp852",
    "ISO-8859-2": "iso-8859-2",
    "Windows-1250": "cp1250",
    "MacCE": "mac_latin2",
    "UTF-8": "utf-8",
    "UTF-16LE": "utf-16le",
    "UTF-16BE": "utf-16be",
}

for nice_name, codec in encodings.items():
    print(f" # {nice_name}")
    print("| znak | dec | heks | bin |")
    print("| ---- | --- | ---- | --- |")
    for znak in slovenski_znaki:
        try:
            b = znak.encode(codec)
        except UnicodeEncodeError:
            print(f"|{znak}|{nice_name}|(ni mogoče kodirati)| | |")
            continue

        decs = int.from_bytes(b)
        hexs = " ".join(f"{x:02X}" for x in b)
        bins = " ".join(f"{x:08b}" for x in b)

        print(f"| {znak} | {decs} | {hexs} | {bins} |")

    print()
