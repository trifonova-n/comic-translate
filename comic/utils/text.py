from PIL import Image, ImageDraw, ImageFont, ImageFilter
import string


def multiline_text(draw, pos, text, box_width, box_height, font, color=0, place='left', contour=0, contour_color=255, spacing=0):
    justify_last_line = False
    x, y = pos
    if contour > 0:
        mask = Image.new("L", draw.im.size, 0)
        mask_draw = ImageDraw.Draw(mask)
        multiline_text(mask_draw, pos, text, box_width=box_width, box_height=box_height, font=font,
                       color=255, place=place, contour=0, spacing=spacing)
        mask = mask.filter(ImageFilter.MaxFilter(contour*2 + 1))
        draw.bitmap((0, 0), mask, fill=contour_color)

    h, w = 0, 0
    lines = []
    line = []
    words = text.split()
    line_spacing = font.getsize(string.ascii_letters)[1] + spacing
    for word in words:
        new_line = ' '.join(line + [word])
        size = font.getsize(new_line)
        if size[0] <= box_width:
            line.append(word)
            w = max(w, size[0])
        else:
            h += line_spacing
            lines.append(line)
            line = [word]
    if line:
        lines.append(line)
        h += line_spacing
        size = font.getsize(line[0])
        w = max(w, size[0])
    lines = [' '.join(line) for line in lines if line]
    height = y + box_height // 2 - h // 2
    y = height
    x_min = x + w
    for index, line in enumerate(lines):
        if place == 'left':
            write_text(draw, (x, height), line, font=font, color=color)
        elif place == 'right':
            total_size = font.getsize(line)
            x_left = x + box_width - total_size[0]
            if x_left < x_min:
                x_min = x_left
            write_text(draw, (x_left, height), line, font=font, color=color)
        elif place == 'center':
            total_size = font.getsize(line)
            x_left = int(x + ((box_width - total_size[0]) / 2))
            if x_left < x_min:
                x_min = x_left
            write_text(draw, (x_left, height), line, font=font, color=color)
        elif place == 'justify':
            words = line.split()
            if (index == len(lines) - 1 and not justify_last_line) or \
                    len(words) == 1:
                write_text(draw, (x, height), line, font=font, color=color)
                continue
            line_without_spaces = ''.join(words)
            total_size = font.getsize(line_without_spaces)
            space_width = (box_width - total_size[0]) / (len(words) - 1.0)
            start_x = x
            for word in words[:-1]:
                write_text(draw, (start_x, height), word, font=font, color=color)
                word_size = font.getsize(word)
                start_x += word_size[0] + space_width
            last_word_size = font.getsize(words[-1])
            last_word_x = x + box_width - last_word_size[0]
            write_text(draw, (last_word_x, height), words[-1], font=font, color=color)
        height += line_spacing
    return x_min, y, w, h


def write_text(draw, pos, text, font, color=0, contour=0, contour_color=255):
    x, y = pos

    if contour > 0:
        mask = Image.new("L", draw.im.size, 0)
        mask_draw = ImageDraw.Draw(mask)
        write_text(mask_draw, pos, text, font=font, color=255, contour=0)
        mask = mask.filter(ImageFilter.MaxFilter(contour))
        draw.bitmap((0, 0), mask, contour_color)

    text_size = font.getsize(text)
    draw.text((x, y), text, font=font, fill=color)
    return text_size


def write_contour(draw, pos, text, font, color=0, contour_color=255):
    mask = Image.new("L", draw.im.size, 0)
    mask_draw = ImageDraw.Draw(mask)
    write_text(mask_draw, pos, text, font, 255)
    mask = mask.filter(ImageFilter.MaxFilter(5))
    draw.bitmap((0, 0), mask, fill=contour_color)
    write_text(draw, pos, text, font, color)
