# -*- coding: utf-8 -*-
# pylint: disable=line-too-long

""" call ImageMagick command """

import os
import re
import shutil
import sys
import tempfile
import touch

import common
import mswindows

def pre_magick(file_in, destination):
    """
    file_in - original file for processing
    destination - processing directory
    file_out - fullname file for processing in destination
    """
    result = "OK"  # initial value
    if file_in is not None:
        if os.path.isfile(file_in):
            # Zakładanie katalogu na obrazki wynikowe o ile nie ma
            out_dir = os.path.join(os.path.dirname(file_in), destination)
            if os.path.isdir(out_dir) is False:
                try:
                    os.mkdir(out_dir)
                except:
                    print("! Error in pre_imagick: Nie można utworzyć katalogu na przemielone rysunki")
                    result = None
        else:
            result = None
    else:
        result = None

    if result == "OK":
        # Kopiowanie oryginału do miejsca mielenia
        file_out = os.path.join(out_dir, os.path.basename(file_in))
        if file_out is not None:
            try:
                shutil.copyfile(file_in, file_out)
            except IOError as error:
                print("! Error in pre_imagick: Unable to copy file. %s" % error)
                exit(1)
            except:
                print("! Error in pre_imagick: Unexpected error:", sys.exc_info())
                exit(1)
        else:
            file_out = None
            print("! pre_imagemagic: No selected file")
    else:
        file_out = None
    return file_out


def magick(cmd, file_out, command):
    """
    run imagemagick command.
    cmd - command for imagemagick
    file_out - fullname picture for processing
    command: it depends:
      convert, mogrify, composite - ImageMagick
      gm convert, gm mogrify, gm composite - GraphicsMagick
    """
    result = None
    if cmd != "":
        if file_out is not None:
            if os.path.isfile(file_out):
                file_out = common.spacja(file_out)
                command = magick_command(command)
                command = command + cmd + " " + file_out
                # print("Excute: ", command)
                try:
                    os.system(command)
                except:
                    print("! Error in imagick: " + command)
                    result = None
                else:
                    result = "OK"
            else:
                print("imagick: No file for processing")
        else:
            print("imagick: No file for imagick")
            result = None
    else:
        result = None
    return result


def magick_command(command):
    """
    make [Graphics|Image]Magick independent
    command: it depends:
    - ImageMagick:
      - Unix: convert, mogrify, composite
      - Windows: magick.exe convert, magick.exe mogrify, magick.exe composite
    - GraphicsMagick:
      - Unix: gm convert, gm mogrify, gm composite
      - Windows: gm.exe convert, gm.exe mogrify, gm.exe composite
    """
    if mswindows.windows() == 1:
        suffix = ".exe "
    else:
        suffix = " "
    tool = command.split()
    tool.insert(1, suffix)
    tool.extend(' ')
    result = "".join(tool)
    return result


def fonts_list_get(gm_or_im):
    """ get available font list from imagemagick """

    fonts_list = None
    file_font = common.spacja(os.path.join(tempfile.gettempdir(),
                                           "fonts_list"))
    touch.touch(file_font)
    command = "-list font > "
    result = magick(command, common.spacja(file_font),
                    gm_or_im + "convert")
    if result is not None:
        try:
            file = open(file_font, "r")
        except:
            print("!fonts_list_get: cannot read file_font")
        else:
            fonts_list = []
            if gm_or_im == "gm ":
                # GraphicsMagick format
                for line in file:
                    if re.search("\d$", line) is not None:
                        line = re.findall('^[-a-zA-Z]+', line)
                        fonts_list.append(line)
            else:
                # ImageMagick format
                for line in file:
                    if re.search("Font", line) is not None:
                        line = re.sub('^[ ]+Font:[ ]*', "", line)
                        line = re.sub('\n', "", line)
                        fonts_list.append(line)
            file.close()
            try:
                os.remove(file_font)
            except:
                print("!fonts_list_get: cannot remove file_font")

    if fonts_list is None or len(fonts_list) == 0:
        fonts_list = ["Helvetica"]
    return fonts_list

# EOF
