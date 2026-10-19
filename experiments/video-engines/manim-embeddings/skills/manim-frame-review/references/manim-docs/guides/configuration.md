# Configuration

Manim provides an extensive configuration system that allows it to adapt to
many different use cases.  There are many configuration options that can be
configured at different times during the scene rendering process.  Each option
can be configured programmatically via [the ManimConfig class](), at the time
of command invocation via [command-line arguments](), or at the time the library
is first imported via [the config files]().

The most common, simplest, and recommended way to configure Manim is
via the command-line interface (CLI), which is described directly below.

## Command-line arguments

By far the most commonly used command in the CLI is the `render` command,
which is used to render scene(s) to an output file.
It is used with the following arguments:

However, since Manim defaults to the `render` command whenever no command
is specified, the following form is far more common and can be used instead:

```bash
manim [OPTIONS] FILE [SCENES]
```

An example of using the above form is:

```bash
manim -qm file.py SceneOne
```

This asks Manim to search for a Scene class called `SceneOne` inside the
file `file.py` and render it with medium quality (specified by the `-qm` flag).

Another frequently used flag is `-p` (“preview”), which makes Manim
open the rendered artifact after rendering. This behavior is the same for all
renderers.

Renderers may also support a live preview while the scene is evaluated. The
OpenGL renderer provides this with `-l` (or `--live-preview`):

```bash
manim --renderer=opengl -l <file.py> SceneName
```

With `--format=auto`, live preview does not write a media file, keeping the
interactive workflow fast. Pass a concrete format, such as `--format=mp4`,
to record the scene while displaying the live preview.

### Advanced examples

To render a scene in high quality, but only output the last frame of the scene
instead of the whole video, you can execute

```bash
manim -sqh <file.py> SceneName
```

The equivalent `--format=png` spelling uses the same fast mode that saves only
the last frame. Use `--format=png-sequence` when every rendered frame should
be written as a numbered PNG instead.

The following example specifies the output file name (with the `-o`
flag), renders only the first ten animations (`-n` flag) with a white
background (`-c` flag), and saves the animation as a `.gif` instead of as a
`.mp4` file (`--format=gif` flag).  It uses the default quality and does not try to
open the file after it is rendered.

```bash
manim -o myscene --format=gif -n 0,10 -c WHITE <file.py> SceneName
```

### A list of all CLI flags

## The ManimConfig class

The most direct way of configuring Manim is through the global `config` object,
which is an instance of [`ManimConfig`](../reference/manim._config.utils.ManimConfig.md#manim._config.utils.ManimConfig).  Each property of this class is
a config option that can be accessed either with standard attribute syntax or
with dict-like syntax:

```pycon
>>> from manim import *
>>> config.background_color = WHITE
>>> config["background_color"] = WHITE
```

#### NOTE
The former is preferred; the latter is provided for backwards
compatibility.

Most classes, including [`Camera`](../reference/manim.camera.camera.Camera.md#manim.camera.camera.Camera), [`Mobject`](../reference/manim.mobject.mobject.Mobject.md#manim.mobject.mobject.Mobject), and
[`Animation`](../reference/manim.animation.animation.Animation.md#manim.animation.animation.Animation), read some of their default configuration from the global
`config`.

```pycon
>>> Camera({}).background_color
<Color white>
>>> config.background_color = RED  # 0xfc6255
>>> Camera({}).background_color
<Color #fc6255>
```

[`ManimConfig`](../reference/manim._config.utils.ManimConfig.md#manim._config.utils.ManimConfig) is designed to keep internal consistency.  For example,
setting `frame_y_radius` will affect `frame_height`:

```pycon
>>> config.frame_height
8.0
>>> config.frame_y_radius = 5.0
>>> config.frame_height
10.0
```

The global `config` object is meant to be the single source of truth for all
config options.  All of the other ways of setting config options ultimately
change the values of the global `config` object.

The following example illustrates the video resolution chosen for examples
rendered in our documentation with a reference frame.

## The config files

As the last example shows, executing Manim from the command line may involve
using many flags simultaneously.  This may become a nuisance if you must
execute the same script many times in a short time period, for example, when
making small incremental tweaks to your scene script.  For this reason, Manim
can also be configured using a configuration file.  A configuration file is a
file ending with the suffix `.cfg`.

To use a local configuration file when rendering your scene, you must create a
file with the name `manim.cfg` in the same directory as your scene code.

#### WARNING
The config file **must** be named `manim.cfg`. Currently, Manim
does not support config files with any other name.

The config file must start with the section header `[CLI]`.  The
configuration options under this header have the same name as the CLI flags
and serve the same purpose.  Take, for example, the following config file.

```ini
[CLI]
# my config file
output_file = myscene
format = gif
background_color = WHITE
```

Config files are parsed with the standard python library `configparser`. In
particular, they will ignore any line that starts with a pound symbol `#`.

Video encoder profiles use dedicated sections because codec options are arbitrary
key/value pairs:

```ini
[video_encoder]
codec = libx264
pixel_format = yuv420p

[video_encoder.options]
crf = 18
preset = slow
```

`codec` and `pixel_format` default to `auto`. Manim resolves them from the
output format and whether alpha is required. The equivalent CLI options are
`--video-codec`, `--pixel-format`, and repeatable
`--encoder-option KEY=VALUE`. If any `--encoder-option` is supplied, the CLI
option map replaces the complete `[video_encoder.options]` map.

Now, executing the following command

```bash
manim -o myscene --format=gif -c WHITE <file.py> SceneName
```

is equivalent to executing the following command, provided that `manim.cfg`
is in the same directory as <file.py>,

```bash
manim <file.py> SceneName
```

#### TIP
The names of the configuration options admissible in config files are
exactly the same as the **long names** of the corresponding command-
line flags.  For example, the `-c` and `--background_color` flags
are interchangeable, but the config file only accepts
`background_color` as an admissible option.

Since config files are meant to replace CLI flags, all CLI flags can be set via
a config file.  Moreover, any config option can be set via a config file,
whether or not it has an associated CLI flag.  See the bottom of this document
for a list of all CLI flags and config options.

Manim will look for a `manim.cfg` config file in the same directory as the
file being rendered, and **not** in the directory of execution.  For example,

```bash
manim -o myscene -i -c WHITE <path/to/file.py> SceneName
```

will use the config file found in `path/to/file.py`, if any.  It will **not**
use the config file found in the current working directory, even if it exists.
In this way, the user may keep different config files for different scenes or
projects, and execute them with the right configuration from anywhere in the
system.

The file described here is called the **folder-wide** config file because it
affects all scene scripts found in the same folder.

### The user config file

As explained in the previous section, a `manim.cfg` config file only
affects the scene scripts in its same folder.  However, the user may also
create a special config file that will apply to all scenes rendered by that
user. This is referred to as the **user-wide** config file, and it will apply
regardless of where Manim is executed from, and regardless of where the scene
script is stored.

The user-wide config file lives in a special folder, depending on the operating
system.

* Windows: `UserDirectory`/AppData/Roaming/Manim/manim.cfg
* MacOS: `UserDirectory`/.config/manim/manim.cfg
* Linux: `UserDirectory`/.config/manim/manim.cfg

Here, `UserDirectory` is the user’s home folder.

#### NOTE
A user may have many **folder-wide** config files, one per folder,
but only one **user-wide** config file.  Different users in the same
computer may each have their own user-wide config file.

#### WARNING
Do not store scene scripts in the same folder as the user-wide
config file.  In this case, the behavior is undefined.

Whenever you use Manim from anywhere in the system, Manim will look for a
user-wide config file and read its configuration.

### Cascading config files

What happens if you execute Manim and it finds both a folder-wide config file
and a user-wide config file?  Manim will read both files, but if they are
incompatible, **the folder-wide file takes precedence**.

For example, take the following user-wide config file

```ini
# user-wide
[CLI]
output_file = myscene
format = gif
background_color = WHITE
```

and the following folder-wide file

```ini
# folder-wide
[CLI]
format = auto
```

Then, executing `manim <file.py> SceneName` will be equivalent to not
using any config files and executing

```bash
manim -o myscene -c WHITE <file.py> SceneName
```

Any command-line flags have precedence over any config file.  For example,
using the previous two config files and executing `manim -c RED
<file.py> SceneName` is equivalent to not using any config files and
executing

```bash
manim -o myscene -c RED <file.py> SceneName
```

There is also a **library-wide** config file that determines Manim’s default
behavior and applies to every user of the library.  It has the least
precedence, so any config options in the user-wide and any folder-wide files
will override the library-wide file.  This is referred to as the *cascading*
config file system.

#### WARNING
**The user should not try to modify the library-wide file**.
Contributors should receive explicit confirmation from the core
developer team before modifying it.

## Order of operations

<div class="mxgraph" style="max-width:100%;border:1px solid transparent;" data-mxgraph="{&quot;highlight&quot;:&quot;#0000ff&quot;,&quot;nav&quot;:true,&quot;resize&quot;:true,&quot;toolbar&quot;:&quot;zoom layers lightbox&quot;,&quot;edit&quot;:&quot;_blank&quot;,&quot;url&quot;:&quot;https://drive.google.com/uc?id=1WYVKKoRbXrumHEcyQKQ9s1yCnBvfU2Ui&amp;export=download&quot;}"></div>
<script type="text/javascript" src="https://viewer.diagrams.net/embed2.js?&fetch=https%3A%2F%2Fdrive.google.com%2Fuc%3Fid%3D1WYVKKoRbXrumHEcyQKQ9s1yCnBvfU2Ui%26export%3Ddownload"></script>

With so many different ways of configuring Manim, it can be difficult to know
when each config option is being set.  In fact, this will depend on how Manim
is being used.

If Manim is imported from a module, then the configuration system will follow
these steps:

1. The library-wide config file is loaded.
2. The user-wide and folder-wide files are loaded if they exist.
3. All files found in the previous two steps are parsed in a single
   `ConfigParser` object, called `parser`.  This is where *cascading*
   happens.
4. `logging.Logger` is instantiated to create Manim’s global `logger`
   object. It is configured using the “logger” section of the parser,
   i.e. `parser['logger']`.
5. `ManimConfig` is instantiated to create the global `config` object.
6. The `parser` from step 3 is fed into the `config` from step 5 via
   `ManimConfig.digest_parser()`.
7. Both `logger` and `config` are exposed to the user.

If Manim is being invoked from the command line, all of the previous steps
happen, and are complemented by:

1. The CLI flags are parsed and fed into `config` via
   `digest_args()`.
2. If the `--config_file` flag was used, a new `ConfigParser` object
   is created with the contents of the library-wide file, the user-wide file if
   it exists, and the file passed via `--config_file`.  In this case, the
   folder-wide file, if it exists, is ignored.
3. The new parser is fed into `config`.
4. The rest of the CLI flags are processed.

To summarize, the order of precedence for configuration options, from lowest to
highest precedence is:

1. Library-wide config file,
2. user-wide config file, if it exists,
3. folder-wide config file, if it exists OR custom config file, if passed via
   `--config_file`,
4. other CLI flags, and
5. any programmatic changes made after the config system is set.

## Inspecting available config options

Run `manim cfg show` to inspect the currently resolved configuration and
`manim render --help` for the authoritative list of render CLI options. The
attributes available for programmatic configuration are documented on
[`ManimConfig`](../reference/manim._config.utils.ManimConfig.md#manim._config.utils.ManimConfig).

Some CLI conveniences intentionally map to a canonical configuration value. In
particular, `-s` / `--save_last_frame` sets `format = png`; configuration
files should use the canonical `format` option directly.

## Accessing CLI command options

Entering `manim`, or `manim --help`, will open the main help page.

```default
Usage: manim [OPTIONS] COMMAND [ARGS]...

  Animation engine for explanatory math videos.

Options:
  --version  Show version and exit.
  --help     Show this message and exit.

Commands:
  cfg      Manages Manim configuration files.
  init     Sets up a new project in current working directory with default
           settings.

           It copies files from templates directory and pastes them in the
           current working dir.
  new      Create a new project or insert a new scene.
  plugins  Manages Manim plugins.
  render   Render SCENE(S) from the input FILE.

See 'manim <command>' to read about a specific subcommand.

Made with <3 by Manim Community developers.
```

Each of the subcommands has its own help page which can be accessed similarly:

```default
manim render
manim render --help
```
