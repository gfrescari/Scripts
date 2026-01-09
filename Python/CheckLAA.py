import sys
import struct

def check_laa_support(exe_path):
    try:
        with open(exe_path, 'rb') as f:
            # Read MS-DOS header to get PE header offset
            f.seek(0x3C)
            pe_offset = struct.unpack('<I', f.read(4))[0]

            # Go to PE header and check signature
            f.seek(pe_offset)
            if f.read(4) != b'PE\x00\x00':
                print("Not a valid PE file.")
                return

            # Skip COFF Header (20 bytes), then read Optional Header Magic
            f.seek(pe_offset + 0x18)
            magic = struct.unpack('<H', f.read(2))[0]

            is_pe32_plus = (magic == 0x20B)  # PE32+ (64-bit)
            f.seek(pe_offset + 0x18)  # Reset pointer to Optional Header

            # Read Characteristics (2 bytes at offset +0x16 from PE header)
            f.seek(pe_offset + 0x16)
            characteristics = struct.unpack('<H', f.read(2))[0]

            # Check the DLL characteristics field for LAA
            f.seek(pe_offset + 0x18 + 0x46)  # Offset to DllCharacteristics
            dll_characteristics = struct.unpack('<H', f.read(2))[0]

            # Go back and read the FileHeader.Characteristics field
            f.seek(pe_offset + 0x16)
            flags = struct.unpack('<H', f.read(2))[0]

            IMAGE_FILE_LARGE_ADDRESS_AWARE = 0x20

            if flags & IMAGE_FILE_LARGE_ADDRESS_AWARE:
                print(f"[+] {exe_path} supports Large Address Aware (LAA).")
            else:
                print(f"[-] {exe_path} does NOT support Large Address Aware (LAA).")

    except Exception as e:
        print(f"Error: {e}")

# Example usage
if __name__ == "__main__":
    exe_file = sys.argv[1] if len(sys.argv) > 1 else input("Enter path to EXE file: ")
    check_laa_support(exe_file)
