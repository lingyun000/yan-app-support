from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
root=Path(__file__).resolve().parent.parent/'assets'
font='/System/Library/Fonts/Hiragino Sans GB.ttc'
items=[('editor','编辑，让结构清晰。','多标签文本编辑 · JSON 格式化与校验'),('tools','常用工具，在一个工作台。','搜索、收藏与工作标签 · 26 个工具入口'),('base64','编码转换，输入即更新。','Base64 与 Base64URL · 双向转换与文件导入'),('http','请求与响应，一目了然。','HTTP/API 工作台 · 本地演示服务器的真实响应')]
for stem,title,subtitle in items:
    canvas=Image.new('RGB',(2880,1800),'#f4f6fa')
    draw=ImageDraw.Draw(canvas)
    draw.text((140,55),'砚 · macOS 开发工具箱',font=ImageFont.truetype(font,28),fill='#536780')
    draw.text((140,105),title,font=ImageFont.truetype(font,68),fill='#182a45')
    draw.text((143,205),subtitle,font=ImageFont.truetype(font,32),fill='#536780')
    source=Image.open(root/f'{stem}-raw.png').convert('RGB')
    source.thumbnail((2600,1440),Image.Resampling.LANCZOS)
    x=(2880-source.width)//2;y=300+(1440-source.height)//2
    shadow=Image.new('RGBA',canvas.size,(0,0,0,0))
    sd=ImageDraw.Draw(shadow);sd.rounded_rectangle((x,y+12,x+source.width,y+source.height+12),radius=16,fill=(21,39,65,45))
    shadow=shadow.filter(ImageFilter.GaussianBlur(22))
    canvas=Image.alpha_composite(canvas.convert('RGBA'),shadow)
    canvas.paste(source,(x,y))
    canvas.convert('RGB').save(root/f'{stem}.png',optimize=True)
    print(stem,source.size)
page=root.parent/'index.html';s=page.read_text()
s=s.replace('<div class="screens" id="gallery"></div>','<div class="screens" id="gallery">'+''.join(f'<figure><img src="assets/{stem}.png" alt="{title} {subtitle}" loading="lazy" width="2880" height="1800"><figcaption>{subtitle}</figcaption></figure>' for stem,title,subtitle in items)+'</div>')
page.write_text(s)
