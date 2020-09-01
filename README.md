# md-tooltips-link

A simple Python markdown extension which will give you tooltips *and* links to definitions from a glossary. Works with `mkdocs` with `mkdocs-material`. This is extensively based on the [`md-tooltips`](https://github.com/lsaether/md-tooltips) extension by Logan Saether but adds in the following:

 * the ability to have the hover-over text link to the glossary
 * the ability to pass a glossary file with any path/name rather than just `docs/glossary.md`
 * automatically create a default CSS file for the tooltip
 * allow the user to supply a custom CSS file
 * allow tags within the Markdown to be plurals of glossary items

To create the tooltips the Javascript [tippy](https://atomiks.github.io/tippyjs/) package is used.

> Note: Version 0.1 just used CSS without any Javascript.

## How to use

Install from `pip`

```bash
$ pip install md-tooltips-link
```

Add to your `mkdocs.yml` under the `markdown_extensions` field.

```yaml
markdown_extensions:
  - mdtooltipslink
```

Create a file named `glossary.md` in the top level of the `docs` directory.

```bash
$ touch docs/glossary.md
```

Format each word as a subheader using double `##`.

```md
## Word

Here is the definition of a word

## Block

A block is a data structure...
```

In any of your markdown files in the `docs` directory, use the `@()` syntax to create a tooltip.

```md
An important term you should be familiar with is @(block).
```

To use tippy you will need to add the javascript paths to the `extra_javascript` option in `mkdocs.yml`:

```yaml
extra_javascript:
  - https://unpkg.com/@popperjs/core@2
  - https://unpkg.com/tippy.js@6
  - javascript/glossary.js
```

and use the `js_file` option for when defining `mdtooltipslink` options:

```yaml
markdown_extensions:
  - mdtooltipslink:
      js_file: docs/javascript/glossary.js
```

### Customisation

The following customisations are available:

```yaml
markdown_extensions:
  - mdtooltipslink:
      glossary_path: filepath
```

`filepath` is the path to your glossary file. This defaults to `docs/glossary.md`.

```yaml
markdown_extensions:
  - mdtooltipslink:
      link: true
```

`link` allows you to set whether or not the tooltip hover text provides a link to the item in the glossary or not. This defaults to `True`.

```yaml
markdown_extensions:
  - mdtooltipslink:
      header: true
```

`header` allows you to set whether or not the tooltip text box has a "header" containing the tooltip text. This defaults to `True`.

```yaml
markdown_extensions:
  - mdtooltipslink:
      css_path: cssfilepath
```

`cssfilepath` sets where the default CSS file will be output to. This defaults to `docs/css/tooltips.css`, which should also be included in the `extra_css` option (without the preceeding `docs`), e.g.,:

```yaml
extra_css:
  - css/tooltips.css
```

```yaml
markdown_extensions:
  - mdtooltipslink:
      css_custom: csscustomfilepath
```

`csscustomfilepath` allows you to pass your own CSS file, which will be copied to the location given by the `css_path` option. This defaults to `None`.

> Note: At the moment the Javascript file that this extension creates does not get copied into the `site` directory created by `mkdocs` unless it already exists. Therefore you have to manually copy it over - I'll try and fix this in the future.

## License

Public domain.
