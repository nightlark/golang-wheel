import os
import json
import platform
import requests
import tarfile
import zipfile

with open("go_downloads.json") as dl_file:
    data  = json.load(dl_file)

os_name = platform.system().lower()
if os_name == "darwin":
    os_name = "macos"

arch_name = platform.machine().lower()
if arch_name.lower() in ("aarch64"):
    arch_name = "arm64"
if arch_name.lower() in ("x86_64", "amd64"):
    arch_name = "x86-64"
if arch_name.lower() in ("i386", "i486", "i586", "i686"):
    arch_name = "x86"

# system, machine
# SunOS, sun4u
# Linux, riscv64
# Linux, riscv32
# Linux, ppc64le
# Linux, ppc64
# Linux, mips64
# OpenBSD, octeon //mips64 processor
# AIX, 00F9C1964C0 //gcc119 powerpc
# AIX, 00F84C0C4C00 //gcc111 powerpc
# OpenBSD, amd64

data = [e for e in data if ("kind" in e and e["kind"] == "Archive") and ("arch" in e and e["arch"].lower() == arch_name) and ("os" in e and e["os"].lower() == os_name)]

if len(data) == 1:
    dl_info = data[0]

def download_file(url, destination):
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    with open(destination, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                file.write(chunk)

download_file(dl_info["download_url"], dl_info["file_name"])


def extract_file(file_path, destination):
    file_name, file_extension = os.path.splitext(file_path)
    
    if file_extension == '.zip':
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(destination)
    elif file_extension == '.tar':
        with tarfile.open(file_path, 'r') as tar_ref:
            tar_ref.extractall(destination)
    elif file_extension == '.gz' or file_extension == '.tar.gz':
        with tarfile.open(file_path, 'r:gz') as tar_ref:
            tar_ref.extractall(destination)
    elif file_extension == '.bz2' or file_extension == '.tar.bz2':
        with tarfile.open(file_path, 'r:bz2') as tar_ref:
            tar_ref.extractall(destination)
    else:
        raise ValueError(f"Unsupported file format: {file_extension}")

extract_file(dl_info["file_name"], "go_install")

