# 1. del: Kodne tabele za slovenske znake

V prvem delu laboratorijske vaje je bilo potrebno generirati tabele, ki prikazujejo kodiranje znakov **"čšžČŠŽ"** v različnih kodnih tabelah (IBM-852, ISO-8859-2, Windows-1250, MacCE, UTF-8, UTF-16LE, UTF-16BE).

Program zaženemo z ukazom:

```bash
python3 zamenjave.py
````

V terminalu se izpišejo tabele.
Primer (ISO-8859-2):

| znak | dec | heks | bin      |
| ---- | --- | ---- | -------- |
| č    | 232 | E8   | 11101000 |
| š    | 185 | B9   | 10111001 |
| ž    | 190 | BE   | 10111110 |
| Č    | 200 | C8   | 11001000 |
| Š    | 169 | A9   | 10101001 |
| Ž    | 174 | AE   | 10101110 |

# 2. del: Pretvorba Unicode kodnih točk v UTF-8

Drugi del vaje zahteva program, ki iz vhodne datoteke prebere seznam Unicode kodnih točk, vsako preveri in ročno pretvori v UTF-8 zapis, ter ustvari tabelo vseh unikatnih znakov skupaj z njihovimi desetiškimi, šestnajstiškimi in binarnimi vrednostmi.

Implementacija se nahaja v datoteki **`main.py`**.

Program zaženemo z:

```bash
python3 main.py <input_file> <output_file> <table_output_file>
```

Primer:

```bash
python3 main.py kodneTocke.txt kodneTockeUnicode.txt kodneTockeTabela.txt
```

Program bo ustvaril dve datoteki:
- v prvi bo prevedeno besedilo,
- v drugi pa tabela vseh unikatnih znakov, razvrščenih po Unicode vrednosti, skupaj z njihovimi desetiškimi, šestnajstiškimi in binarnimi kodnimi zamenjavami.

# 3. del: Poročilo
Poročilo v PDF obliki se nahaja v `porocilo.pdf`, ter njegova surova oblika v `porocilo.tex`.
