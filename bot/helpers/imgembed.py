import random
import requests
import re

from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageChops
from utils import files
from utils import console

def crop_center_square(im: Image.Image) -> Image.Image:
    if im.mode != "RGBA":
        im = im.convert("RGBA")

    w, h = im.size
    side = min(w, h)

    left = (w - side) // 2
    top = (h - side) // 2
    right = left + side
    bottom = top + side

    return im.crop((left, top, right, bottom))

def add_corners(im, rad):
    if im.mode != "RGBA":
        im = im.convert("RGBA")

    w, h = im.size

    # Create rounded rectangle mask
    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), (w, h)], radius=rad, fill=255)

    # Combine with existing alpha (if present)
    existing_alpha = im.split()[3]
    combined_alpha = ImageChops.multiply(existing_alpha, mask)

    im.putalpha(combined_alpha)

    return im

def rounded_rectangle(self: ImageDraw, xy, corner_radius, fill=None, outline=None):
    """Draw a rounded rectangle.
    Taken from a stackoverflow post somehwere"""
    upper_left_point = xy[0]
    bottom_right_point = xy[1]
    self.rectangle([(upper_left_point[0], upper_left_point[1] + corner_radius),
                    (bottom_right_point[0], bottom_right_point[1] - corner_radius)], fill=fill, outline=outline)
    self.rectangle([(upper_left_point[0] + corner_radius, upper_left_point[1]),
                    (bottom_right_point[0] - corner_radius, bottom_right_point[1])], fill=fill, outline=outline)
    self.pieslice(
        [upper_left_point, (upper_left_point[0] + corner_radius * 2, upper_left_point[1] + corner_radius * 2)], 180,
        270, fill=fill, outline=outline)
    self.pieslice(
        [(bottom_right_point[0] - corner_radius * 2, bottom_right_point[1] - corner_radius * 2), bottom_right_point], 0,
        90, fill=fill, outline=outline)
    self.pieslice([(upper_left_point[0], bottom_right_point[1] - corner_radius * 2),
                   (upper_left_point[0] + corner_radius * 2, bottom_right_point[1])], 90, 180, fill=fill,
                  outline=outline)
    self.pieslice([(bottom_right_point[0] - corner_radius * 2, upper_left_point[1]),
                   (bottom_right_point[0], upper_left_point[1] + corner_radius * 2)], 270, 360, fill=fill,
                  outline=outline)


ImageDraw.rounded_rectangle = rounded_rectangle


def get_wrapped_text(text: str, font: ImageFont, line_length: int):
    """Wrap text to a certain length.
    Taken from a stackoverflow post somewhere"""
    lines = ['']
    for word in text.split():
        if font.getlength(lines[-1] + word) < line_length:
            lines[-1] += word + ' '
        else:
            lines.append(word + ' ')

    return lines


def hex_to_rgb(hex: str) -> tuple:
    """Convert a hex colour to RGB."""
    hex = hex.lstrip('#')
    return tuple(int(hex[i:i + 2], 16) for i in (0, 2, 4))


class Field:
    def __init__(self, name: str, value: str):
        self.name = name
        self.value = value

class Embed:
    def __init__(self, title="", description="", colour="#AE00E5", color=""):
        self.title = title
        self.description = description.replace("`", "")
        self.footer = ""
        self.thumbnail = ""
        self.image = ""
        self.fields = []
        self.colour = None

        if colour != "":
            self.colour = colour
        elif color != "":
            self.colour = color  # for the americans

        self.title_font = ImageFont.truetype(files.resource_path("data/fonts/HostGrotesk-Bold.ttf"), 70)
        self.description_font = ImageFont.truetype(files.resource_path("data/fonts/HostGrotesk-Light.ttf"), 54)
        self.description_font_bold = ImageFont.truetype(files.resource_path("data/fonts/HostGrotesk-Bold.ttf"), 54)
        self.footer_font = ImageFont.truetype(files.resource_path("data/fonts/HostGrotesk-LightItalic.ttf"), 54)

        self.height = 50
        self.width = 1500
        self.wrap_width = self.width - 450
        
        self.thumbnail_resp = None
        self.thumbnail_gif = False
        self.waves = Image.open(files.resource_path("data/waves.png")).convert("RGBA")

    def set_thumbnail(self, url = ""): 
        self.thumbnail = url
        self.thumbnail_resp = requests.get(url)
    def set_image(self, url = ""): self.image = url
    def set_footer(self, text = "", icon_url = ""): self.footer = text
    def set_author(self, name = "", icon_url = "", url = ""): pass
    def add_field(self, name = "", value = "", inline = False): self.fields.append(Field(name, value))

    def setup_dimensions(self):
        if self.thumbnail == "":
            self.wrap_width = self.width - 150

        if self.title != "" and self.description != "":
            self.height += 200
        elif self.title != "" and self.description == "":
            self.height += 170
        elif self.title == "" and self.description != "":
            self.height += 50

        if self.description != "":
            for line in self.description.splitlines():
                wrap = get_wrapped_text(line, self.description_font, self.wrap_width)
                for _ in wrap:
                    self.height += 60

        if len(self.fields) > 0:
            for field in self.fields:
                self.height += 50
                for line in field.value.splitlines():
                    wrap = get_wrapped_text(line, self.description_font, self.wrap_width)
                    for _ in wrap:
                        self.height += 60

            self.height += 100

        if self.footer != "": self.height += 100
        if self.thumbnail != "" and self.height < 400: self.height = 400

    def draw_title(self, template, draw):
        if self.title != "":
            if self.thumbnail != "":
                title_bg_img = Image.new("RGBA", (self.width - 300 - 40 - 40 - 40, 135), (0, 0, 0, 0))
                ImageDraw.Draw(title_bg_img).rounded_rectangle([(0, 0), (title_bg_img.width, title_bg_img.height)], 20,
                                                               fill=(0, 0, 0, 50))
                template.alpha_composite(title_bg_img, (40, 40))
            else:
                title_bg_img = Image.new("RGBA", (self.width - 45 - 40, 135), (0, 0, 0, 0))
                ImageDraw.Draw(title_bg_img).rounded_rectangle([(0, 0), (title_bg_img.width, title_bg_img.height)], 20,
                                                               fill=(0, 0, 0, 50))
                template.alpha_composite(title_bg_img, (40, 40))

            draw.text((70, 62), self.title, (255, 255, 255), font=self.title_font)

    def draw_thumbnail(self, template, draw):
        if self.thumbnail != "":
            try:
                logo = Image.open(BytesIO(self.thumbnail_resp.content))
                logo = crop_center_square(logo)
                logo = logo.resize((300, 300), Image.LANCZOS)
                logo = add_corners(logo, 20)

                template.alpha_composite(logo, (self.width - 300 - 45, 40))
            except Exception:
                console.print_error("Failed to load thumbnail from theme.")

    def draw_description(self, template, draw):
        if self.description != "":
            if self.title != "":
                y_offset = 200
            else:
                y_offset = 50
            for desc_line in self.description.splitlines():
                wrap = get_wrapped_text(desc_line, self.description_font, self.wrap_width)

                for line in wrap:
                    x_offset = 60
                    pieces = re.findall(r'(?<=\*\*)(.*)(?=\*\*)', line)
                    new_line = []

                    for word in line.split("**"):
                        if word in pieces:
                            new_line.append(f"**{word}**")
                        else:
                            new_line.append(word)

                    for word in new_line:
                        if word.startswith("**") and word.endswith("**"):
                            draw.text((x_offset, y_offset), word.replace("**", ""), (255, 255, 255),
                                      font=self.description_font_bold)
                            x_offset += self.description_font_bold.getlength(word.replace("**", ""))
                        else:
                            draw.text((x_offset, y_offset), word, (255, 255, 255), font=self.description_font)
                            x_offset += self.description_font.getlength(word)

                    y_offset += 60

    def draw_footer(self, template, draw):
        if self.footer != "":
            draw.text((60, self.height - 100), self.footer, (180, 180, 180), font=self.footer_font)

    def draw_fields(self, template, draw):
        if len(self.fields) > 0:
            y_offset = 0

            if self.title != "" and self.description != "":
                y_offset = 200
                for line in self.description.splitlines():
                    wrap = get_wrapped_text(line, self.description_font, self.wrap_width)
                    for _ in wrap:
                        y_offset += 60
                
                y_offset += 50

            elif self.title != "" and self.description == "":
                y_offset == 170
            elif self.title == "" and self.description != "":
                y_offset = 50

                for line in self.description.splitlines():
                    wrap = get_wrapped_text(line, self.description_font, self.wrap_width)
                    for _ in wrap:
                        y_offset += 60

                y_offset += 50

            for field in self.fields:
                draw.text((60, y_offset), field.name, (255, 255, 255), font=self.description_font_bold)
                y_offset += 50

                for field_line in field.value.splitlines():
                    wrap = get_wrapped_text(field_line, self.description_font, self.wrap_width)

                    for line in wrap:
                        x_offset = 60
                        pieces = re.findall(r'(?<=\*\*)(.*)(?=\*\*)', line)
                        new_line = []

                        for word in line.split("**"):
                            if word in pieces:
                                new_line.append(f"**{word}**")
                            else:
                                new_line.append(word)

                        for word in new_line:
                            if word.startswith("**") and word.endswith("**"):
                                draw.text((x_offset, y_offset), word.replace("**", ""), (255, 255, 255), font=self.description_font_bold)
                                x_offset += self.description_font_bold.getlength(word.replace("**", ""))
                            else:
                                draw.text((x_offset, y_offset), word, (255, 255, 255), font=self.description_font)
                                x_offset += self.description_font.getlength(word)

                        y_offset += 60

                y_offset += 20

    def draw_background(self, template, draw):
        # draw background
        # draw.rounded_rectangle([(0, 0), (self.width - 15, self.height)], 25, fill=hex_to_rgb(self.colour))
        # draw.rounded_rectangle([(10, 0), (self.width - 10, self.height)], 25, fill=(30, 30, 30, 255))

        template.paste(self.waves,
                       (int(self.width / 2) - int(self.waves.width / 2), int(self.height / 2) - int(self.waves.height / 1.5)),
                       self.waves)

        # draw background image
        # background = Image.open("data/background.png").convert("RGBA")
        # background.putalpha(40)
        # background = background.resize((int(background.width * 3), int(background.height * 3)))

        # template.alpha_composite(background, (int(self.width / 2) - int(background.width / 2), int(self.height / 2) - int(background.height / 2)))

        draw.rectangle([(0, 0), (10, self.height)], fill=hex_to_rgb(self.colour))

    def draw(self):
        self.setup_dimensions()

        template = Image.new("RGBA", (self.width, self.height), (30, 30, 30, 255))
        draw = ImageDraw.Draw(template)

        self.draw_background(template, draw)
        self.draw_title(template, draw)
        self.draw_thumbnail(template, draw)
        self.draw_description(template, draw)
        self.draw_fields(template, draw)
        self.draw_footer(template, draw)

        return template

    def build_static_base(self):
        template = Image.new("RGBA", (self.width, self.height), (30, 30, 30, 255))
        draw = ImageDraw.Draw(template)

        self.draw_background(template, draw)
        self.draw_title(template, draw)
        self.draw_description(template, draw)
        self.draw_fields(template, draw)
        self.draw_footer(template, draw)

        return template
    
    def draw_animated(self):
        self.setup_dimensions()

        thumbnail = Image.open(BytesIO(self.thumbnail_resp.content))

        base = self.build_static_base()

        frames = []
        duration = thumbnail.info.get("duration", 100)

        # Limit frames for speed
        max_frames = 40
        step = max(1, thumbnail.n_frames // max_frames)

        for i in range(0, thumbnail.n_frames, step):
            thumbnail.seek(i)

            frame_image = thumbnail.convert("RGBA")
            frame_image = crop_center_square(frame_image)
            frame_image = frame_image.resize((300, 300), Image.LANCZOS)
            frame_image = add_corners(frame_image, 20)

            frame = base.copy()  # cheap copy
            frame.alpha_composite(frame_image, (self.width - 300 - 45, 40))

            frames.append(frame)

        return frames, duration * 1.5

    def save(self):
        thumbnail_is_gif = getattr(Image.open(BytesIO(self.thumbnail_resp.content)), "is_animated", False)
        extension = ".gif" if thumbnail_is_gif else ".png"
        path = f"embed-{random.randint(1000, 9999)}" + extension  # comment this out if youre running the script directly
        # path = "embed.png" # uncomment this if youre running the script directly
        
        if thumbnail_is_gif:
            frames, duration = self.draw_animated()
            frames[0].save(path, save_all=True, append_images=frames[1:], optimize=True, duration=duration, loop=0)
        else:
            final = self.draw()
            final.thumbnail((self.width // 2, self.height // 2), Image.LANCZOS)
            # final = final.resize((self.width // 2, self.height // 2), Image.LANCZOS)
            final.save(path, optimize=True, quality=20)
            
        return path


# if the file is run directly, run the main function
# this is for testing purposes
if __name__ == "__main__":
    embed = Embed(title="epic title", description="testing 123 sdjfhlskdjhflskdjhfsld\nmulti line tesT", colour="#ff0000")
    embed.set_footer(text="this is footer text, pretty cool")
    embed.set_thumbnail(url="https://github.com/GhostSelfbot/Branding/blob/main/ghost.png?raw=true")
    embed.add_field(name="field 1", value="this is a field")
    embed.add_field(name="field 2", value="this is a field")
    embed.save()