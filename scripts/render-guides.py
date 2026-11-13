"""Render docs/*.md into the static GitHub Pages site."""

from html import escape
from pathlib import Path
import re
from urllib.parse import unquote

from markdown_it import MarkdownIt

DOCS = Path(__file__).resolve().parents[1] / "docs"
markdown = MarkdownIt("commonmark", {"html": False}).enable("table")


def render_guide(path):
    tokens = markdown.parse(path.read_text(encoding="utf-8"))
    title = tokens[1].content
    heading_ids = set()
    for index, token in enumerate(tokens):
        if token.type != "heading_open":
            continue
        heading = "".join(part.content for part in tokens[index + 1].children)
        base = re.sub(r"[^\w\s-]", "", heading.lower()).replace(" ", "-")
        anchor = base
        suffix = 1
        while anchor in heading_ids:
            anchor = f"{base}-{suffix}"
            suffix += 1
        heading_ids.add(anchor)
        token.attrSet("id", anchor)

    for token in tokens:
        for child in token.children or []:
            if child.type == "link_open":
                href = unquote(child.attrGet("href"))
                if re.match(r"^[\w-]+\.md(?:#|$)", href):
                    child.attrSet("href", href.replace(".md", ".html", 1))

    markdown.renderer.rules["table_open"] = lambda *_: '<div class="table-scroll"><table>\n'
    markdown.renderer.rules["table_close"] = lambda *_: '</table></div>\n'
    body = markdown.renderer.render(tokens, markdown.options, {})
    path.with_suffix(".html").write_text(f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="description" content="{escape(title)} · 砚插件开发文档">
  <title>{escape(title)} · 砚</title>
  <link rel="icon" href="../assets/icon.png">
  <link rel="stylesheet" href="../style.css?v=4">
</head>
<body>
  <header>
    <a class="brand" href="../index.html"><img src="../assets/icon.png" alt="">砚</a>
    <nav aria-label="主导航">
      <a href="../index.html">概览</a>
      <a href="../plugins.html">插件开发</a>
      <a href="../support.html">支持</a>
    </nav>
  </header>
  <main class="document guide">
    <article>
{body}    </article>
  </main>
  <footer>
    <a href="../plugins.html">返回插件开发</a>
    <a href="{path.name}">Markdown 源文档</a>
  </footer>
</body>
</html>
""", encoding="utf-8")


if __name__ == "__main__":
    for guide in sorted(DOCS.glob("*.md")):
        render_guide(guide)
