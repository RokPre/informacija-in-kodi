import hashlib


def compress(text: bytes):
    dict_size = 256
    dictionary = {bytes([i]): i for i in range(dict_size)}

    encoded = []
    w = bytes([text[0]])

    for c in text[1:]:
        wc = w + bytes([c])
        if wc in dictionary:
            w = wc
        else:
            encoded.append(dictionary[w])
            dictionary[wc] = dict_size
            dict_size += 1
            w = bytes([c])

    encoded.append(dictionary[w])
    return encoded


def dekompresiraj(codes: list[int]) -> bytes:
    dict_size = 256
    dictionary = {i: bytes([i]) for i in range(dict_size)}

    result = []

    prev = dictionary[codes[0]]
    result.append(prev)

    for code in codes[1:]:
        if code in dictionary:
            entry = dictionary[code]
        else:
            # poseben LZW primer (KwKwK)
            entry = prev + prev[:1]

        result.append(entry)
        dictionary[dict_size] = prev + entry[:1]
        dict_size += 1

        prev = entry

    return b"".join(result)


def izracunaj_velikost(KT: list[int]) -> int:
    total_bits = len(KT) * 12
    return (total_bits + 7) // 8


if __name__ == "__main__":
    files = ["besedilo.txt", "posnetek.mp3", "slika.bmp"]

    for file in files:
        print(file)
        # 1. Preberi besedilno datoteko
        with open(file, "rb") as f:
            original = f.read()

        # 2. LZW kompresija
        compressed = compress(original)

        # 3. Shranimo komprimirane kode kot TEXT (zahteve vaje)
        with open(f"compressed_{file}", "w") as f:
            f.write(",".join(map(str, compressed)))

        # 4. LZW dekompresija (tvoja funkcija)
        decompressed = dekompresiraj(compressed)

        # 5. Shranimo dekompresirano datoteko
        with open(f"decompressed_{file}", "wb") as f:
            f.write(decompressed)

        # 6. MD5 preverjanje pravilnosti
        print("MD5 original:    ", hashlib.md5(original).hexdigest())
        print("MD5 dekompresija:", hashlib.md5(decompressed).hexdigest())

        if hashlib.md5(original).digest() == hashlib.md5(decompressed).digest():
            print("OK – Datoteke se ujemajo.")
        else:
            print("NAPAKA – Ne ujemata se!")

        # 7. Izračun "gospodarnosti" kompresije
        vel_original = len(original)
        vel_kompresirano = izracunaj_velikost(compressed)

        print("\nVelikost originalne datoteke:", vel_original, "B")
        print("Ocenjena velikost LZW:", vel_kompresirano, "B")
        print("Razmerje:", round(vel_original / vel_kompresirano, 3))

    import math

    with open("besedilo.txt", "rb") as f:
        data = f.read()

    for p in range(10, 110, 10):
        n = math.floor(len(data) * (p / 100))
        partial = data[:n]

        compressed = compress(partial)
        estimated = izracunaj_velikost(compressed)

        print(f"{p}%: original={n}B  LZW={estimated}B  ratio={n/estimated:.3f}")
