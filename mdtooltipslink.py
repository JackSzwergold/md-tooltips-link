import markdown
from markdown.extensions import Extension
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
  border-left: 3px solid rgb(43, 155, 70);
  padding: 0.5em 0.8em 0.8em 0.8em;
}

#tooltipheader {
  font-size: 110%;
  font-weight: bold;
  display: block;
  color: rgb(43, 155, 70);
  padding: 0.2em 0 0.6em 0;
}

.tooltip:hover .tooltiptext {
  visibility: visible;
}
"""


DEF_RE = r"(@\()(?P<text>.+?)\)"


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

        elem.set("class", "tooltip")

        # because overall content is with a <p>-tag it does not like <p> or <div>
        # within the hover over box (for the moment just remove the preceeding and
        # trailing <p>'s added my markdown processing.
        content = markdown.markdown(definition).lstrip("<p>").rstrip("</p>").strip()

        # add a header within the tool tip
        header = ""
        if self.header:
            header = '<em id="tooltipheader">"{}"</em>'.format(text)

        inner = '{}<span class="tooltiptext">{}{}</span>'.format(text, header, content)
        placeholder = self.md.htmlStash.store(inner)
        elem.text = placeholder

        return elem


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
        }

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

    def extendMarkdown(self, md, md_globals):
        md.inlinePatterns["definition"] = DefinitionPattern(
            DEF_RE, md, configs=self.getConfigs()
        )


def makeExtension(**kwargs):
    return MdTooltipLink(**kwargs)
