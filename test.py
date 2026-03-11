from rich.traceback import install

install(show_locals=True)

import rich_click as click
import sys
from datetime import datetime
from functools import partial
from itertools import chain
from pathlib import Path
from rich import inspect
from rich.console import Console
from rich.markdown import Markdown
from subprocess import run, PIPE

runner = partial(run, shell=True)

# Adapted From:
# Answer: https://stackoverflow.com/a/3430395
# User: https://stackoverflow.com/users/7432/bryan-oakley
directory = Path(__file__).parent.resolve()

# TODO
resources = directory / "resources"

ext = "md"

console = Console()

class Gum:
  # TODO
  @property
  def files(self):
    files = {}
    for fd in resources.iterdir():
      if not fd.is_dir():

        # Adapted From:
        # Answer: https://stackoverflow.com/a/44259260
        # User: https://stackoverflow.com/users/3015186/niko-fohr
        last_edited = str(datetime.fromtimestamp(fd.lstat().st_mtime))

        files[last_edited] = fd

    return files

  def __getattr__(self, name):
    return partial(self, "gum", name)

  def __call__(self, *args, **kwargs):

    # TODO
    n = 2
    if len(args) > n and not isinstance(args[n], str):
      new_args = list(args[:n]) + list(args[n])
      if len(args) > (n + 1):
        new_args += list(args[n + 1:])
    else:
      new_args = list(args)
    
    kwargs = { f'{"-" if len(k) == 1 else "--"}{k}':v for k, v in kwargs.items() }

    return runner(new_args + list(chain(*kwargs.items())), stdout=PIPE).stdout.decode().strip()

  def note(self, *args):

    # Adapted From:
    # Answer: https://stackoverflow.com/a/873333
    # User: https://stackoverflow.com/users/16417/paolo-bergantino
    longest = max(args, key=len)
    length = len(longest) - 3

    args = list(args)
    for last_edited, file in self.files.items():
        stem = file.stem

        # Adapted From:
        # Answer: https://stackoverflow.com/a/5676676
        # User: https://stackoverflow.com/users/218196/felix-kling
        name = (stem[:length] + "...") if len(stem) >= length else stem.ljust(length + 3)

        args.append(f"{name}\tlast edited {last_edited}")

    return self.choose(*args)

gum = Gum()

@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
  if len(sys.argv) > 1:
    if sys.argv[1] in ["--help", "-h"]:
      click.echo(ctx.get_help())
    else:
      ctx.invoke(main.commands[sys.argv[1]].callback, *sys.argv[2:])
  else:
      while True:
        answer = gum.note("Exit", "Create a new file")
        if answer:
          match answer:
            case "Create a new file":
              ctx.invoke(new)
            case "Exit":
              exit(0)
            case _:
              operation = gum.choose(f.capitalize() for f in main.commands if f not in ("server"))
              if operation:
                ctx.invoke(main.commands[operation.lower()].callback, str(gum.files[answer.split("last edited ")[1]].stem))

@main.command()
@click.argument("name", required=False)
def new(name: str | None = None):
  if not name:
    click.echo("What would you like to name this new file?")
    name = gum.input()
  if name:
    runner(["nvim", resources / (name if name.endswith(f".{ext}") else f"{name}.{ext}")])

@main.command()
@click.argument("old_name", required=False)
@click.argument("new_name", required=False)
def rename(old_name: str | None = None, new_name: str | None = None):
  if old_name:
    file = resources / (old_name if old_name.endswith(f".{ext}") else f"{old_name}.{ext}")
  else:
    click.echo("Which file would you like to rename?")
    file = gum.file(resources)
  if file:
    if not new_name:
      click.echo("What would you like the new name to be?")
      new_name = gum.input(placeholder = old_name)
    if new_name and old_name != new_name:
      Path(file).rename(file.parent / (new_name+file.suffix))

@main.command()
@click.argument("name", required=False)
def delete(name: str | None = None):
  if name:
    file = resources / (name if name.endswith(f".{ext}") else f"{name}.{ext}")
  else:
    click.echo("Which file would you like to delete?")
    file = gum.file(resources)
  if file:
    Path(file).unlink()

@main.command()
@click.argument("name", required=False)
def edit(name: str | None = None):
  if name:
    file = resources / (name if name.endswith(f".{ext}") else f"{name}.{ext}")
  else:
    click.echo("Which file would you like to edit?")
    file = gum.file(resources)
  if file:
    runner(["nvim", file])

# TODO
@main.command()
@click.argument("name", required=False)
def preview(name: str | None = None):
  if name:
    file = resources / (name if name.endswith(f".{ext}") else f"{name}.{ext}")
  else:
    click.echo("Which file would you like to preview?")
    file = gum.file(resources)
  if file:
    console.print(Markdown(file.read_text()))

@main.group(no_args_is_help=True)
def server():
  ...

@server.command()
def start():
  ...

@server.command()
def stop():
  ...

if __name__ == "__main__":
  # TODO: Ensure `gum' and `$EDITOR' are installed.

  main({})