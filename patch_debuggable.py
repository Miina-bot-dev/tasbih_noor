#!/usr/bin/env python3
"""
patch_debuggable.py

Flips android:debuggable from true to false inside the compiled
AndroidManifest.xml of an unsigned APK, by editing the binary AXML
directly (no apktool / decompile needed).

Usage:
    python3 patch_debuggable.py <input.apk> <output.apk>
"""
import sys
import struct
import zipfile

RES_STRING_POOL_TYPE = 0x0001
UTF8_FLAG = 1 << 8
TYPE_INT_BOOLEAN = 0x12


def parse_string_pool(data, chunk_start):
    header_type, header_size, chunk_size = struct.unpack_from('<HHI', data, chunk_start)
    if header_type != RES_STRING_POOL_TYPE:
        raise ValueError("Expected string pool chunk, got 0x%04x" % header_type)

    string_count, style_count, flags, strings_start, styles_start = struct.unpack_from(
        '<IIIII', data, chunk_start + 8
    )
    is_utf8 = bool(flags & UTF8_FLAG)
    offsets_base = chunk_start + header_size
    offsets = struct.unpack_from('<%dI' % string_count, data, offsets_base)
    strings_base = chunk_start + strings_start

    strings = []
    for off in offsets:
        pos = strings_base + off
        if is_utf8:
            first = data[pos]
            pos += 2 if (first & 0x80) else 1
            first2 = data[pos]
            if first2 & 0x80:
                length = ((first2 & 0x7F) << 8) | data[pos + 1]
                pos += 2
            else:
                length = first2
                pos += 1
            s = bytes(data[pos:pos + length]).decode('utf-8', errors='replace')
        else:
            first = struct.unpack_from('<H', data, pos)[0]
            if first & 0x8000:
                length = ((first & 0x7FFF) << 16) | struct.unpack_from('<H', data, pos + 2)[0]
                pos += 4
            else:
                length = first
                pos += 2
            s = bytes(data[pos:pos + length * 2]).decode('utf-16-le', errors='replace')
        strings.append(s)
    return strings, chunk_size


def patch_manifest(manifest_bytes):
    data = bytearray(manifest_bytes)

    file_type, file_header_size, file_size = struct.unpack_from('<HHI', data, 0)
    if file_type != 0x0003:
        raise ValueError(
            "Not a valid binary AndroidManifest.xml (unexpected root chunk type 0x%04x)" % file_type
        )

    pool_offset = file_header_size
    strings, _ = parse_string_pool(data, pool_offset)

    try:
        target_index = strings.index("debuggable")
    except ValueError:
        return bytes(data), 0

    patched = 0
    name_pattern = struct.pack('<I', target_index)
    i = 0
    n = len(data)

    while True:
        idx = data.find(name_pattern, i)
        if idx == -1:
            break
        i = idx + 1

        # ResXMLTree_attribute layout: ns(4) name(4) rawValue(4) typedValue{size2,res0,1,dataType1,data4}
        tv_off = idx + 8
        if tv_off + 8 > n:
            continue

        size, res0, data_type = struct.unpack_from('<HBB', data, tv_off)
        value = struct.unpack_from('<I', data, tv_off + 4)[0]

        if size == 8 and data_type == TYPE_INT_BOOLEAN and value == 0xFFFFFFFF:
            struct.pack_into('<I', data, tv_off + 4, 0x00000000)
            patched += 1

    return bytes(data), patched


def main():
    if len(sys.argv) != 3:
        print("Usage: python3 patch_debuggable.py <input.apk> <output.apk>")
        sys.exit(1)

    src, dst = sys.argv[1], sys.argv[2]

    with zipfile.ZipFile(src, 'r') as zin:
        if 'AndroidManifest.xml' not in zin.namelist():
            print("ERROR: AndroidManifest.xml not found inside the APK")
            sys.exit(1)

        manifest = zin.read('AndroidManifest.xml')
        patched_manifest, count = patch_manifest(manifest)

        if count == 0:
            print("No android:debuggable=true flag found (already safe). Copying APK unchanged.")
        else:
            print(f"Patched {count} occurrence(s) of android:debuggable -> false")

        with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                content = zin.read(item.filename)
                if item.filename == 'AndroidManifest.xml':
                    content = patched_manifest
                zi = zipfile.ZipInfo(item.filename, date_time=item.date_time)
                zi.compress_type = item.compress_type
                zi.external_attr = item.external_attr
                zout.writestr(zi, content)

    print(f"Wrote patched APK to {dst}")


if __name__ == '__main__':
    main()
