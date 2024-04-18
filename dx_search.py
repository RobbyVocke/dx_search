import os
import sys
import shutil

def create_new_file(search_term, index):
    file_path = os.path.join("dx_search", search_term, f"{search_term}{index}.syx")
    file = open(file_path, "wb")
    for hex_value in hex_header:
        file.write(bytes.fromhex(hex_value[2:]))
    return file

def fill_syx(file):
    global patches_to_write, patches_written, checksum_total
    count = 0
    while patches_written < 32:
        if patches_to_write:
            filename, patch_num = patches_to_write.pop(0)
            write_patch(file, filename, patch_num)
        else:
            write_blank_patch(file)
    write_sysex_footer(file)
    file.close()

def write_sysex_footer(file):
    global checksum_total
    file.write(calculate_checksum(checksum_total))
    file.write(bytes([0xF7]))

def write_blank_patch(file):
    global checksum_total, patches_written
    for byte in blank_patch:
        checksum_total += int.from_bytes(byte, byteorder='big')
        file.write(byte)
    patches_written += 1

def write_patch(file, file_path, patch_num):
    global checksum_total, patches_written
    with open(file_path, "rb") as patch_file:
        patch_file.seek(0x06 + (patch_num*128))
        for _ in range(128):
            byte = patch_file.read(1)
            file.write(byte)
            checksum_total += int.from_bytes(byte, byteorder='big')
    patches_written += 1

def calculate_checksum(checksum):
    checksum_twos_comp = -(checksum & 0xFF) & 0xFF
    checksum_masked = checksum_twos_comp & 0x7F
    return bytes([checksum_masked])

def normalize_pgm_name(sysex_name):
    buffer = list(sysex_name[:10])
    for i in range(len(buffer)):
        c = buffer[i]
        if c < 32 or c > 126:
            buffer[i] = 32
        else:
            buffer[i] = c & 0x7F
    return bytes(buffer).decode('ascii', 'ignore').strip()

def scan_patches(filename, search):
    global patches_to_write, text_file
    with open(filename, 'rb') as file:
        for i in range(0, 32):
            file.seek(offset + (step * i))
            name = file.read(10)
            normalized_name = normalize_pgm_name(name)
            if search.lower() in normalized_name.lower():
                patches_to_write.append([filename, i])
                text_file.write("\n"+filename+"\n"+normalized_name+"\n---------------\n")

def syx_scan(directory, search):
    for root, dirs, files in os.walk(directory):
        if "dx_search" in root:
            continue  # Skip the 'dx_search' directory
        for file in files:
            if file.endswith('.syx'):
                full_path = os.path.join(root, file)
                scan_patches(full_path, search)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script_name.py <search_term>")
        sys.exit(1)

    search_term = sys.argv[1]

    patches_to_write = []
    checksum_total = 0
    patches_written = 0
    current_directory = os.getcwd()
    hex_header = ["0xF0", "0x43", "0x00", "0x09", "0x20", "0x00"]
    offset = 0x7c
    step = 0x80
    blank_patch = [b'c', b'c', b'c', b'c', b'c', b'c', b'c', b'\x00', b'\x00', b'\x00', b'\x00', b'\x00', b'8', b'\x00', b'\x00', b'\x02', b'\x00', b'c', b'c', b'c', b'c', b'c', b'c', b'c', b'\x00', b'\x00', b'\x00', b'\x00', b'\x00', b'8', b'\x00', b'\x00', b'\x02', b'\x00', b'c', b'c', b'c', b'c', b'c', b'c', b'c', b'\x00', b'\x00', b'\x00', b'\x00', b'\x00', b'8', b'\x00', b'\x00', b'\x02', b'\x00', b'c', b'c', b'c', b'c', b'c', b'c', b'c', b'\x00', b'\x00', b'\x00', b'\x00', b'\x00', b'8', b'\x00', b'\x00', b'\x02', b'\x00', b'c', b'c', b'c', b'c', b'c', b'c', b'c', b'\x00', b'\x00', b'\x00', b'\x00', b'\x00', b'8', b'\x00', b'\x00', b'\x02', b'\x00', b'c', b'c', b'c', b'c', b'c', b'c', b'c', b'\x00', b'\x00', b'\x00', b'\x00', b'\x00', b'8', b'\x00', b'c', b'\x02', b'\x00', b'c', b'c', b'c', b'c', b'2', b'2', b'2', b'2', b'\x00', b'\x08', b'#', b'\x00', b'\x00', b'\x00', b'1', b'\x18', b' ', b' ', b' ', b' ', b' ', b' ', b' ', b' ', b' ', b' ']

    search_folder_path = os.path.join("dx_search", search_term)

    if os.path.exists(search_folder_path):
        shutil.rmtree(search_folder_path)

    os.makedirs(search_folder_path)

    text_file_path = os.path.join(search_folder_path, f"{search_term}.txt")
    text_file = open(text_file_path, 'w')
    text_file.write('--------------\n')

    syx_scan(current_directory, search_term)

    file_index = 0
    while patches_to_write:
        file = create_new_file(search_term, file_index)
        fill_syx(file)
        patches_written = 0
        checksum_total = 0
        file_index += 1

    text_file.close()
