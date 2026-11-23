# 3mf Converter — an OrcaSlicer plugin

Rebuild a `.3mf` for the printer **you** own, from inside OrcaSlicer.

A MakerWorld `.3mf` is a Bambu Studio project. Opening one as it comes is not an
error — OrcaSlicer ships the Bambu profiles, so the file loads and slices happily —
but it slices for the *designer's* machine: their bed, their machine limits, their
start and end G-code. Everything they tuned is buried under a printer you do not
own, and switching the printer afterwards throws it away.

This plugin rebuilds the project for whatever printer is selected in OrcaSlicer:
the designer's layer height, walls, infill, supports and temperatures are kept, and
their machine is replaced with yours.

One Python file in the standard OrcaSlicer plugin format
([plugin docs](https://www.orcaslicer.com/wiki/developer_reference/plugin_development/plugin_development.html)),
with no third-party dependencies — nothing is downloaded at plugin load time.

The FlashForge device tab and printer agent are a **separate plugin in a separate
repository** (`orca-flashforge-c5`), so the two install, version and publish
independently.

## Requirements

- **OrcaSlicer 2.5.0 or newer.** The Python plugin system landed in 2.5.0; older
  builds will not list the plugin at all.
- A printer **selected** in OrcaSlicer. That selection is what the project is
  rebuilt for.
- A **BambuCloud token**, and only to pull a *link*. A `.3mf` you already have
  converts without one. See *The tab* below.

## What you get

| Capability | Type | What it does |
|---|---|---|
| **3mf Converter** tab | `pages` | Drop a `.3mf`, choose one, or paste a MakerWorld link. The project is rebuilt for the selected printer, saved, and opened in the running OrcaSlicer ready to slice. |

## Install

1. Open **Plugins** in OrcaSlicer, then **Browse plugins ▾ → Install local
   plugin**, and pick `3mf-converter_any.py`.

   Or copy the file into its own folder under the OrcaSlicer data directory, e.g.
   `%APPDATA%\OrcaSlicer\orca_plugins\3mf-converter\3mf-converter_any.py`. A
   plugin folder must contain exactly one entry file (one `.py` or one `.whl`).

   The `_any` suffix is not decoration — Orca Cloud's hub requires a target-OS
   suffix on uploaded plugin files, and `any` is its universal marker for a pure
   Python plugin. The same filename works for a local install.

2. OrcaSlicer prompts for the filesystem and network access the plugin declares.
   Accept both — without the network permission a MakerWorld link cannot resolve.

## Where the token is kept

The BambuCloud token is stored in `settings.json` at
`<OrcaSlicer data>/orca_plugin_data/3mf-converter/`, **not** in the plugin's own
directory. Installing a new plugin version replaces `orca_plugins/<plugin>/`, which
took a token saved beside the plugin with it — the token was lost on every update.
The old location is still read, so a token saved by an earlier version carries over
the first time you save again.

## Theme

The tab follows OrcaSlicer. It takes its background, text, border, muted text,
accent and font from the variables OrcaSlicer injects into every plugin page
(`--orca-bg`, `--orca-fg`, `--orca-border`, `--orca-muted`, `--orca-accent`,
`--orca-accent-fg`, `--orca-font`), and it re-themes live when the app theme
changes. It does not pin itself to dark. The button rules are written `body button` rather
than bare `button` on purpose: OrcaSlicer injects its own default `button` style into
`<head>` *after* the page's stylesheet, at the same specificity, so an unqualified rule
would lose to it — and the host's default is white text on the accent, which is
invisible on a light-theme accent.

## The tab

**A `.3mf` you already have is the easy route.** Drop it on the tab, or use the
file chooser in the drop zone; both convert on their own, with no button to press.
Typing a path is not offered up front — nobody chooses it when dragging works — and
lives behind a one-line link for the case where neither route does.

**A MakerWorld link** works too. Paste it and press **Find plates**, then pick the
plate to convert. That path needs a token; a local file never does.

**Getting a token.** It is the same BambuCloud token Bambu Studio uses, and it is a
one-off. The field is collapsed under **Token settings** until you need it, and it
opens by itself if you ask for a link without one:

1. Sign in at `makerworld.com` in a browser.
2. Press **F12** for Developer Tools.
3. **Application** (Chrome, Edge) or **Storage** (Firefox) → **Cookies** →
   `makerworld.com`.
4. Click the row named `token` and copy its **Value**.
5. Paste it into the panel and press **Save token**.

No cookie called `token`? Reload the page, open the **Network** tab, click any
request to makerworld.com, and keep the `token=…` part of its `cookie:` request
header. Treat it like a password — it is your whole Bambu Cloud session — and it
lapses after roughly 90 days, at which point downloads start failing and you paste a
fresh one. It lives in `settings.json` beside the plugin (mode 0600) and goes to
MakerWorld and nowhere else.

### What is kept, and what is replaced

OrcaSlicer already knows which settings belong to a machine:
`Preset::printer_options()` is that list, and the plugin uses it rather than a
hand-written one. Every key the machine owns takes the selected printer's value;
**every other key keeps the designer's**, so layer height, walls, infill pattern and
density, shells, seam, supports, elephant-foot compensation, temperatures and
filament colours all survive conversion.

Preset *names* are neither: `printer_settings_id`, `print_settings_id` and
`filament_settings_id` are re-pointed at your own presets so the project resolves
against what you have. The report calls those out separately, because filing them
under "kept" or "replaced by your printer" would both be untrue.

### What the report tells you

After a conversion the tab says what came *out*, not just how many settings moved:

- **Every plate** in the file and the filament each one uses.
- **The tools** the project ends up with, and the filament and profile behind each.
- **The machine start and end G-code** that was swapped for your printer's, capped to
  a readable head with the line count — these blocks run to dozens of lines of fan
  and temperature setup. A MakerWorld `.3mf` is unsliced and carries no `.gcode` at
  all, so the G-code shown is the machine block the conversion actually replaced.
- **The full audit**: an expandable list of every key kept from the designer, every
  key re-pointed at your presets, every key replaced by your printer, and every key
  reset to OrcaSlicer's defaults. The counts are only worth trusting if the lists
  behind them can be read, and every key the project carried lands in exactly one.
- **A warning when the tool counts differ**, because that is where filament ends up
  on the wrong extruder.

### Opening an earlier conversion

Converted projects are kept in a folder inside OrcaSlicer's own data directory,
several levels down and awkward to reach. The tab lists them — newest first, with
size and age — and opens one again with a click.

## What it reads, and what it will not

To rebuild a project the plugin reads OrcaSlicer's **printer profile** — bed shape,
machine limits, G-code, thermals, nozzle and extruder setup — because that is what
the designer's machine has to be replaced with. The list of keys is OrcaSlicer's own
published machine-option set, and nothing outside it is read.

Connection settings are excluded from that list, and removed from any project that
arrives carrying them. OrcaSlicer keeps the printer's address, user, password and API
key among its printer options, and those are not machine geometry — they are how one
particular machine is reached. A converted `.3mf` gets passed around; it must not
carry someone's printer credentials inside it. If a project you convert had them, the
report names which were removed rather than fixing it silently.

The exclusion is a **rule on the shape of the key name, not a list of fields** — so
the names of credential fields appear nowhere in this plugin's source. A plugin that
never names them cannot leak them, and that is checkable by reading the file rather
than by trusting a claim. A test asserts it.

The plugin makes **no connection to your printer at all**. The only network calls it
makes are to MakerWorld, and only when you paste a link.

## Settings

Written to `settings.json` beside the plugin, mode 0600.

| Key | Meaning |
|---|---|
| `bambu_token` | BambuCloud token, for pulling a MakerWorld link. A credential — never commit it |

## Publishing

`HUB_LISTING.md` holds the listing text and the submission checklist.

This repository holds **exactly one plugin**, and that is not a preference: Orca
Cloud connects a repository to exactly one of your plugins, and a run against a
repository connected to none or to several fails with a 401.

Connect the repo in **Plugins → Shared → your plugin → Edit plugin → GitHub
publishing** → `ben0551/orca-3mf-converter` → **Connect**, then publish a GitHub
Release tagged `vX.Y.Z`. `.github/workflows/publish-orcacloud.yml` does the upload
over OIDC, so there is no token to store: the tag becomes the version, and the
release notes become the changelog.

## Tests

```
./run_tests.sh
```

Two suites, neither needing OrcaSlicer or a printer:

- `tests/test_converter.py` runs the real plugin against a stub `orca` module
  (`tests/fake_orca.py`) and drives the tab end to end. The conversion is asserted
  key by key against the *converted project settings* — what OrcaSlicer would load —
  not against what the plugin believes it produced.
- `tests/test_page_js.py` extracts the tab's JavaScript and runs it under Node in a
  DOM stub built from the real markup, checking the rendering, the button wiring,
  the drop route and the report.

## What is and is not verified

Verified by the suites above, and against real inputs:

- The conversion, against a real MakerWorld download and real OrcaSlicer: a
  converted project sliced by OrcaSlicer 2.4.2 with *no* `--load-settings` override
  came out as a FlashForge Creator 5 Pro job. A control run of the same file
  unconverted sliced as a Bambu Lab P1P, and a controlled edit proved the designer's
  values survive while the machine's replace theirs.
- The download route, against the live MakerWorld API: the instance endpoint, the
  bearer header, and the returned `url` + `name`.
- That no connection setting is read from a preset or survives into a converted
  project, and that every key the project carried lands in exactly one report bucket.
- Reading OrcaSlicer's presets, per-extruder array resizing, the G-code head capping,
  the decoding of the JSON-encoded values OrcaSlicer hands back, and the whole
  message flow including the drop route and its refusals.

Not verified here, because it needs the real application:

- That OrcaSlicer 2.5.0 loads the plugin and renders the tab. It follows the
  documented API and passes a stub of it, but the stub is not OrcaSlicer.
- **The file hand-off against a live OrcaSlicer.** The payload format and the
  per-platform transport come from OrcaSlicer's own `InstanceCheck` and from a
  published plugin using the same route, and the Linux path is asserted against a
  stubbed `dbus-send` — but no converted file has been pushed into a running
  OrcaSlicer from here. If the hand-off is refused (the audit hook matches `process`
  targets verbatim, so a differently-resolved `dbus-send` would not match), the tab
  says so and prints the path, so the file can be opened with **File → Open
  Project…**.
- **Whether your webview forwards a file drop or opens a file dialog.** Both are
  standard web APIs and both work in the author's OrcaSlicer on Windows, but that is
  one machine. The typed-path link under the drop zone exists for the case where
  they do not.
- **Whether `preset_bundle()` surfaces the machine keys on a real install.** Which
  of the read paths answers on your machine has not been observed from here.
- Deep conversion beyond MakerWorld: a PrusaSlicer project has a genuinely different
  vocabulary, and no key-by-key translation is done for it yet.

## Known limitations

- **Keys OrcaSlicer does not recognise are left in the file, not stripped.** They are
  harmless (the slicer ignores them), but the report cannot list them: a plugin
  cannot enumerate the set of keys OrcaSlicer accepts, only the keys a preset sets.
  That is why the audit has four buckets rather than a "discarded" one.
- **Bambu Studio key names are not translated to OrcaSlicer ones.** Where the two
  disagree on a name for the same setting, the designer's value stays under the name
  OrcaSlicer may not read. Doing this properly needs an alias table kept against both
  codebases.
- The converter runs on the license terms in `LICENSE` (MIT). OrcaSlicer itself is
  AGPL-3.0; a runtime-loaded Python plugin is not a derivative work of it.
