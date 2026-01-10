# Installing qoi viewer
```bash
git clone https://github.com/floooh/qoiview && cd qoiview
mkdir build && cd build
cmake ..
cmake --build .
cp qoiview /usr/local/bin
```

# QOI data structure
The qoi format has a 14-byte header. It is structured like this:
```C
file {
    qoi_header {
        char     magic[4];   // magic bytes "qoif"
        uint32_t width;      // image width in pixels (BE)
        uint32_t height;     // image height in pixels (BE)
        uint8_t  channels;   // 3 = RGB, 4 = RGBA
        uint8_t  colorspace; // 0 = sRGB with linear alpha
                             // 1 = all channels linear
    };
    data {
        uint8_t  index // First two bits are 00 the rest are indexes. 6-bit = 64 values
    };
    data {
        uint8_t diff // First two bits are 01 the rest are the differences in chanels. 
    };
    data { //RGB
        uint8_t tag // 11111110
        uint8_t red_chanel // 8-bit 256 values
        uint8_t green_chanel // 8-bit 256 values
        uint8_t blue_chanel // 8-bit 256 values
    };
    data { // RGBA
        uint8_t tag // 11111111
        uint8_t red_chanel // 8-bit 256 values
        uint8_t green_chanel // 8-bit 256 values
        uint8_t blue_chanel // 8-bit 256 values
        uint8_t alpha_chanel // 8-bit 256 values
    };
    qoi_end_marker {

    };
};
```

Encoder starting value is `{r: 0, g: 0, b: 0, a: 255}`.

Running array size is 64 bytes. 

Has function: $\text{index_position} = (3r + 5g + 7b + 11a) \% 64$.

```bash
cd /home/rok/sync/faks4/informacijaInKodi/izbirna/images/
rm * ../encoded/* ../decoded/*
wget https://qoiformat.org/qoi_test_images.zip
unzip qoi_test_images.zip && rm qoi_test_images.zip
mv qoi_test_images/* . && rm qoi_test_images
rm kodim23.png kodim10.png
wget https://www.kaggle.com/api/v1/datasets/download/sherylmehta/kodak-dataset
unzip kodak-dataset && rm kodak-dataset
cd ..
source .venv/bin/activate
python3 qoi_encoder.py images/*.png && mv images/*.qoi encoded/
python3 qoi_decoder.py encoded/*.qoi && mv encoded/*.png decoded/
feh decoded/*
```

```bash
cd /home/rok/sync/faks4/informacijaInKodi/izbirna/
python3 qoi_encoder.py images/kodim23.png
rm log_kodim23.log && xxd images/kodim23.qoi >> log_kodim23.log
rm log_kodim23_original.log && xxd images/kodim23.qoi.bak >> log_kodim23_original.log
diff log_kodim23_original.log log_kodim23.log
```


# TODOS
