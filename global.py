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
      from urllib.request import urldownload

      modules = os.path.abspath(".venv/modules")
      if modules not in sys.path:
        sys.path.insert(2, modules)

      module = repository.split("/")[-1].replace("/", ".")
      dest = modules + "/" + module

      if not os.path.isdir(dest):
        os.makedirs(dest)

        http_response = urlopen(f"https://github.com/{repository}/archive/%s.zip" % commit)

        zipfile = ZipFile(BytesIO(http_response.read()))
        zipfile.extractall(path=dest)

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
