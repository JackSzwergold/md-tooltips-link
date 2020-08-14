import markdown
from mdtooltipslink import MdTooltipLink

txt = "@(parachain) test @(lol)"
res = markdown.markdown(txt, extensions=[MdTooltipLink()])
print(res)
