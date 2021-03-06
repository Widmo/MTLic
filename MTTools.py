#!/usr/bin/python3

import sys
import struct
from SHA256 import SHA256

SWIDTab = b'TN0BYX18S5HZ4IA67DGF3LPCJQRUK9MW2VE'

SHA256_K = (
    0x0548D563, 0x98308EAB, 0x37AF7CCC, 0xDFBC4E3C,
    0xF125AAC9, 0xEC98ACB8, 0x8B540795, 0xD3E0EF0E,
    0x4904D6E5, 0x0DA84981, 0x9A1F8452, 0x00EB7EAA,
    0x96F8E3B3, 0xA6CDB655, 0xE7410F9E, 0x8EECB03D,
    0x9C6A7C25, 0xD77B072F, 0x6E8F650A, 0x124E3640,
    0x7E53785A, 0xE0150772, 0xC61EF4E0, 0xBC57E5E0,
    0xC0F9A285, 0xDB342856, 0x190834C7, 0xFBEB7D8E,
    0x251BED34, 0x0E9F2AAD, 0x256AB901, 0x0A5B7890,
    0x9F124F09, 0xD84A9151, 0x427AF67A, 0x8059C9AA,
    0x13EAB029, 0x3153CDF1, 0x262D405D, 0xA2105D87,
    0x9C745F15, 0xD1613847, 0x294CE135, 0x20FB0F3C,
    0x8424D8ED, 0x8F4201B6, 0x12CA1EA7, 0x2054B091,
    0x463D8288, 0xC83253C3, 0x33EA314A, 0x9696DC92,
    0xD041CE9A, 0xE5477160, 0xC7656BE8, 0x5179FE33,
    0x1F4726F1, 0x5F393AF0, 0x26E2D004, 0x6D020245,
    0x85FDF6D7, 0xB0237C56, 0xFF5FBD94, 0xA8B3F534 )

SHA256_I = (
    0x5B653932, 0x7B145F8F, 0x71FFB291, 0x38EF925F,
    0x03E1AAF9, 0x4A2057CC, 0x4CAF4DD9, 0x643CC9EA )

class MT_SHA256(SHA256):
    K = SHA256_K
    INITIAL_STATE = SHA256.State(*SHA256_I)

def MTBse64Encode(s, padd = False):
    b64s = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    b64p = "="
    ret = ""
    left = 0
    for i in range(0, len(s)):
        if left == 0:
            ret += chr(b64s[s[i] & 0x3F])
            left = 2
        else:
            if left == 6:
                ret += chr(b64s[s[i - 1] >> 2])
                ret += chr(b64s[s[i] & 0x3F])
                left = 2
            else:
                index1 = s[i - 1] >> (8 - left)
                index2 = s[i] << (left)
                index = (index1 | index2) & 0x3F
                ret += chr(b64s[index])
                left += 2
    if left != 0:
        ret += chr(b64s[s[len(s) - 1] >> (8 - left)])
    if(padd):
        for i in range(0, (4 - len(ret) % 4) % 4):
            ret += b64p
    return ret

def MTBse64Decode(s):
    b64s = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    b64p = "="
    ret = b""
    s2 = str.encode(s.replace(b64p, ""))
    left = 0
    for i in range(0, len(s2)):
        if left == 0:
            left = 6
        else:
            value1 = b64s.index(s2[i - 1]) >> (6 - left)
            value2 = b64s.index(s2[i]) & (2 ** (8 - left) - 1)
            value = value1 | (value2 << left)
            ret += bytes([value])
            left -= 2
    return ret

# rotate n left by d bits
def rotl(n, d):

    # In n<<d, last d bits are 0.
    # To put first 3 bits of n at
    # last, do bitwise or of n<<d
    # with n >>(INT_BITS - d)
    return (n << d)|(n >> (32 - d))

# rotate n right by d bits
def rotr(n, d):

    # In n>>d, first d bits are 0.
    # To put last 3 bits of at
    # first, do bitwise or of n>>d
    # with n <<(INT_BITS - d)
    return (n >> d)|(n << (32 - d)) & 0xFFFFFFFF

def to32bits(val):
    return (val + (1 << 32)) % (1 << 32)

def swap32(val):
    return ((val << 24) & 0xFF000000) | \
           ((val <<  8) & 0x00FF0000) | \
           ((val >>  8) & 0x0000FF00) | \
           ((val >> 24) & 0x000000FF)

def printBytes(val):
    for i in range(len(val) // 16):
        print(''.join('{:02x} '.format(x) for x in val[i*16:i*16+16]))

def MT_Transform(s):
    s = list(struct.unpack('>'+'I'*(len(s) // 4), s))
    for i in range(16):
        s[(i+2) % 4] = to32bits(s[(i+2) % 4] - s[(i+0) % 4] - SHA256_K[i*4+0])
        s[(i+3) % 4] = to32bits((rotl(s[(i+0) % 4], SHA256_K[i*4+0] & 0x0F) ^ s[(i+3) % 4]) + s[(i+0) % 4])

        s[(i+1) % 4] = to32bits(s[(i+1) % 4] - s[(i+3) % 4] - SHA256_K[i*4+1])
        s[(i+2) % 4] = to32bits((rotl(s[(i+1) % 4], SHA256_K[i*4+1] & 0x0F) ^ s[(i+2) % 4]) + s[(i+1) % 4])

        s[(i+0) % 4] = to32bits(s[(i+0) % 4] - s[(i+2) % 4] - SHA256_K[i*4+2])
        s[(i+1) % 4] = to32bits((rotl(s[(i+2) % 4], SHA256_K[i*4+2] & 0x0F) ^ s[(i+1) % 4]) + s[(i+2) % 4])

        s[(i+3) % 4] = to32bits(s[(i+3) % 4] - s[(i+1) % 4] - SHA256_K[i*4+3])
        s[(i+0) % 4] = to32bits((rotl(s[(i+3) % 4], SHA256_K[i*4+3] & 0x0F) ^ s[(i+0) % 4]) + s[(i+3) % 4])

    ret = b''
    for x in s:
      ret += x.to_bytes(4, 'big')

    return ret

def MT_TransformRev(s):
    s = list(struct.unpack('>'+'I'*(len(s) // 4), s))
    for i in reversed(range(16)):
        s[(i+0) % 4] = to32bits(rotl(s[(i+3) % 4], SHA256_K[i*4+3] & 0x0F) ^ (s[(i+0) % 4] - s[(i+3) % 4]))
        s[(i+3) % 4] = to32bits(s[(i+3) % 4] + s[(i+1) % 4] + SHA256_K[i*4+3])

        s[(i+1) % 4] = to32bits(rotl(s[(i+2) % 4], SHA256_K[i*4+2] & 0x0F) ^ (s[(i+1) % 4] - s[(i+2) % 4]))
        s[(i+0) % 4] = to32bits(s[(i+0) % 4] + s[(i+2) % 4] + SHA256_K[i*4+2])

        s[(i+2) % 4] = to32bits(rotl(s[(i+1) % 4], SHA256_K[i*4+1] & 0x0F) ^ (s[(i+2) % 4] - s[(i+1) % 4]))
        s[(i+1) % 4] = to32bits(s[(i+1) % 4] + s[(i+3) % 4] + SHA256_K[i*4+1])

        s[(i+3) % 4] = to32bits(rotl(s[(i+0) % 4], SHA256_K[i*4+0] & 0x0F) ^ (s[(i+3) % 4] - s[(i+0) % 4]))
        s[(i+2) % 4] = to32bits(s[(i+2) % 4] + s[(i+0) % 4] + SHA256_K[i*4+0])

    ret = b''
    for x in s:
      ret += x.to_bytes(4, 'big')

    return ret

def MT_Hash(data):
    return bytearray(MT_SHA256(data).digest())

def MT_SWSNToSWID(s):
    ret = ""
    for i in range(8):
        ret += chr(SWIDTab[s % 0x23])
        s = s // 0x23
        if i == 3:
            ret += '-'

    return ret

def MT_SWIDToSWSN(s):
    ret = 0
    s = s.replace('-', '')
    for i in reversed(range(len(s))):
        ret = ret*0x23 + SWIDTab.index(ord(s[i]))

    return ret
