from rich.traceback import install

install(show_locals=True)

import os
import rich_click as click
import sys
from datetime import datetime
from functools import partial
from itertools import chain
from pathlib import Path
from rich import inspect
from rich.console import Console
from rich.markdown import Markdown
from subprocess import run, PIPE, CalledProcessError

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
        return partial(self, name)

    def __call__(self, *args, **kwargs):

        # TODO
        n = 1
        if len(args) > n and not isinstance(args[n], str):
            new_args = list(args[:n]) + list(args[n])
            if len(args) > (n + 1):
                new_args += list(args[n + 1 :])
        else:
            new_args = list(args)

        kwargs = {
            f"{'-' if len(k) == 1 else '--'}{k}": ("" if isinstance(v, bool) else v)
            for k, v in kwargs.items()
        }

        return (
            runner(
                list(filter(None, ["gum"] + new_args + list(chain(*kwargs.items())))),
                stdout=PIPE,
                check=True,
            )
            .stdout.decode()
            .strip()
        )

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
            name = (
                (stem[:length] + "...")
                if len(stem) >= length
                else stem.ljust(length + 3)
            )

            args.append(f"{name}\tlast edited {last_edited}")

        return self.choose(*args)


def get_key():
    if os.name == "nt":
        import msvcrt

        char = msvcrt.getch()

        # Check if it's a special key prefix (\x00 or \xe0)
        if char in (b"\x00", b"\xe0"):
            # Read the second byte to clear the buffer
            second_char = msvcrt.getch()
            # Return a custom string so your editor knows it's an arrow
            special_keys = {b"H": "UP", b"P": "DOWN", b"K": "LEFT", b"M": "RIGHT"}
            return special_keys.get(second_char, "SPECIAL")

        return char.decode("cp437", errors="ignore")
    else:
        import tty, termios

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


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
                        operation = gum.choose(
                            f.capitalize() for f in main.commands if f not in ("server")
                        )
                        if operation:
                            ctx.invoke(
                                main.commands[operation.lower()].callback,
                                str(gum.files[answer.split("last edited ")[1]].stem),
                            )


@main.command()
@click.argument("name", required=False)
def new(name: str | None = None):
    if not name:
        click.echo("What would you like to name this new file?")
        name = gum.input()
    if name:
        if not name.endswith(f".{ext}"):
            name = f"{name}.{ext}"
        (resources / name).touch()


@main.command()
@click.argument("old_name", required=False)
@click.argument("new_name", required=False)
def rename(old_name: str | None = None, new_name: str | None = None):
    if old_name:
        file = resources / (
            old_name if old_name.endswith(f".{ext}") else f"{old_name}.{ext}"
        )
    else:
        click.echo("Which file would you like to rename?")
        file = gum.file(resources)
    if file:
        if not new_name:
            click.echo("What would you like the new name to be?")
            new_name = gum.input(placeholder=old_name)
        if new_name and old_name != new_name:
            Path(file).rename(file.parent / (new_name + file.suffix))


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
        print(f"-- editing {file} press '=' to exit --")

        text = file.read_text()

        cursor = len(text)
        beforeCursor = text[:cursor]
        afterCursor = text[cursor:]
        key = ""
        print(f"\r{beforeCursor}{key}|{afterCursor}\n\n\n\n", end="", flush=True)
        while key != "=":
            key = get_key()
            runner(["cls" if os.name == "nt" else "clear"])
            print(f"-- editing {file} press '=' to exit --")
            if key == "LEFT":
                cursor -= 1
                key = ""
            if key == "RIGHT":
                cursor += 1
                if cursor > len(text):
                    cursor = len(text)
                key = ""
            if key == "\r":
                key = "\n"
            if key in ["\b", "\x08", "\x7f"]:  # Backspace detection
                if cursor > 0:
                    text = beforeCursor[:-1] + afterCursor
                    cursor -= 1
                    key = ""
            if key == "UP":
                prev_newline = text.rfind("\n", 0, cursor - 1)
                if prev_newline != -1:
                    cursor = prev_newline + 1
                else:
                    cursor = 0
                key = ""

            if key == "DOWN":
                next_newline = text.find("\n", cursor + 1)
                if next_newline != -1:
                    cursor = next_newline
                else:
                    cursor = len(text)
                key = ""
            beforeCursor = text[:cursor]
            afterCursor = text[cursor:]
            file.write_text(text)

            # Append the key to your text and display it

            # \r moves cursor to start of line, allowing a 'typewriter' effect

            print(f"\r{beforeCursor}{key}|{afterCursor}\n\n\n\n", end="", flush=True)
            text = beforeCursor + key + afterCursor
            cursor += len(key)

        print("\n--- Exiting Editor ---")


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
def server(): ...


@server.command()
def start(): ...


@server.command()
def stop(): ...


if __name__ == "__main__":
    try:
        gum(help=True)
    except CalledProcessError:
        raise click.UsageError(
            "`gum' must be installed to run this program. Please refer to https://github.com/charmbracelet/gum?tab=readme-ov-file#installation for instructions on how to install it."
        )

    main({})
