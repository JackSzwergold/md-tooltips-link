# md-tooltips-link

A simple Python markdown extension which will give you tooltips *and* links to definitions from a glossary. Works with `mkdocs` with `mkdocs-material`. This is extensively based on the [`md-tooltips`](https://github.com/lsaether/md-tooltips) extension by Logan Saether, but adds in the following:

 * the ability to have the hover-over text link to the glossary
 * the ability to pass a glossary file with any path/name rather than just `docs/glossary.md`
 * automatically create a default CSS file
 * allow the user to supply a custom CSS file

These tooltips just use CSS without any Javascript.

> Note: I should probably switch this over to using something like the Javascript [tippy](https://atomiks.github.io/tippyjs/) package. That would offer better control of the tooltip and allow full HTML within the tooltip. This will happen if/when I have the time...

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

`cssfilepath` sets where the default CSS file will be output to. This defaults to `docs/css/tooltips.css`.

```yaml
markdown_extensions:
  - mdtooltipslink:
      css_custom: csscustomfilepath
```

`csscustomfilepath` allows you to pass your own CSS file, which will be copied to the location given by the `css_path` option. This defaults to `None`.

## License

Public domain.
