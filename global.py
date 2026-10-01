from typing import Callable, TypeVar

Function = TypeVar('T', bound=Callable)
Annotation = Callable[[Function], Function]

def Ignore(func: Function) -> Function:
  func.__Grab_ignore__ = True
  return func

def Grab(*, repository: str, commit: str) -> Annotation:
  def gen(func: Function) -> Function:
    nonlocal repository, commit

    installed = False

    def install():
      nonlocal repository, commit

      # importing deferred as they may break in global site
      import os
      import sys

      from io import BytesIO
      from zipfile import ZipFile
      from urllib.request import urlopen

      modules = os.path.abspath(".venv/modules")
      if modules not in sys.path:
        sys.path.insert(2, modules)

      module = repository.split("/")[-1].replace("/", ".")
      dest = modules + "/" + module

      if not os.path.isdir(dest):
        os.makedirs(dest)

        http_response = urlopen(f"https://github.com/{repository}/archive/%s.zip" % commit)

        with ZipFile(BytesIO(http_response.read())) as zipfile:
          for file in zipfile.infolist():
            if '/' in file.filename:
              file.filename = file.filename.partition("/")[2]

              if file.filename:
                zipfile.extract(file, path=dest)

        grabsetup = dest + "/__grab__.py"
        if os.path.isfile(grabsetup):
          with open(grabsetup) as f:
            script = f.read()

          store = {}
          exec(compile(script, grabsetup, 'exec'), {}, store)

          if "__module__" not in store:
            print(f"[Grab] [!] Module '{module}' contains __grab__.py file, doesn't declare __module__'")
          elif not isinstance(store['__module__'], dict) or 'name' not in store['__module__']:
            print(f"[Grab] [!] Module '{module}' contains __grab__.py file, has corrupted __module__'")
          else:
            module = store['__module__']['name']

          if os.name == 'nt':
            import subprocess
            # 'C:\\Windows\\System32\cmd.exe', '/c', 
            subprocess.run(['mklink', '/J', (modules + "/" + module).replace("/", "\\"), dest.replace("/", "\\")], shell=True, stdout=subprocess.DEVNULL)
          else:
            os.link(dest, modules + "/" + module)

        print(f"[Grab] Provided module '{module}'")

    if func.__name__ == 'install' and not hasattr(func, '__Grab_ignore__'):
      install()
      return func

    def wrap(*args, **kwargs):
      nonlocal func, installed
      nonlocal repository, commit

      if not installed:
        installed = True
        install()

      return func(*args, **kwargs)

    return wrap

  return gen

def getmodulename(path: str) -> str:
  import os

  grabsetup = path + "/__grab__.py"
  if os.path.isfile(grabsetup):
    with open(grabsetup) as f:
      script = f.read()

    store = {}
    exec(compile(script, grabsetup, 'exec'), {}, store)

    if "__module__" not in store:
      return path
    elif not isinstance(store['__module__'], dict) or 'name' not in store['__module__']:
      return path
    else:
      return store['__module__']['name']

from typing import Any

def shell(globals: dict[str, Any]) -> None:
  import traceback

  locals = {}
  globals = globals.copy()

  while True:
    try:
      try:
        text = input('>>> ')
      except ValueError:
        break

      try:
        val = eval(compile(text, '<input>', 'eval'), globals, locals)
      except:
        broken = True
      else:
        broken = False

      if broken:
        val = exec(compile(text, '<input>', 'exec'), globals, locals)

      if val is not None:
        print(val)
    except KeyboardInterrupt:
      print("\nKeyboardInterrupt")
    except SystemExit:
      break
    except BaseException as e:
      exc = traceback.format_exception(e)

      print(exc[0], end='')
      print("".join(exc[2:]), end='')
