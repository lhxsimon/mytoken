import platform
from ctypes import cdll, c_char_p
from time import time


def validate_license():
    # load libtoken.so
    dll_file = "libtoken.so"

    if platform.system() == "Darwin":
        dll_file = "libtoken_darwin.so"
    elif platform.system() == "Linux":
        dll_file = 'libtoken_linux.so'
    else:
        print("Cannot support system: ", platform.system())
        exit(1)

    libtoken = cdll.LoadLibrary("../assets/{}".format(dll_file))
    libtoken.GetKey.argtypes = [c_char_p, c_char_p]
    libtoken.GetKey.restype = c_char_p

    # check license
    with open("./license.dat", "r", encoding='utf-8') as f:
        license = f.read()

    check_license(license, libtoken)


def check_license(license, libtoken):
    if license is None or license == "":
        print("License data error!")
        exit(1)

    license_time = license.split(":")[0]
    timestamp = int(time())

    if timestamp > int(license_time):
        print("License time out")
        exit(1)

    timestamp = str(timestamp).encode('utf-8')
    license = license.encode('utf-8')
    code = libtoken.GetKey(timestamp, license).decode('utf-8')

    if code.startswith('error'):
        print("License libtoken.so error")
        exit(1)

    print("License status ok!")


if __name__ == '__main__':
    validate_license()
