import platform
import json

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

