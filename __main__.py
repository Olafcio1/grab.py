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

with open(site.getsitepackages()[-1] + "/sitecustomize.py", "ab") as f:
  f.write(b"\n\n# grab.py\n")
  f.write(b"import grab")
  f.write(b"\n")
#endregion
