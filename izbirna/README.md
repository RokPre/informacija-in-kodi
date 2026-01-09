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
# TODOS
- [ ] TODO: Implement run when pixels repeat.

