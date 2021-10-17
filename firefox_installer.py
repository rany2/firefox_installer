#!/usr/bin/env python3

import shutil
import tarfile
from base64 import b64decode
from os import environ, makedirs
from os.path import dirname, expanduser, isdir
from os.path import join as path_join
from tempfile import NamedTemporaryFile, mkdtemp
from typing import Any, List, Tuple, Union
from urllib.request import urlopen

from lxml.html import parse


def get_xdg_data_home() -> str:
    try:
        return environ["XDG_DATA_HOME"]
    except KeyError:
        return expanduser("~/.local/share")


def parsed_download_page() -> Any:
    with NamedTemporaryFile() as fp:
        print("Downloading and parsing the download page...")
        with urlopen("https://www.mozilla.org/en-US/firefox/all/") as resp:
            shutil.copyfileobj(resp, fp)
        _parse_ret = parse(fp.name)
        print("Download page was downloaded and parsed.")
        return _parse_ret


def prompt(prompt_text: str, array: Union[List[str], Tuple[str]]) -> str:
    print()
    print(prompt_text)
    for x, y in enumerate(array):
        print(f"  {x+1}: {y}")
    print()

    while True:
        user_input = input("Your number: ")
        try:
            user_input = int(user_input)
        except ValueError:
            continue

        if 0 < user_input < len(array) + 1:
            break

    for x, y in enumerate(array):
        if x + 1 == user_input:
            return y


def get_product_selection(doc: Any) -> str:
    product_options = []
    for x in doc.xpath('//select[@id="select-product"]//option'):
        if x.values()[0].startswith("desktop_"):
            product_options.append(x.values()[0])
    return prompt("Pick a product:", product_options)


def get_platform_selection(doc: Any, product_select: str) -> str:
    platform_options = []
    for x in doc.xpath(f'//select[@id="select_{product_select}_platform"]//option'):
        if x.values()[0].startswith("linux"):
            platform_options.append(x.values()[0])
    return prompt("Pick a platform:", platform_options)


def get_language_selection(doc: Any, product_select: str) -> str:
    language_options = []
    for x in doc.xpath(f'//select[@id="select_{product_select}_language"]//option'):
        language_options.append(x.values()[0])
    return prompt("Pick a language:", language_options)


def get_current_href(
    doc: Any, product_select: str, language_select: str, platform_select: str
) -> str:
    for x in doc.xpath(
        f'//ol [@data-product="{product_select}"] //li[@data-language="{language_select}"]//a'
    ):
        is_good = -1
        current_href = ""
        for k, v in zip(x.keys(), x.values()):
            if k == "data-download-version" and v == platform_select:
                is_good += 1
            elif k == "data-link-type" and v == "download":
                is_good += 1
            elif k == "href":
                is_good += 1
                current_href = v

        if is_good == 2:
            return current_href


def download_and_extract(url: str, extract_dir: str) -> None:
    with NamedTemporaryFile(mode="w+b") as fp:
        print()
        print("Downloading...")
        with urlopen(url) as resp:
            shutil.copyfileobj(resp, fp)
        print("Download complete.")
        print()

        if isdir(extract_dir):
            print("Removing old Firefox installation...")
            print("You will not lose your profiles or data.")
            shutil.rmtree(extract_dir)
            print("Old Firefox installation removed.")
            print()

        print("Extracting...")
        try:
            temp_extract = mkdtemp()
            with tarfile.open(fp.name) as tar:
                tar.extractall(temp_extract)
            shutil.move(f"{temp_extract}/firefox", f"{extract_dir}")
            print("Extract complete.")
        finally:
            shutil.rmtree(f"{temp_extract}")


def create_desktop(
    product_select: str,
    platform_select: str,
    language_select: str,
    extract_dir: str,
) -> None:
    _release_type = product_select
    wm_class = "Firefox"
    if product_select == "desktop_release":
        product_select = ""
        wm_class = "Firefox"
    elif product_select == "desktop_beta":
        product_select = " Beta"
        wm_class = "Firefox"
    elif product_select == "desktop_developer":
        product_select = " Developer Edition"
        wm_class = "Firefox Developer Edition"
    elif product_select == "desktop_nightly":
        product_select = " Nightly"
        wm_class = "Nightly"
    elif product_select == "desktop_esr":
        product_select = " ESR"
        wm_class = "Firefox"

    # noinspection SpellCheckingInspection
    desktop_data = b64decode(
        b"W0Rlc2t0b3AgRW50cnldClZlcnNpb249MS4wCk5hbWU9RmlyZWZveCUlJVJFTEVBU0VfVFlQRSUlJQpHZW5lcmljTmFtZT1XZWIgQnJvd3NlcgpHZW5lcmljTmFtZVthcl092YXYqti12YHYrSDZiNmQ2KgKR2VuZXJpY05hbWVbYXN0XT1SZXN0b2xhZG9yIFdlYgpHZW5lcmljTmFtZVtibl094KaT4Kav4Ka84KeH4KasIOCmrOCnjeCmsOCmvuCmieCmnOCmvuCmsApHZW5lcmljTmFtZVtjYV09TmF2ZWdhZG9yIHdlYgpHZW5lcmljTmFtZVtjc109V2Vib3bDvSBwcm9obMOtxb5lxI0KR2VuZXJpY05hbWVbZGFdPVdlYmJyb3dzZXIKR2VuZXJpY05hbWVbZGVdPVdlYmJyb3dzZXIKR2VuZXJpY05hbWVbZWxdPc6gzrXPgc65zrfOs863z4TOrs+CIM60zrnOsc60zrnOus+Ez43Ov8+FCkdlbmVyaWNOYW1lW2VzXT1OYXZlZ2Fkb3Igd2ViCkdlbmVyaWNOYW1lW2V0XT1WZWViaWJyYXVzZXIKR2VuZXJpY05hbWVbZmFdPdmF2LHZiNix2q/YsSDYp9uM2YbYqtix2YbYqtuMCkdlbmVyaWNOYW1lW2ZpXT1XV1ctc2VsYWluCkdlbmVyaWNOYW1lW2ZyXT1OYXZpZ2F0ZXVyIFdlYgpHZW5lcmljTmFtZVtnbF09TmF2ZWdhZG9yIFdlYgpHZW5lcmljTmFtZVtoZV0915PXpNeT16TXnyDXkNeZ16DXmNeo16DXmApHZW5lcmljTmFtZVtocl09V2ViIHByZWdsZWRuaWsKR2VuZXJpY05hbWVbaHVdPVdlYmLDtm5nw6lzesWRCkdlbmVyaWNOYW1lW2l0XT1Ccm93c2VyIFdlYgpHZW5lcmljTmFtZVtqYV0944Km44Kn44OW44O744OW44Op44Km44K2CkdlbmVyaWNOYW1lW2tvXT3sm7kg67iM65287Jqw7KCACkdlbmVyaWNOYW1lW2t1XT1HZXJva2EgdG9yw6oKR2VuZXJpY05hbWVbbHRdPUludGVybmV0byBuYXLFoXlrbMSXCkdlbmVyaWNOYW1lW25iXT1OZXR0bGVzZXIKR2VuZXJpY05hbWVbbmxdPVdlYmJyb3dzZXIKR2VuZXJpY05hbWVbbm5dPU5ldHRsZXNhcgpHZW5lcmljTmFtZVtub109TmV0dGxlc2VyCkdlbmVyaWNOYW1lW3BsXT1QcnplZ2zEhWRhcmthIFdXVwpHZW5lcmljTmFtZVtwdF09TmF2ZWdhZG9yIFdlYgpHZW5lcmljTmFtZVtwdF9CUl09TmF2ZWdhZG9yIFdlYgpHZW5lcmljTmFtZVtyb109TmF2aWdhdG9yIEludGVybmV0CkdlbmVyaWNOYW1lW3J1XT3QktC10LEt0LHRgNCw0YPQt9C10YAKR2VuZXJpY05hbWVbc2tdPUludGVybmV0b3bDvSBwcmVobGlhZGHEjQpHZW5lcmljTmFtZVtzbF09U3BsZXRuaSBicnNrYWxuaWsKR2VuZXJpY05hbWVbc3ZdPVdlYmJsw6RzYXJlCkdlbmVyaWNOYW1lW3RyXT1XZWIgVGFyYXnEsWPEsQpHZW5lcmljTmFtZVt1Z1092KrZiNix2YPbhtix2q/biApHZW5lcmljTmFtZVt1a1090JLQtdCxLdCx0YDQsNGD0LfQtdGACkdlbmVyaWNOYW1lW3ZpXT1UcsOsbmggZHV54buHdCBXZWIKR2VuZXJpY05hbWVbemhfQ05dPee9kee7nOa1j+iniOWZqApHZW5lcmljTmFtZVt6aF9UV10957ay6Lev54CP6Ka95ZmoCkNvbW1lbnQ9QnJvd3NlIHRoZSBXZWIKQ29tbWVudFthcl092KrYtdmB2K0g2KfZhNmI2ZDYqApDb21tZW50W2FzdF09UmVzdG9sYSBwZWxhIFJlZGUKQ29tbWVudFtibl094KaH4Kao4KeN4Kaf4Ka+4Kaw4Kao4KeH4KafIOCmrOCnjeCmsOCmvuCmieCmnCDgppXgprDgp4HgpqgKQ29tbWVudFtjYV09TmF2ZWd1ZXUgcGVyIGVsIHdlYgpDb21tZW50W2NzXT1Qcm9obMOtxb5lbsOtIHN0csOhbmVrIFdvcmxkIFdpZGUgV2VidQpDb21tZW50W2RhXT1TdXJmIHDDpSBpbnRlcm5ldHRldApDb21tZW50W2RlXT1JbSBJbnRlcm5ldCBzdXJmZW4KQ29tbWVudFtlbF09zpzPgM6/z4HOtc6vz4TOtSDOvc6xIM+AzrXPgc65zrfOs863zrjOtc6vz4TOtSDPg8+Ezr8gzrTOuc6xzrTOr866z4TPhc6/IChXZWIpCkNvbW1lbnRbZXNdPU5hdmVndWUgcG9yIGxhIHdlYgpDb21tZW50W2V0XT1MZWhpdHNlIHZlZWJpCkNvbW1lbnRbZmFdPdi12YHYrdin2Kog2LTYqNqp2Ycg2KzZh9in2YbbjCDYp9uM2YbYqtix2YbYqiDYsdinINmF2LHZiNixINmG2YXYp9uM24zYrwpDb21tZW50W2ZpXT1TZWxhYSBJbnRlcm5ldGluIFdXVy1zaXZ1amEKQ29tbWVudFtmcl09TmF2aWd1ZXIgc3VyIGxlIFdlYgpDb21tZW50W2dsXT1OYXZlZ2FyIHBvbGEgcmVkZQpDb21tZW50W2hlXT3Xktec15nXqdeUINeR16jXl9eR15kg15TXkNeZ16DXmNeo16DXmApDb21tZW50W2hyXT1QcmV0cmHFvml0ZSB3ZWIKQ29tbWVudFtodV09QSB2aWzDoWdow6Fsw7MgYsO2bmfDqXN6w6lzZQpDb21tZW50W2l0XT1Fc3Bsb3JhIGlsIHdlYgpDb21tZW50W2phXT3jgqbjgqfjg5bjgpLplrLopqfjgZfjgb7jgZkKQ29tbWVudFtrb1097Ju57J2EIOuPjOyVhCDri6Tri5nri4jri6QKQ29tbWVudFtrdV09TGkgdG9yw6ogYmlnZXJlCkNvbW1lbnRbbHRdPU5hcsWheWtpdGUgaW50ZXJuZXRlCkNvbW1lbnRbbmJdPVN1cmYgcMOlIG5ldHRldApDb21tZW50W25sXT1WZXJrZW4gaGV0IGludGVybmV0CkNvbW1lbnRbbm5dPVN1cmYgcMOlIG5ldHRldApDb21tZW50W25vXT1TdXJmIHDDpSBuZXR0ZXQKQ29tbWVudFtwbF09UHJ6ZWdsxIVkYW5pZSBzdHJvbiBXV1cKQ29tbWVudFtwdF09TmF2ZWd1ZSBuYSBJbnRlcm5ldApDb21tZW50W3B0X0JSXT1OYXZlZ3VlIG5hIEludGVybmV0CkNvbW1lbnRbcm9dPU5hdmlnYcibaSBwZSBJbnRlcm5ldApDb21tZW50W3J1XT3QlNC+0YHRgtGD0L8g0LIg0JjQvdGC0LXRgNC90LXRggpDb21tZW50W3NrXT1QcmVobGlhZGFuaWUgaW50ZXJuZXR1CkNvbW1lbnRbc2xdPUJyc2thanRlIHBvIHNwbGV0dQpDb21tZW50W3N2XT1TdXJmYSBww6Ugd2ViYmVuCkNvbW1lbnRbdHJdPcSwbnRlcm5ldCd0ZSBHZXppbmluCkNvbW1lbnRbdWddPdiv24fZhtmK2KfYr9mJ2YPZiSDYqtmI2LHYqNuV2KrZhNuV2LHZhtmJINmD24bYsdqv2YnZhNmJINio2YjZhNmJ2K/bhwpDb21tZW50W3VrXT3Qn9C10YDQtdCz0LvRj9C0INGB0YLQvtGA0ZbQvdC+0Log0IbQvdGC0LXRgNC90LXRgtGDCkNvbW1lbnRbdmldPcSQ4buDIGR1eeG7h3QgY8OhYyB0cmFuZyB3ZWIKQ29tbWVudFt6aF9DTl095rWP6KeI5LqS6IGU572RCkNvbW1lbnRbemhfVFddPeeAj+imvee2sumam+e2sui3rwpFeGVjPSUlJUVYVFJBQ1RfRElSJSUlL2ZpcmVmb3ggJXUKSWNvbj0lJSVFWFRSQUNUX0RJUiUlJS9icm93c2VyL2Nocm9tZS9pY29ucy9kZWZhdWx0L2RlZmF1bHQxMjgucG5nClRlcm1pbmFsPWZhbHNlClR5cGU9QXBwbGljYXRpb24KTWltZVR5cGU9dGV4dC9odG1sO3RleHQveG1sO2FwcGxpY2F0aW9uL3hodG1sK3htbDthcHBsaWNhdGlvbi92bmQubW96aWxsYS54dWwreG1sO3RleHQvbW1sO3gtc2NoZW1lLWhhbmRsZXIvaHR0cDt4LXNjaGVtZS1oYW5kbGVyL2h0dHBzOwpTdGFydHVwTm90aWZ5PXRydWUKU3RhcnR1cFdNQ2xhc3M9JSUlV01fQ0xBU1MlJSUKQ2F0ZWdvcmllcz1OZXR3b3JrO1dlYkJyb3dzZXI7CktleXdvcmRzPXdlYjticm93c2VyO2ludGVybmV0OwpBY3Rpb25zPW5ldy13aW5kb3c7bmV3LXByaXZhdGUtd2luZG93O3Byb2ZpbGUtbWFuYWdlci13aW5kb3c7CgpbRGVza3RvcCBBY3Rpb24gbmV3LXdpbmRvd10KTmFtZT1OZXcgV2luZG93Ck5hbWVbYWNoXT1EaXJpY2EgbWFueWVuCk5hbWVbYWZdPU51d2UgdmVuc3RlcgpOYW1lW2FuXT1OdWV2YSBmaW5lc3RyYQpOYW1lW2FyXT3Zhtin2YHYsNipINis2K/Zitiv2KkKTmFtZVthc1094Kao4Kak4KeB4KaoIOCmieCmh+CmqOCnjeCmoeCniwpOYW1lW2FzdF09VmVudGFuYSBudWV2YQpOYW1lW2F6XT1ZZW5pIFDJmW5jyZlyyZkKTmFtZVtiZV090J3QvtCy0LDQtSDQsNC60L3QvgpOYW1lW2JnXT3QndC+0LIg0L/RgNC+0LfQvtGA0LXRhgpOYW1lW2JuX0JEXT3gpqjgpqTgp4Hgpqgg4KaJ4KaH4Kao4KeN4Kah4KeLIChOKQpOYW1lW2JuX0lOXT3gpqjgpqTgp4Hgpqgg4KaJ4KaH4Kao4KeN4Kah4KeLCk5hbWVbYnJdPVByZW5lc3RyIG5ldmV6Ck5hbWVbYnJ4XT3gpJfgpYvgpKbgpL7gpKgg4KSJ4KSH4KSo4KWN4KShJyhOKQpOYW1lW2JzXT1Ob3ZpIHByb3pvcgpOYW1lW2NhXT1GaW5lc3RyYSBub3ZhCk5hbWVbY2FrXT1LJ2FrJ2EnIHR6dXfDpGNoCk5hbWVbY3NdPU5vdsOpIG9rbm8KTmFtZVtjeV09RmZlbmVzdHIgTmV3eWRkCk5hbWVbZGFdPU55dCB2aW5kdWUKTmFtZVtkZV09TmV1ZXMgRmVuc3RlcgpOYW1lW2RzYl09Tm93ZSB3b2tubwpOYW1lW2VsXT3Onc6tzr8gz4DOsc+BzqzOuM+Fz4HOvwpOYW1lW2VuX0dCXT1OZXcgV2luZG93Ck5hbWVbZW5fVVNdPU5ldyBXaW5kb3cKTmFtZVtlbl9aQV09TmV3IFdpbmRvdwpOYW1lW2VvXT1Ob3ZhIGZlbmVzdHJvCk5hbWVbZXNfQVJdPU51ZXZhIHZlbnRhbmEKTmFtZVtlc19DTF09TnVldmEgdmVudGFuYQpOYW1lW2VzX0VTXT1OdWV2YSB2ZW50YW5hCk5hbWVbZXNfTVhdPU51ZXZhIHZlbnRhbmEKTmFtZVtldF09VXVzIGFrZW4KTmFtZVtldV09TGVpaG8gYmVycmlhCk5hbWVbZmFdPdm+2YbYrNix2Ycg2KzYr9uM2K8KTmFtZVtmZl09SGVub3JkZSBIZXNlcmUKTmFtZVtmaV09VXVzaSBpa2t1bmEKTmFtZVtmcl09Tm91dmVsbGUgZmVuw6p0cmUKTmFtZVtmeV9OTF09TmlqIGZpbnN0ZXIKTmFtZVtnYV9JRV09RnVpbm5lb2cgTnVhCk5hbWVbZ2RdPVVpbm5lYWcgw7lyCk5hbWVbZ2xdPU5vdmEgeGFuZWxhCk5hbWVbZ25dPU92ZXTDoyBweWFodQpOYW1lW2d1X0lOXT3gqqjgqrXgq4Ag4Kq14Kq/4Kqo4KuN4Kqh4KuLCk5hbWVbaGVdPdeX15zXldefINeX15PXqQpOYW1lW2hpX0lOXT3gpKjgpK/gpL4g4KS14KS/4KSC4KSh4KWLCk5hbWVbaHJdPU5vdmkgcHJvem9yCk5hbWVbaHNiXT1Ob3dlIHdva25vCk5hbWVbaHVdPcOaaiBhYmxhawpOYW1lW2h5X0FNXT3VhtW41oAg1YrVodW/1bjWgtWw1aHVtgpOYW1lW2lkXT1KZW5kZWxhIEJhcnUKTmFtZVtpc109TsO9ciBnbHVnZ2kKTmFtZVtpdF09TnVvdmEgZmluZXN0cmEKTmFtZVtqYV095paw44GX44GE44Km44Kj44Oz44OJ44KmCk5hbWVbamFfSlAtbWFjXT3mlrDopo/jgqbjgqTjg7Pjg4njgqYKTmFtZVtrYV094YOQ4YOu4YOQ4YOa4YOYIOGDpOGDkOGDnOGDr+GDkOGDoOGDkApOYW1lW2trXT3QltCw0qPQsCDRgtC10YDQtdC30LUKTmFtZVtrbV094Z6U4Z6E4Z+S4Z6i4Z694Z6F4Z6Q4Z+S4Z6Y4Z64Ck5hbWVba25dPeCyueCziuCyuCDgspXgsr/gsp/gspXgsr8KTmFtZVtrb1097IOIIOywvQpOYW1lW2tva1094KSo4KS14KWH4KSCIOCknOCkqOClh+CksgpOYW1lW2tzXT3Zhtim2KYg2YjZkNmG2ojZiApOYW1lW2xpal09TmV1dm8gYmFyY29uCk5hbWVbbG9dPeC6q+C6meC7ieC6suC6leC7iOC6suC6h+C7g+C6q+C6oeC7iApOYW1lW2x0XT1OYXVqYXMgbGFuZ2FzCk5hbWVbbHRnXT1KYXVucyBsxatncwpOYW1lW2x2XT1KYXVucyBsb2dzCk5hbWVbbWFpXT3gpKjgpLUg4KS14KS/4KSC4KSh4KWLCk5hbWVbbWtdPdCd0L7QsiDQv9GA0L7Qt9C+0YDQtdGGCk5hbWVbbWxdPeC0quC1geC0pOC0v+C0ryDgtJzgtL7gtLLgtJXgtIIKTmFtZVttcl094KSo4KS14KWA4KSoIOCkquCkn+CksgpOYW1lW21zXT1UZXRpbmdrYXAgQmFydQpOYW1lW215XT3hgJ3hgIThgLrhgLjhgJLhgK3hgK/hgLjhgKHhgJ7hgIXhgLoKTmFtZVtuYl9OT109Tnl0dCB2aW5kdQpOYW1lW25lX05QXT3gpKjgpK/gpL7gpIEg4KS44KSe4KWN4KSd4KWN4KSv4KS+4KSyCk5hbWVbbmxdPU5pZXV3IHZlbnN0ZXIKTmFtZVtubl9OT109Tnl0dCB2aW5kYXVnZQpOYW1lW29yXT3grKjgrYLgrKTgrKgg4K2x4Ky/4Kyj4K2N4Kyh4K2LCk5hbWVbcGFfSU5dPeCoqOCoteCpgOCogiDgqLXgqL/gqbDgqKHgqYsKTmFtZVtwbF09Tm93ZSBva25vCk5hbWVbcHRfQlJdPU5vdmEgamFuZWxhCk5hbWVbcHRfUFRdPU5vdmEgamFuZWxhCk5hbWVbcm1dPU5vdmEgZmFuZXN0cmEKTmFtZVtyb109RmVyZWFzdHLEgyBub3XEgwpOYW1lW3J1XT3QndC+0LLQvtC1INC+0LrQvdC+Ck5hbWVbc2F0XT3gpKjgpL7gpLXgpL4g4KS14KS/4KSC4KSh4KWLIChOKQpOYW1lW3NpXT3gtrHgt4Ag4Laa4LeA4LeU4LeF4LeU4LeA4Laa4LeKCk5hbWVbc2tdPU5vdsOpIG9rbm8KTmFtZVtzbF09Tm92byBva25vCk5hbWVbc29uXT1aYW5mdW4gdGFhZ2EKTmFtZVtzcV09RHJpdGFyZSBlIFJlCk5hbWVbc3JdPdCd0L7QstC4INC/0YDQvtC30L7RgApOYW1lW3N2X1NFXT1OeXR0IGbDtm5zdGVyCk5hbWVbdGFdPeCuquCvgeCupOCuv+CuryDgrprgrr7grrPgrrDgrq7gr40KTmFtZVt0ZV094LCV4LGK4LCk4LGN4LCkIOCwteCwv+CwguCwoeCxiwpOYW1lW3RoXT3guKvguJnguYnguLLguJXguYjguLLguIfguYPguKvguKHguYgKTmFtZVt0cl09WWVuaSBwZW5jZXJlCk5hbWVbdHN6XT1FcmFhdGFyYWt1YSBqaW1wYW5pCk5hbWVbdWtdPdCd0L7QstC1INCy0ZbQutC90L4KTmFtZVt1cl092YbbjNinINiv2LHbjNqG24EKTmFtZVt1el09WWFuZ2kgb3luYQpOYW1lW3ZpXT1D4butYSBz4buVIG3hu5tpCk5hbWVbd29dPVBhbGFudGVlciBidSBiZWVzCk5hbWVbeGhdPUlmZXN0aWxlIGVudHNoYQpOYW1lW3poX0NOXT3mlrDlu7rnqpflj6MKTmFtZVt6aF9UV1096ZaL5paw6KaW56qXCkV4ZWM9JSUlRVhUUkFDVF9ESVIlJSUvZmlyZWZveCAtLW5ldy13aW5kb3cgJXUKCltEZXNrdG9wIEFjdGlvbiBuZXctcHJpdmF0ZS13aW5kb3ddCk5hbWU9TmV3IFByaXZhdGUgV2luZG93Ck5hbWVbYWNoXT1EaXJpY2EgbWFueWVuIG1lIG11bmcKTmFtZVthZl09TnV3ZSBwcml2YWF0dmVuc3RlcgpOYW1lW2FuXT1OdWV2YSBmaW5lc3RyYSBwcml2YWRhCk5hbWVbYXJdPdmG2KfZgdiw2Kkg2K7Yp9i12Kkg2KzYr9mK2K/YqQpOYW1lW2FzXT3gpqjgpqTgp4Hgpqgg4Kas4KeN4Kav4KaV4KeN4Kak4Ka/4KaX4KakIOCmieCmh+CmqOCnjeCmoeCniwpOYW1lW2FzdF09VmVudGFuYSBwcml2YWRhIG51ZXZhCk5hbWVbYXpdPVllbmkgTcmZeGZpIFDJmW5jyZlyyZkKTmFtZVtiZV090J3QvtCy0LDQtSDQsNC60L3QviDQsNC00LDRgdCw0LHQu9C10L3QvdGPCk5hbWVbYmddPdCd0L7QsiDQv9GA0L7Qt9C+0YDQtdGGINC30LAg0L/QvtCy0LXRgNC40YLQtdC70L3QviDRgdGK0YDRhNC40YDQsNC90LUKTmFtZVtibl9CRF094Kao4Kak4KeB4KaoIOCmrOCnjeCmr+CmleCnjeCmpOCmv+Cml+CmpCDgpongpofgpqjgp43gpqHgp4sKTmFtZVtibl9JTl094Kao4Kak4KeB4KaoIOCmrOCnjeCmr+CmleCnjeCmpOCmv+Cml+CmpCDgpongpofgpqjgp43gpqHgp4sKTmFtZVticl09UHJlbmVzdHIgbWVyZGVpw7EgcHJldmV6IG5ldmV6Ck5hbWVbYnJ4XT3gpJfgpYvgpKbgpL7gpKgg4KSq4KWN4KSw4KS+4KSH4KSt4KWH4KSfIOCkieCkh+CkqOCljeCkoScKTmFtZVtic109Tm92aSBwcml2YXRuaSBwcm96b3IKTmFtZVtjYV09RmluZXN0cmEgcHJpdmFkYSBub3ZhCk5hbWVbY2FrXT1LJ2FrJ2EnIGljaGluYW4gdHp1d8OkY2gKTmFtZVtjc109Tm92w6kgYW5vbnltbsOtIG9rbm8KTmFtZVtjeV09RmZlbmVzdHIgQnJlaWZhdCBOZXd5ZGQKTmFtZVtkYV09Tnl0IHByaXZhdCB2aW5kdWUKTmFtZVtkZV09TmV1ZXMgcHJpdmF0ZXMgRmVuc3RlcgpOYW1lW2RzYl09Tm93ZSBwcml3YXRuZSB3b2tubwpOYW1lW2VsXT3Onc6tzr8gz4DOsc+BzqzOuM+Fz4HOvyDOuc60zrnPic+EzrnOus6uz4Igz4DOtc+BzrnOrs6zzrfPg863z4IKTmFtZVtlbl9HQl09TmV3IFByaXZhdGUgV2luZG93Ck5hbWVbZW5fVVNdPU5ldyBQcml2YXRlIFdpbmRvdwpOYW1lW2VuX1pBXT1OZXcgUHJpdmF0ZSBXaW5kb3cKTmFtZVtlb109Tm92YSBwcml2YXRhIGZlbmVzdHJvCk5hbWVbZXNfQVJdPU51ZXZhIHZlbnRhbmEgcHJpdmFkYQpOYW1lW2VzX0NMXT1OdWV2YSB2ZW50YW5hIHByaXZhZGEKTmFtZVtlc19FU109TnVldmEgdmVudGFuYSBwcml2YWRhCk5hbWVbZXNfTVhdPU51ZXZhIHZlbnRhbmEgcHJpdmFkYQpOYW1lW2V0XT1VdXMgcHJpdmFhdG5lIGFrZW4KTmFtZVtldV09TGVpaG8gcHJpYmF0dSBiZXJyaWEKTmFtZVtmYV092b7Zhtis2LHZhyDZhtin2LTZhtin2LMg2KzYr9uM2K8KTmFtZVtmZl09SGVub3JkZSBTdXR1cm8gSGVzZXJlCk5hbWVbZmldPVV1c2kgeWtzaXR5aW5lbiBpa2t1bmEKTmFtZVtmcl09Tm91dmVsbGUgZmVuw6p0cmUgZGUgbmF2aWdhdGlvbiBwcml2w6llCk5hbWVbZnlfTkxdPU5paiBwcml2ZWVmaW5zdGVyCk5hbWVbZ2FfSUVdPUZ1aW5uZW9nIE51YSBQaHLDrW9iaMOhaWRlYWNoCk5hbWVbZ2RdPVVpbm5lYWcgcGhyw6xvYmhhaWRlYWNoIMO5cgpOYW1lW2dsXT1Ob3ZhIHhhbmVsYSBwcml2YWRhCk5hbWVbZ25dPU92ZXTDoyDDsWVtaSBweWFodQpOYW1lW2d1X0lOXT3gqqjgqrXgq4Ag4KqW4Kq+4Kqo4KqX4KuAIOCqteCqv+CqqOCrjeCqoeCriwpOYW1lW2hlXT3Xl9ec15XXnyDXpNeo15jXmSDXl9eT16kKTmFtZVtoaV9JTl094KSo4KSv4KWAIOCkqOCkv+CknOClgCDgpLXgpL/gpILgpKHgpYsKTmFtZVtocl09Tm92aSBwcml2YXRuaSBwcm96b3IKTmFtZVtoc2JdPU5vd2UgcHJpd2F0bmUgd29rbm8KTmFtZVtodV09w5pqIHByaXbDoXQgYWJsYWsKTmFtZVtoeV9BTV091Y3Vr9W91aXVrCDUs9Wh1bLVv9W21asg1aTVq9W/1aHWgNWv1bjWgtW0Ck5hbWVbaWRdPUplbmRlbGEgTW9kZSBQcmliYWRpIEJhcnUKTmFtZVtpc109TsO9ciBodWxpw7BzZ2x1Z2dpCk5hbWVbaXRdPU51b3ZhIGZpbmVzdHJhIGFub25pbWEKTmFtZVtqYV095paw44GX44GE44OX44Op44Kk44OZ44O844OI44Km44Kj44Oz44OJ44KmCk5hbWVbamFfSlAtbWFjXT3mlrDopo/jg5fjg6njgqTjg5njg7zjg4jjgqbjgqTjg7Pjg4njgqYKTmFtZVtrYV094YOQ4YOu4YOQ4YOa4YOYIOGDnuGDmOGDoOGDkOGDk+GDmCDhg6Thg5Dhg5zhg6/hg5Dhg6Dhg5AKTmFtZVtra1090JbQsNKj0LAg0LbQtdC60LXQu9GW0Log0YLQtdGA0LXQt9C1Ck5hbWVba21dPeGelOGehOGfkuGeouGeveGeheGer+GegOGeh+Gek+GekOGfkuGemOGeuApOYW1lW2tuXT3gsrngs4rgsrgg4LKW4LK+4LK44LKX4LK/IOCyleCyv+Cyn+CyleCyvwpOYW1lW2tvXT3sg4gg7IKs7IOd7ZmcIOuztO2YuCDrqqjrk5wKTmFtZVtrb2tdPeCkqOCkteCliyDgpJbgpL7gpJzgpJfgpYAg4KS14KS/4KSC4KSh4KWLCk5hbWVba3NdPdmG2ZLZiCDZvtix2KfbjNmI2bkg2YjbjNmG2ojZiApOYW1lW2xpal09TsOqdXZvIGJhcmPDs24gcHJpdsOydQpOYW1lW2xvXT3gu4DgupvgurXgupTguqvgupngu4ngurLgupXgu4jgurLguofguqrguqfgupngupXgurvguqfguoLgurfgu4ngupnguqHgurLgu4PguqvguqHgu4gKTmFtZVtsdF09TmF1amFzIHByaXZhdGF1cyBuYXLFoXltbyBsYW5nYXMKTmFtZVtsdGddPUphdW5zIHByaXZhdGFpcyBsxatncwpOYW1lW2x2XT1KYXVucyBwcml2xIF0YWlzIGxvZ3MKTmFtZVttYWldPeCkqOCkr+CkviDgpKjgpL/gpJwg4KS14KS/4KSC4KSh4KWLIChXKQpOYW1lW21rXT3QndC+0LIg0L/RgNC40LLQsNGC0LXQvSDQv9GA0L7Qt9C+0YDQtdGGCk5hbWVbbWxdPeC0quC1geC0pOC0v+C0ryDgtLjgtY3gtLXgtJXgtL7gtLDgtY3gtK8g4LSc4LS+4LSy4LSV4LSCCk5hbWVbbXJdPeCkqOCkteClgOCkqCDgpLXgpYjgpK/gpJXgpY3gpKTgpL/gpJUg4KSq4KSf4KSyCk5hbWVbbXNdPVRldGluZ2thcCBQZXJzZW5kaXJpYW4gQmFoYXJ1Ck5hbWVbbXldPU5ldyBQcml2YXRlIFdpbmRvdwpOYW1lW25iX05PXT1OeXR0IHByaXZhdCB2aW5kdQpOYW1lW25lX05QXT3gpKjgpK/gpL7gpIEg4KSo4KS/4KSc4KWAIOCkuOCknuCljeCkneCljeCkr+CkvuCksgpOYW1lW25sXT1OaWV1dyBwcml2w6l2ZW5zdGVyCk5hbWVbbm5fTk9dPU55dHQgcHJpdmF0IHZpbmRhdWdlCk5hbWVbb3JdPeCsqOCtguCspOCsqCDgrKzgrY3grZ/grJXgrY3grKTgrL/grJfgrKQg4K2x4Ky/4Kyj4K2N4Kyh4K2LCk5hbWVbcGFfSU5dPeCoqOCoteCpgOCogiDgqKrgqY3gqLDgqL7gqIjgqLXgqYfgqJ8g4Ki14Ki/4Kmw4Kih4KmLCk5hbWVbcGxdPU5vd2Ugb2tubyBwcnl3YXRuZQpOYW1lW3B0X0JSXT1Ob3ZhIGphbmVsYSBwcml2YXRpdmEKTmFtZVtwdF9QVF09Tm92YSBqYW5lbGEgcHJpdmFkYQpOYW1lW3JtXT1Ob3ZhIGZhbmVzdHJhIHByaXZhdGEKTmFtZVtyb109RmVyZWFzdHLEgyBwcml2YXTEgyBub3XEgwpOYW1lW3J1XT3QndC+0LLQvtC1INC/0YDQuNCy0LDRgtC90L7QtSDQvtC60L3QvgpOYW1lW3NhdF094KSo4KS+4KS14KS+IOCkqOCkv+CknOClh+CksOCkvuCkleCljSDgpLXgpL/gpILgpKHgpYsgKFcgKQpOYW1lW3NpXT3gtrHgt4Ag4La04LeU4Lav4LeK4Lac4La94LeS4LaaIOC2muC3gOC3lOC3heC3lOC3gCAoVykKTmFtZVtza109Tm92w6kgb2tubyB2IHJlxb5pbWUgU8O6a3JvbW7DqSBwcmVobGlhZGFuaWUKTmFtZVtzbF09Tm92byB6YXNlYm5vIG9rbm8KTmFtZVtzb25dPVN1dHVyYSB6YW5mdW4gdGFhZ2EKTmFtZVtzcV09RHJpdGFyZSBlIFJlIFByaXZhdGUKTmFtZVtzcl090J3QvtCy0Lgg0L/RgNC40LLQsNGC0LDQvSDQv9GA0L7Qt9C+0YAKTmFtZVtzdl9TRV09Tnl0dCBwcml2YXQgZsO2bnN0ZXIKTmFtZVt0YV094K6q4K+B4K6k4K6/4K6vIOCupOCuqeCuv+CuquCvjeCuquCun+CvjeCunyDgrprgrr7grrPgrrDgrq7gr40KTmFtZVt0ZV094LCV4LGK4LCk4LGN4LCkIOCwhuCwguCwpOCwsOCwguCwl+Cwv+CwlSDgsLXgsL/gsILgsKHgsYsKTmFtZVt0aF094Lir4LiZ4LmJ4Liy4LiV4LmI4Liy4LiH4Liq4LmI4Lin4LiZ4LiV4Lix4Lin4LmD4Lir4Lih4LmICk5hbWVbdHJdPVllbmkgZ2l6bGkgcGVuY2VyZQpOYW1lW3Rzel09SnVjaGlpdGkgZXJhYXRhcmFrdWEgamltcGFuaQpOYW1lW3VrXT3Qn9GA0LjQstCw0YLQvdC1INCy0ZbQutC90L4KTmFtZVt1cl092YbbjNinINmG2KzbjCDYr9ix24zahtuBCk5hbWVbdXpdPVlhbmdpIG1heGZpeSBveW5hCk5hbWVbdmldPUPhu61hIHPhu5UgcmnDqm5nIHTGsCBt4bubaQpOYW1lW3dvXT1QYW5sYW50ZWVydSBiaWlyIGJ1IGJlZXMKTmFtZVt4aF09SWZlc3RpbGUgeWFuZ2FzZXNlIGVudHNoYQpOYW1lW3poX0NOXT3mlrDlu7rpmpDnp4HmtY/op4jnqpflj6MKTmFtZVt6aF9UV1095paw5aKe6Zqx56eB6KaW56qXCkV4ZWM9JSUlRVhUUkFDVF9ESVIlJSUvZmlyZWZveCAtLXByaXZhdGUtd2luZG93ICV1CgpbRGVza3RvcCBBY3Rpb24gcHJvZmlsZS1tYW5hZ2VyLXdpbmRvd10KTmFtZT1PcGVuIHRoZSBQcm9maWxlIE1hbmFnZXIKTmFtZVtjc109U3Byw6F2YSBwcm9maWzFrwpFeGVjPSUlJUVYVFJBQ1RfRElSJSUlL2ZpcmVmb3ggLS1Qcm9maWxlTWFuYWdlcgo="  # noqa
    )
    desktop_data = desktop_data.replace(
        b"%%%RELEASE_TYPE%%%", product_select.encode("utf-8")
    )
    desktop_data = desktop_data.replace(
        b"%%%EXTRACT_DIR%%%", extract_dir.encode("utf-8")
    )
    desktop_data = desktop_data.replace(b"%%%WM_CLASS%%%", wm_class.encode("utf-8"))
    applications_dir = path_join(get_xdg_data_home(), "applications")
    makedirs(applications_dir, exist_ok=True)
    # noinspection SpellCheckingInspection
    with open(
        expanduser(
            f"{applications_dir}/rany2_firefox_installer-firefox_{_release_type}_{platform_select}_{language_select}.desktop"  # noqa
        ),
        "w+b",
    ) as fp:
        fp.write(desktop_data)


def main() -> None:
    doc = parsed_download_page()

    product_select = get_product_selection(doc)
    platform_select = get_platform_selection(doc, product_select)
    language_select = get_language_selection(doc, product_select)
    current_href = get_current_href(
        doc, product_select, language_select, platform_select
    )
    # noinspection SpellCheckingInspection
    extract_dir = path_join(
        get_xdg_data_home(),
        "rany2_firefox_installer",
        f"firefox_{product_select[len('desktop_'):]}-{platform_select}-{language_select}",
    )
    makedirs(dirname(extract_dir), exist_ok=True)
    download_and_extract(current_href, extract_dir)

    print()
    print("Creating desktop file...")
    create_desktop(product_select, platform_select, language_select, extract_dir)
    print("Desktop file created.")


if __name__ == "__main__":
    main()
