import argparse
import os
from timeit import default_timer
from pyaxmlparser import APK
from termcolor import cprint
from iappatcher_patcher.extractor import Extractor
from iappatcher_patcher.patcher import Patcher


def main():
    start = default_timer()
    parser = argparse.ArgumentParser(description="Bump Version")
    parser.add_argument("-path", "-p", dest="path", type=str, required=True)
    parser.add_argument(
        "-output", "-o", dest="output", type=str, default="patched.apk"
    )
    parser.add_argument(
        "--temp-path", dest="temp_path", type=str, default="./extracted"
    )
    args = parser.parse_args()
    if not os.path.exists(args.path) or not os.access(args.path, os.R_OK):
        cprint("[+] File doesn't exists or required reading permissions", color="red")
        exit(-1)
    if not args.path.endswith(".apk") or not args.output.endswith(".apk"):
        cprint(
            "[+] Input path and output path supposed to be a path to apk.", color="red"
        )
        exit(-1)
    extractor = Extractor(args.path, args.output, args.temp_path)
    extractor.extract_apk()
    patcher = Patcher(extractor)
    patcher.patch()
    extractor.compile_smali()
    extractor.sign_apk()
    print(f"It took {default_timer() - start} seconds to complete the run.")


if __name__ == "__main__":
    main()
