import os
import sys
import subprocess

try:
  import colorama
except:
  try:
    if not input("[!] grab.py requires 'colorama' (from pip). Install (y/n)? ").startswith('y'):
      raise Exception()
  except:
    print("\nAborting.")
    sys.exit(1)

  subprocess.run([sys.executable, "-m", "pip", "--no-input", "--no-color", "--no-clean", "install", "colorama"], stdout=subprocess.DEVNULL)

colorama.just_fix_windows_console()

print("---------------------------------------------------------------------")
print("Grab.py is a dependency management tool for Python."                        )
print("To use it, installation is required. This will modify your Python stdlib.")
print("Do you want to install (y/n)? "                                                                      )
print("---------------------------------------------------------------------")

CSI =  "\x1b["

print(f"{CSI}2F",   end='')  # move 2 lines up
print(f"{CSI}31G", end='')  # move 10 right

try:
  if not input().startswith('y'):
    raise Exception()
except:
  print("\n\nAborting.")
  sys.exit(1)

print()
print("--- patching stdlib ---")

#region installation
import site

with open(os.path.dirname(__file__) + "/global.py", "rb") as f:
  addition = f.read()

with open(site.getsitepackages()[-1] + "/grab.py", "wb") as f:
  f.write(addition)

with open(site.getsitepackages()[-1] + "/sitecustomize.py", "rb") as f:
  content = f.read()

sep = b"\n# grab.py\n"

if sep in content:
  seploc = content.index(sep)
  content = content[:seploc].rstrip() + content[seploc + len(sep):].partition(b"\n")[2]

with open(site.getsitepackages()[-1] + "/sitecustomize.py", "wb") as f:
  f.write(content)
  f.write(b"\n")
  f.write(sep)
  f.write(b"from grab import Ignore, Grab; import builtins; builtins.Ignore = Ignore; builtins.Grab = Grab")
  f.write(b"\n")
#endregion
