"""Bounded ISO9660 reader for single-track raw MODE2/2352 Integral BIN images."""
import struct

def read_user_bin(image, sector):
    start = sector * 2352
    raw = image[start:start + 2352]
    if len(raw) != 2352 or raw[:12] != bytes.fromhex('00ffffffffffffffffffff00'):
        raise ValueError(f'Invalid or truncated raw sector {sector}')
    if raw[15] == 1:
        return raw[16:2064]
    if raw[15] == 2 and raw[16:20] == raw[20:24] and not raw[18] & 0x20:
        return raw[24:2072]
    raise ValueError(f'Unsupported sector mode/form at {sector}')

def read_file(reader, image, extent, size):
    if extent < 0 or size < 0 or (extent + (size + 2047)//2048)*2352 > len(image):
        raise ValueError('ISO file exceeds image bounds')
    return b''.join(reader(image, extent+i) for i in range((size+2047)//2048))[:size]

def parse_directory_entries(data):
    entries = {}
    at = 0
    while at < len(data):
        length = data[at]
        if not length:
            at = (at//2048+1)*2048
            continue
        if length < 34 or at+length > len(data):
            raise ValueError('Malformed ISO directory record')
        row = data[at:at+length]
        name = row[33:33+row[32]]
        if name not in (b'\0', b'\1'):
            key = name.decode('ascii').split(';')[0].upper()
            entries[key] = (struct.unpack_from('<I',row,2)[0],struct.unpack_from('<I',row,10)[0],row[25])
        at += length
    return entries

def resolve_iso_file(reader, image, root, path):
    entries = root
    components = path.upper().split('/')
    for index,name in enumerate(components):
        if name not in entries:
            raise ValueError(f'ISO file not found: {path}')
        extent,size,flags = entries[name]
        if index < len(components)-1:
            if not flags & 2:
                raise ValueError('Expected ISO directory')
            entries = parse_directory_entries(read_file(reader,image,extent,size))
    return extent,size

def root_directory(image):
    pvd = read_user_bin(image,16)
    if pvd[:7] != b'\x01CD001\x01':
        raise ValueError('Not an ISO9660 raw BIN image')
    return parse_directory_entries(read_file(read_user_bin,image,struct.unpack_from('<I',pvd,158)[0],struct.unpack_from('<I',pvd,166)[0]))
