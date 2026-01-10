# About
`my_qoi.py` je python module.

Ima dve funkciji `encode` in `decode`.

## Encdoe
Funkcija `enkode` ima 1 vhod, ta je ime datoteke, ki jo hočemo prebrati in pretvoriti v format `QOI`.
Funkcija `decode` ima 1 vhod, ta je ime datoteke, ki jo hočemo prebrati in pretvoriti iz formata `QOI`. 

# Test
Za validacijo delovanja lahko zaženemo datoteko `qoi_test.py`. Ta bo prebrala datoteke mape in jih pretvorila v `QOI` format in jih shranila. Tem lahko preverimo validnost z katerim koli program, ki podpira `QOI` format. Potem datoteka prebere shranjene datoteke in jih pretvori nazaj v originalni format, ter primerja pidatke pikslov. 

# Podatki
Slike za previrjanje delovanja so bile pridobljene iz dveh virov:
https://qoiformat.org/qoi_test_images.zip
https://www.kaggle.com/api/v1/datasets/download/sherylmehta/kodak-dataset
