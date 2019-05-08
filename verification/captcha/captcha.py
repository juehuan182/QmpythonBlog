import os
import string
import random
# Image:是一个画板(context)  ImageDraw:是一个画笔  ImageFont:画笔的字体
from PIL import Image, ImageDraw, ImageFont


class Captcha:
    # 字体的路径
    font_path = os.path.join(os.path.dirname(__file__), 'MTCORSVA.TTF')
    # 验证码位数
    number = 4
    # 验证码(宽高)
    size = (75, 36)
    # 背景颜色，默认为白色 rgb(red,green,blue)
    bg_color = (0, 0, 0, 0)  #RGBA(4通道为透明通道，0为完全透明， 256为不透明)
    # 随机字体颜色 (0, 0, 0)
    font_color = (random.randint(230, 255), random.randint(200, 255), random.randint(100, 255))
    # 验证码字体大小
    font_size = 25
    # 随机干扰线颜色。
    line_color = (random.randint(123, 250), random.randint(100, 200), random.randint(0, 100))
    # 是否绘制干扰线
    is_draw_line = True
    # 是否绘制干扰点
    is_draw_point = True
    # 干扰线的数量
    line_number = 5

    # a~zA~Z1~9  因为 0 O o
    SOURCE = list(string.ascii_letters)
    for index in range(1, 10):
        SOURCE.append(str(index))

    @classmethod
    def gene_text(cls):
        """
        用来随机生成一个字符串(包括英文和数字)
        :return:  text
        """
        # number是生成验证码的位数 sx2D
        text = ''.join(random.sample(cls.SOURCE, cls.number))
        return text

    @classmethod
    def __gene_line(cls, draw, width, height):
        """绘制干扰线"""
        begin = (random.randint(0, width), random.randint(0, height))
        end = (random.randint(0, width), random.randint(0, height))
        draw.line([begin, end], fill=cls.line_color)

    @classmethod
    def __gene_points(cls, draw, point_chance, width, height):
        """绘制干扰点"""
        # 大小限制在[0, 100]
        chance = min(100, max(0, int(point_chance)))
        for w in range(width):
            for h in range(height):
                tmp = random.randint(0, 100)
                if tmp > 100 - chance:
                    draw.point((w, h), fill=(0, 0, 0))

    @classmethod
    def gene_code(cls):
        """
        绘制图形验证码
        # sx2D image[ pillow function ]
        :return:  [text, image]
        """
        # 宽和高
        width, height = cls.size
        # 创建图片
        image = Image.new('RGBA', (width, height), cls.bg_color)
        # 验证码的字体
        font = ImageFont.truetype(cls.font_path, cls.font_size)
        # 创建画笔
        draw = ImageDraw.Draw(image)
        # 生成验证码字符串
        text = cls.gene_text()
        # 获取字体宽高
        font_width, font_height = font.getsize(text)
        # 填充字符串
        draw.text(((width - font_width) / 2, (height - font_height) / 2), text, font=font, fill=cls.font_color)
        # 如果需要绘制干扰线
        if cls.is_draw_line:
            # 遍历 line_number 次, 就是画l ine_number 根线条
            for x in range(0, cls.line_number):
                cls.__gene_line(draw, width, height)
        # 如果需要绘制噪点
        if cls.is_draw_point:
            cls.__gene_points(draw, 2, width, height)
        return [text, image]
