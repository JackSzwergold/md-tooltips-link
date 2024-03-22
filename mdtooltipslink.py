import markdown
from markdown.extensions import Extension
from markdown.postprocessors import Postprocessor
from markdown.inlinepatterns import Pattern
from codecs import open
import os
import re
import requests
import shutil
from urllib.parse import urlparse


DEFAULT_CSS = """
div.tooltip::before {
  font-size: 130%;
  font-weight: bold;
  display: block;
  color: #4c50b4;
  content: attr(header);
  border-bottom: 1px solid LightGray;
  padding-bottom: 4px;
}

a.tooltiptext {
  color: MidnightBlue;
  font-weight: 500;
  border-bottom: 1px dotted black;
}

a.tooltiptext:hover {
  color: MidnightBlue;
  font-weight: 500;
  text-shadow: 2px 2px 2px DarkGrey;
  border-bottom: 1px dotted black;
}

span.tooltiptext {
  color: MidnightBlue;
  font-weight: 500;
  border-bottom: 1px dotted black;
}
"""

TIPPY_THEME_URL = "https://unpkg.com/tippy.js@6/themes/{}.css"

DEF_RE = r"(@\()(?P<text>.+?)\)"

JAVASCRIPT = {}


class DefinitionPattern(Pattern):
    def __init__(self, pattern, md=None, configs={}):
        super().__init__(pattern, md=md)

        # use DOTALL flag to allow multiline text (https://stackoverflow.com/q/63636926/1862861)
        self.compiled_re = re.compile(r"^(.*?)%s(.*)$" % pattern, flags=re.DOTALL)

        self.glossary = configs.get("glossary_path")
        self.header = configs.get("header")
        self.link = configs.get("link")
        self.plural = configs.get("allow_plural")

    def handleMatch(self, matched):
        text = matched.group("text").replace("\n", " ")

        with open(self.glossary, "r") as r:
            lines = r.readlines()

        total = ""

        # if term is plural try glossary for singular versions
        textsingular = []
        singulartext = ""
        if text.lower()[-2:] == "es" and self.plural:
            textsingular.append(text.lower()[:-2])
        if text.lower()[-1] == "s" and self.plural:
            textsingular.append(text.lower()[:-1])

        for i in range(len(lines)):
            if lines[i].lower().rstrip() == "## " + text.lower():
                count = 1
                res = ""
                while not res.startswith("##") and i + count < len(lines):
                    res = lines[i + count]
                    if not res.isspace() and not res.startswith("##"):
                        total += res
                    count += 1
            elif self.plural:
                for ts in textsingular:
                    if lines[i].lower().rstrip() == "## " + ts:
                        singulartext = ts
                        count = 1
                        res = ""
                        while not res.startswith("##") and i + count < len(lines):
                            res = lines[i + count]
                            if not res.isspace() and not res.startswith("##"):
                                total += res
                            count += 1
                        break

            if total:
                break

        if not total:
            return

        definition = total.rstrip()

        if self.link:
            basename = os.path.basename(self.glossary).strip(".md")
            elem = markdown.util.etree.Element("a")
            linktext = text.lower() if len(singulartext) == 0 else singulartext
            elem.set(
                "href",
                "../{}/index.html#{}".format(basename, linktext.replace(" ", "-")),
            )
        else:
            elem = markdown.util.etree.Element("span")

        id = (
            "tooltip-{}".format(text.lower().replace(" ", "-"))
            if len(singulartext) == 0
            else "tooltip-{}".format(singulartext.replace(" ", "-"))
        )

        elem.set("id", id)
        elem.text = text

        elem.set("class", "tooltiptext")

        content = markdown.markdown(definition)

        if self.header:
            # wrap in div with header containing text
            headertext = text if len(singulartext) == 0 else singulartext
            content = '<div class="tooltip" header="{}">{}</div>'.format(
                headertext, content
            )

        if id not in JAVASCRIPT:
            JAVASCRIPT[id] = content.replace("'", "&#39;").replace("\n", " ")

        return elem


class DefinitionPostprocessor(Postprocessor):
    def __init__(self, js):
        self.js = js

    def run(self, text):
        # write out javascript to file

        tippytemplate = """tippy('#{id}', {{
    content: '{html}',
    allowHTML: true,
    interactive: true,
    theme: '{theme}',
}});
"""

        jsfile = self.js.getConfig("js_file")
        theme = self.js.getConfig("theme", "light-border")

        with open(jsfile, "w") as fp:
            for key in JAVASCRIPT:
                fp.write(
                    tippytemplate.format(
                        **{"id": key, "html": JAVASCRIPT[key], "theme": theme}
                    )
                )
                fp.write("\n")

        # don't do anything to text
        return text


class MdTooltipLink(Extension):
    def __init__(self, **kwargs):
        # configuration defaults
        self.config = {
            "glossary_path": ["docs/glossary.md", "Default location for glossary."],
            "header": [True, "Add header containing the text in the tooltip."],
            "link": [True, "Add link to the glossary item."],
            "allow_plural": [
                True,
                "Allow tags around plural versions of glossary items",
            ],
            "css_path": [
                "docs/css/tooltips.css",
                "Location to output default CSS style.",
            ],
            "css_custom": [
                None,
                "Custom CSS to place in path (including tippy theme CSS).",
            ],
            "js_file": ["docs/javascripts/glossary.js", "Javascript path"],
            "theme": [
                "light-border",
                "The tippy.js theme name, or a URL to the theme, or the theme definition CSS",
            ],
        }

        # in the mkdocs.yml file add:
        # extra_javascript:
        #   - https://unpkg.com/@popperjs/core@2
        #   - https://unpkg.com/tippy.js@6
        #   - value from js_file

        super().__init__(**kwargs)

        if self.getConfig("css_custom") is None:
            # output default CSS to path
            try:
                with open(self.getConfig("css_path"), "w") as fp:
                    fp.write(DEFAULT_CSS)

                    theme = self.getConfig("theme")

                    if ".tippy-box[" in theme:
                        # theme is CSS, so add to CSS file
                        fp.write("\n" + theme + "\n")
                    else:
                        result = urlparse(theme)
                        if all([result.scheme, result.netloc, result.path]):
                            # have passed a URL
                            themeurl = theme
                        else:
                            themeurl = TIPPY_THEME_URL.format(theme)

                        req = requests.get(themeurl)
                        if req.text:
                            fp.write("\n" + req.text + "\n")

            except Exception as e:
                raise IOError("Problem writing CSS file: {}".format(e))
        elif os.path.isfile(self.getConfig("css_custom")):
            try:
                shutil.copyfile(
                    self.getConfig("css_custom"), self.getConfig("css_path")
                )
            except Exception as e:
                raise RuntimeError("Problem copying CSS file: {}".format(e))

        jspath, jsfile = os.path.split(self.getConfig("js_file"))
        if not os.path.isdir(jspath):
            os.makedirs(jspath)

    def extendMarkdown(self, md):
        md.inlinePatterns["definition"] = DefinitionPattern(
            DEF_RE, md, configs=self.getConfigs()
        )

        # Insert a postprocessor
        md.postprocessors.register(DefinitionPostprocessor(self), "definition", 25)


def makeExtension(**kwargs):
    return MdTooltipLink(**kwargs)
