import struct
import sys
import zipfile
import shutil

def parse_string_pool(data, offset):
    string_count, style_count, flags, strings_start, styles_start = struct.unpack_from('<IIIII', data, offset + 8)
    is_utf8 = bool(flags & 0x100)
    offsets = struct.unpack_from(f'<{string_count}I', data, offset + 28)
    strings = []
    base = offset + strings_start
    for off in offsets:
        pos = base + off
        if is_utf8:
            def read_len(p):
                b = data[p]
                if b & 0x80:
                    b2 = data[p+1]
                    return ((b & 0x7f) << 8) | b2, p + 2
                return b, p + 1
            _, pos = read_len(pos)
            length, pos = read_len(pos)
            s = data[pos:pos+length].decode('utf-8', errors='replace')
        else:
            length = struct.unpack_from('<H', data, pos)[0]
            pos += 2
            s = data[pos:pos+length*2].decode('utf-16-le', errors='replace')
        strings.append(s)
    return strings

def get_string(strings, idx):
    if idx == -1 or idx >= len(strings):
        return None
    return strings[idx]

def patch_debuggable(manifest_bytes):
    data = bytearray(manifest_bytes)
    pos = 8
    strings = []
    patched = False

    while pos < len(data):
        if pos + 8 > len(data):
            break
        chunk_type, header_size, chunk_size = struct.unpack_from('<HHI', data, pos)
        if chunk_size == 0:
            break
        if chunk_type == 0x0001:
            strings = parse_string_pool(data, pos)
        elif chunk_type == 0x0102:  # START_ELEMENT
            p = pos + header_size
            ns, name_idx, attr_start, attr_size, attr_count, id_idx, class_idx, style_idx = struct.unpack_from('<iiHHHHHH', data, p)
            elem_name = get_string(strings, name_idx)
            p2 = p + attr_start
            for i in range(attr_count):
                a_ns, a_name, a_raw, a_size, a_res0, a_type, a_data = struct.unpack_from('<iiiHBBi', data, p2)
                attr_name = get_string(strings, a_name)
                if elem_name == 'application' and attr_name == 'debuggable' and a_data != 0:
                    data_offset = p2 + 16
                    struct.pack_into('<i', data, data_offset, 0)
                    patched = True
                    print(f"Patched debuggable flag to false at offset {data_offset}")
                p2 += attr_size
        pos += chunk_size

    return bytes(data), patched

def patch_apk(apk_path, output_path):
    shutil.copy(apk_path, output_path)
    with zipfile.ZipFile(apk_path, 'r') as zin:
        manifest_data = zin.read('AndroidManifest.xml')

    patched_manifest, was_patched = patch_debuggable(manifest_data)

    if not was_patched:
        print("No debuggable=true flag found (already false or not present). No changes made.")
        return False

    tmp_path = output_path + '.tmp'
    with zipfile.ZipFile(apk_path, 'r') as zin, zipfile.ZipFile(tmp_path, 'w', zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            if item.filename == 'AndroidManifest.xml':
                zout.writestr(item, patched_manifest)
            else:
                zout.writestr(item, zin.read(item.filename))
    shutil.move(tmp_path, output_path)
    print(f"Successfully wrote patched APK to {output_path}")
    return True

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python3 patch_debuggable.py <input.apk> <output.apk>")
        sys.exit(1)
    patch_apk(sys.argv[1], sys.argv[2])
