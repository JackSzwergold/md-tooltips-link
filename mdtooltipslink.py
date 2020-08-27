import markdown
from markdown.extensions import Extension
from markdown.postprocessors import Postprocessor
from markdown.inlinepatterns import Pattern
from codecs import open
import os
import shutil


DEFAULT_CSS = """
.tooltip {
  border-bottom: 1px dotted #000000;
  cursor: pointer;
  position: relative;
  display: inline-block;
}

.tooltip .tooltiptext{
  visibility: hidden;
  position: absolute;

  border-radius: 0px 3px 3px 0px;
  -moz-border-radius: 0px 3px 3px 0px;
  -webkit-border-radius: 0px 3px 3px 0px;
  box-shadow: 2px 2px 2px rgba(0, 0, 0, 0.1);
  -webkit-box-shadow: 2px 2px rgba(0, 0, 0, 0.1);
  -moz-box-shadow: 2px 2px rgba(0, 0, 0, 0.1);

  left: -1.5em;
  top: 2.2em;
  z-index: 1;
  width: 350px;

  font-size: 90%;
  color: #666666;
  background-color: #F7F7F7; 
  border: 1px solid #F5F5F5;
  border-left: 3px solid #4c50b4;
  padding: 0.5em 0.8em 0.8em 0.8em;
}

#tooltipheader {
  font-size: 110%;
  font-weight: bold;
  display: block;
  color: #4c50b4;
  padding: 0.2em 0 0.6em 0;
}

.tooltip:hover .tooltiptext {
  visibility: visible;
}
"""


DEF_RE = r"(@\()(?P<text>.+?)\)"

JAVASCRIPT = {}


class DefinitionPattern(Pattern):
    def __init__(self, pattern, md=None, configs={}):
        super().__init__(pattern, md=md)

        self.glossary = configs.get("glossary_path")
        self.header = configs.get("header")
        self.link = configs.get("link")

    def handleMatch(self, matched):
        text = matched.group("text")

        with open(self.glossary, "r") as r:
            lines = r.readlines()

        total = ""
        for i in range(len(lines)):
            if lines[i].lower().rstrip() == "## " + text.lower():
                count = 1
                res = ""
                while not res.startswith("##") and i + count < len(lines):
                    res = lines[i + count]
                    if not res.isspace() and not res.startswith("##"):
                        total += res
                    count += 1

        if not total:
            return

        definition = total.rstrip()

        if self.link:
            basename = os.path.basename(self.glossary).strip(".md")
            elem = markdown.util.etree.Element("a")
            elem.set("href", "../{}/index.html#{}".format(basename, text))
        else:
            elem = markdown.util.etree.Element("span")

        id = "tooltip-{}".format(text.replace(" ", "-"))

        elem.set("id", id)
        elem.text = text

        content = markdown.markdown(definition)
        if id not in JAVASCRIPT:
            JAVASCRIPT[id] = content.replace("'", "&#39;").replace("\n", " ")

        return elem


class DefinitionPostprocessor(Postprocessor):
    def __init__(self, js):
        self.js = js

    def run(self, text):
        # write out javascript to file

        tippytemplate = \
"""tippy('#{id}', {{
    content: '{html}',
    allowHTML: true,
    interactive: true,
}});
"""

        jsfile = self.js.getConfig("js_file")

        with open(jsfile, "w") as fp:
            for key in JAVASCRIPT:
                fp.write(tippytemplate.format(**{"id": key, "html": JAVASCRIPT[key]}))
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
            "css_path": [
                "docs/css/tooltips.css",
                "Location to output default CSS style.",
            ],
            "css_custom": [None, "Custom CSS to place in path."],
            "js_file": ["docs/javascripts/glossary.js", "Javascript path"]
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

    def extendMarkdown(self, md, md_globals):
        md.inlinePatterns["definition"] = DefinitionPattern(
            DEF_RE, md, configs=self.getConfigs(),
        )

        # Insert a postprocessor
        md.postprocessors.register(DefinitionPostprocessor(self), 'definition', 25)


def makeExtension(**kwargs):
    return MdTooltipLink(**kwargs)
