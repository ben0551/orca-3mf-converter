# Orca Cloud hub listing

Copy-paste material for this plugin's page on the Orca Cloud hub, kept here so the
listing text does not drift from the code.

## Checklist before publishing

| # | Requirement | Status |
|---|---|---|
| 1 | Plugin file carries a target-OS suffix — `any` for a pure Python plugin | Done: `3mf-converter_any.py` |
| 2 | A `LICENSE` file at the repo root | Done: MIT |
| 3 | `.py` only, no binaries/archives/symlinks in the upload | Done: one `.py` |
| 4 | Release tagged with a semantic version greater than the current one | `v1.3.0` on first publish |
| 5 | Repo connected in the portal: **Plugins → Shared → the plugin → Edit plugin → GitHub publishing** → `ben0551/orca-3mf-converter` → Connect | Not yet — manual step, needs your login |
| 6 | Portal metadata filled: compatible OrcaSlicer version, supported OS, tags | Not yet — set in the portal |
| 7 | Listing icon uploaded (set in the portal, not in plugin metadata) | Ready: `icon.png` (512), `icon-256.png`, `icon-128.png` |

Once 5 and 6 are done, publishing a new version is: push, create a GitHub Release
tagged `vX.Y.Z`, publish it. `.github/workflows/publish-orcacloud.yml` uploads the
file, the tag becomes the version, and the release notes become the changelog.

**A repository connects to exactly one plugin.** Orca Cloud fails a run with a 401 if
the repository is connected to none or to more than one, which is why this plugin has
its own repository rather than sharing one with the FlashForge device tab.

## ⚠️ Read this first: the hub needs a Nightly build

Orca Cloud's own help page states that plugins are a **Beta feature that currently
works only with current OrcaSlicer Nightly builds** — "stable releases without the
Plugins feature will not show or load Orca Cloud plugins."

That is a different gate from the plugin *system* itself, which shipped in OrcaSlicer
**2.5.0** and is what loads a locally installed `.py`. So:

- **Local install on 2.5.0** — works today.
- **Hub listing** — the listing can be created now, but subscribers on 2.5.0 stable
  may not see or activate it until they run a Nightly.

## Listing text

**Name:** 3mf Converter

**Types:** one capability — Pages. See *Capability types and the hub* below: the
listing dropdown is narrower than the real capability set and does not include Pages.

**Compatible OrcaSlicer:** 2.5.0 or newer

**Supported OS:** any (pure Python, standard library only)

**Tags:** `3mf`, `converter`, `bambu-studio`, `project`,
`rebuild-for-my-printer`

**Short description**

> Rebuild a `.3mf` for the printer you actually own, then open it ready to slice.
> A MakerWorld `.3mf` is a Bambu Studio project, so opening one as it comes slices
> for the *designer's* printer — their bed, their machine limits, their start and end
> G-code — while everything they tuned is buried under a machine you do not have.
> This plugin drops a file onto the tab or pulls a MakerWorld link, replaces every
> setting the machine owns with yours, keeps every setting the designer actually
> chose, and hands the result straight to OrcaSlicer.

**Long description**

> **The problem.** A MakerWorld `.3mf` is a Bambu Studio project. Opening one as it
> comes is not an error: OrcaSlicer ships the Bambu profiles, so the file loads and
> slices cleanly — as a Bambu Lab P1P. Wrong bed, wrong machine limits, wrong start
> and end G-code, and everything the designer tuned is buried under a printer you do
> not own.
>
> **What you get**
>
> - **The conversion.** Every setting the *machine* owns is taken from the printer
>   selected in OrcaSlicer; every other setting is left exactly as the designer set
>   it. Layer height, walls, infill, shells, seam, supports, temperatures and colours
>   stay theirs — they know their model.
> - **A file you already have, or a link.** Drop a `.3mf` straight onto the tab or
>   pick it with the file chooser; both convert on their own. Or paste a MakerWorld
>   link and choose the plate to pull. Downloading a link needs a BambuCloud token,
>   and the tab explains in place how to get one — it is the `token` cookie from a
>   signed-in makerworld.com session. A local `.3mf` needs no token at all.
> - **It opens itself.** The converted project is handed straight to the running
>   OrcaSlicer, ready to slice. If that is refused, the tab says why and prints the
>   path, so you can finish with **File → Open Project…**.
> - **The whole audit.** Not just how many settings moved: every plate in the file,
>   the tools the project ends up with, the machine G-code that was replaced, and an
>   expandable list of every key kept, re-pointed at your presets, replaced by your
>   printer, or reset to OrcaSlicer's defaults.
> - **What you converted before**, listed in the tab with size and age, and reopened
>   with a click — instead of digging through OrcaSlicer's data directory.
>
> **Privacy, and what this plugin reads.** A BambuCloud token (needed to download a
> link, and only for that) lives in `settings.json` beside the plugin at mode 0600,
> and is sent to MakerWorld alone.
>
> The plugin reads OrcaSlicer's **printer profile** — the machine geometry it needs
> to rebuild the project: bed shape, machine limits, G-code, thermals, nozzle and
> extruder setup. That is a fixed, published list of machine options, and it stops
> there. It does **not** read the printer's address, user or password, and it makes
> **no network connection to your printer** — converting a `.3mf` never touches it.
> Those connection settings are also stripped from any project that arrives carrying
> them, so a converted file never carries someone's printer credentials inside it.
> It has no dependencies.
>
> **Requirements.** OrcaSlicer 2.5.0 or newer, and a printer selected in it — that is
> what the project gets rebuilt for.

## Capability types and the hub

A plugin is **not listed under a single type**. From the wiki's Plugin Types page:
there is "no separate `type` declaration in the metadata" — the capabilities the
plugin registers determine which workflows can run it, and the Plugins dialog shows
*one row per registered capability*, each with its own enable checkbox and type label.

So this plugin presents one row: Pages (the 3mf Converter tab). Pages does not appear
in the listing card's dropdown (Script / Slicing-pipeline / Resource textures), so
there is nothing to match and nothing to contort — that dropdown describes a narrower
set than the capability system supports. Worth a note to the Orca Cloud team rather
than guessing. The **Compatible OrcaSlicer Version** field is the right place to
record the 2.5.0 floor.

## Differentiation

| Plugin | Covers | Approach | Licence | Notes |
|---|---|---|---|---|
| **ForgeBridge** (closed source) | MakerWorld / Printables / Creality Cloud / makeronline / Snapmaker Space → FlashForge | Web app + Chrome extension + an OrcaSlicer panel | proprietary, free | The same idea, and the one to beat on polish. Its published audit is the model this plugin's report follows. Windows-only panel as of 2026-11 |
| **This plugin** | any `.3mf` (and a MakerWorld link) → the printer selected in OrcaSlicer | One Python file, in-process, no service | MIT | Not FlashForge-specific: it converts for whatever printer OrcaSlicer has selected |

The difference worth stating: this one is not tied to a printer vendor. It reads the
target machine from OrcaSlicer's own selection and uses OrcaSlicer's own
`printer_options()` as the definition of which settings a machine owns, rather than a
maintained list.
