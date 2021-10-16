#!/usr/bin/env python3

from base64 import b64decode
from os import makedirs, environ
from os.path import expanduser, dirname
from os.path import join as path_join
from shutil import copyfileobj, move, rmtree
from tarfile import open as topen
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
        print("Downloading and parsing the download page.")
        with urlopen("https://www.mozilla.org/en-US/firefox/all/") as resp:
            copyfileobj(resp, fp)
        _parse_ret = parse(fp.name)
        print("Download page was downloaded and parsed.")
        return _parse_ret


def prompt(prompt: str, array: Union[List[str], Tuple[str]]) -> str:
    print()
    print(prompt)
    for x, y in enumerate(array):
        print(f"  {x+1}: {y}")
    print()

    while True:
        user_input = input("Your number: ")
        try:
            user_input = int(user_input)
        except ValueError:
            continue

        if user_input > 0 and user_input < len(array) + 1:
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
            copyfileobj(resp, fp)
        print("Download complete.")
        print()

        print("Extracting...")
        temp_extract = mkdtemp()
        with topen(fp.name) as tar:
            tar.extractall(temp_extract)
        move(f"{temp_extract}/firefox", f"{extract_dir}")
        rmtree(f"{temp_extract}")
        print("Extract complete.")


def create_desktop(
    product_select: str,
    platform_select: str,
    language_select: str,
    extract_dir: str,
):
    _release_type = product_select
    if product_select == "desktop_release":
        product_select == ""
    elif product_select == "desktop_beta":
        product_select = " Beta"
    elif product_select == "desktop_developer":
        product_select = " Developer Edition"
    elif product_select == "desktop_nightly":
        product_select = " Nightly"
    elif product_select == "desktop_esr":
        product_select = " ESR"

    desktop_data = b64decode(
        b'W0Rlc2t0b3AgRW50cnldClZlcnNpb249MS4wCk5hbWU9RmlyZWZveCUlJVJFTEVBU0VfVFlQRSUlJQpHZW5lcmljTmFtZT1XZWIgQnJvd3NlcgpHZW5lcmljTmFtZVthcl092YXYqti12YHYrSDZiNmQ2KgKR2VuZXJpY05hbWVbYXN0XT1SZXN0b2xhZG9yIFdlYgpHZW5lcmljTmFtZVtibl094KaT4Kav4Ka84KeH4KasIOCmrOCnjeCmsOCmvuCmieCmnOCmvuCmsApHZW5lcmljTmFtZVtjYV09TmF2ZWdhZG9yIHdlYgpHZW5lcmljTmFtZVtjc109V2Vib3bDvSBwcm9obMOtxb5lxI0KR2VuZXJpY05hbWVbZGFdPVdlYmJyb3dzZXIKR2VuZXJpY05hbWVbZGVdPVdlYmJyb3dzZXIKR2VuZXJpY05hbWVbZWxdPc6gzrXPgc65zrfOs863z4TOrs+CIM60zrnOsc60zrnOus+Ez43Ov8+FCkdlbmVyaWNOYW1lW2VzXT1OYXZlZ2Fkb3Igd2ViCkdlbmVyaWNOYW1lW2V0XT1WZWViaWJyYXVzZXIKR2VuZXJpY05hbWVbZmFdPdmF2LHZiNix2q/YsSDYp9uM2YbYqtix2YbYqtuMCkdlbmVyaWNOYW1lW2ZpXT1XV1ctc2VsYWluCkdlbmVyaWNOYW1lW2ZyXT1OYXZpZ2F0ZXVyIFdlYgpHZW5lcmljTmFtZVtnbF09TmF2ZWdhZG9yIFdlYgpHZW5lcmljTmFtZVtoZV0915PXpNeT16TXnyDXkNeZ16DXmNeo16DXmApHZW5lcmljTmFtZVtocl09V2ViIHByZWdsZWRuaWsKR2VuZXJpY05hbWVbaHVdPVdlYmLDtm5nw6lzesWRCkdlbmVyaWNOYW1lW2l0XT1Ccm93c2VyIFdlYgpHZW5lcmljTmFtZVtqYV0944Km44Kn44OW44O744OW44Op44Km44K2CkdlbmVyaWNOYW1lW2tvXT3sm7kg67iM65287Jqw7KCACkdlbmVyaWNOYW1lW2t1XT1HZXJva2EgdG9yw6oKR2VuZXJpY05hbWVbbHRdPUludGVybmV0byBuYXLFoXlrbMSXCkdlbmVyaWNOYW1lW25iXT1OZXR0bGVzZXIKR2VuZXJpY05hbWVbbmxdPVdlYmJyb3dzZXIKR2VuZXJpY05hbWVbbm5dPU5ldHRsZXNhcgpHZW5lcmljTmFtZVtub109TmV0dGxlc2VyCkdlbmVyaWNOYW1lW3BsXT1QcnplZ2zEhWRhcmthIFdXVwpHZW5lcmljTmFtZVtwdF09TmF2ZWdhZG9yIFdlYgpHZW5lcmljTmFtZVtwdF9CUl09TmF2ZWdhZG9yIFdlYgpHZW5lcmljTmFtZVtyb109TmF2aWdhdG9yIEludGVybmV0CkdlbmVyaWNOYW1lW3J1XT3QktC10LEt0LHRgNCw0YPQt9C10YAKR2VuZXJpY05hbWVbc2tdPUludGVybmV0b3bDvSBwcmVobGlhZGHEjQpHZW5lcmljTmFtZVtzbF09U3BsZXRuaSBicnNrYWxuaWsKR2VuZXJpY05hbWVbc3ZdPVdlYmJsw6RzYXJlCkdlbmVyaWNOYW1lW3RyXT1XZWIgVGFyYXnEsWPEsQpHZW5lcmljTmFtZVt1Z1092KrZiNix2YPbhtix2q/biApHZW5lcmljTmFtZVt1a1090JLQtdCxLdCx0YDQsNGD0LfQtdGACkdlbmVyaWNOYW1lW3ZpXT1UcsOsbmggZHV54buHdCBXZWIKR2VuZXJpY05hbWVbemhfQ05dPee9kee7nOa1j+iniOWZqApHZW5lcmljTmFtZVt6aF9UV10957ay6Lev54CP6Ka95ZmoCkNvbW1lbnQ9QnJvd3NlIHRoZSBXZWIKQ29tbWVudFthcl092KrYtdmB2K0g2KfZhNmI2ZDYqApDb21tZW50W2FzdF09UmVzdG9sYSBwZWxhIFJlZGUKQ29tbWVudFtibl094KaH4Kao4KeN4Kaf4Ka+4Kaw4Kao4KeH4KafIOCmrOCnjeCmsOCmvuCmieCmnCDgppXgprDgp4HgpqgKQ29tbWVudFtjYV09TmF2ZWd1ZXUgcGVyIGVsIHdlYgpDb21tZW50W2NzXT1Qcm9obMOtxb5lbsOtIHN0csOhbmVrIFdvcmxkIFdpZGUgV2VidQpDb21tZW50W2RhXT1TdXJmIHDDpSBpbnRlcm5ldHRldApDb21tZW50W2RlXT1JbSBJbnRlcm5ldCBzdXJmZW4KQ29tbWVudFtlbF09zpzPgM6/z4HOtc6vz4TOtSDOvc6xIM+AzrXPgc65zrfOs863zrjOtc6vz4TOtSDPg8+Ezr8gzrTOuc6xzrTOr866z4TPhc6/IChXZWIpCkNvbW1lbnRbZXNdPU5hdmVndWUgcG9yIGxhIHdlYgpDb21tZW50W2V0XT1MZWhpdHNlIHZlZWJpCkNvbW1lbnRbZmFdPdi12YHYrdin2Kog2LTYqNqp2Ycg2KzZh9in2YbbjCDYp9uM2YbYqtix2YbYqiDYsdinINmF2LHZiNixINmG2YXYp9uM24zYrwpDb21tZW50W2ZpXT1TZWxhYSBJbnRlcm5ldGluIFdXVy1zaXZ1amEKQ29tbWVudFtmcl09TmF2aWd1ZXIgc3VyIGxlIFdlYgpDb21tZW50W2dsXT1OYXZlZ2FyIHBvbGEgcmVkZQpDb21tZW50W2hlXT3Xktec15nXqdeUINeR16jXl9eR15kg15TXkNeZ16DXmNeo16DXmApDb21tZW50W2hyXT1QcmV0cmHFvml0ZSB3ZWIKQ29tbWVudFtodV09QSB2aWzDoWdow6Fsw7MgYsO2bmfDqXN6w6lzZQpDb21tZW50W2l0XT1Fc3Bsb3JhIGlsIHdlYgpDb21tZW50W2phXT3jgqbjgqfjg5bjgpLplrLopqfjgZfjgb7jgZkKQ29tbWVudFtrb1097Ju57J2EIOuPjOyVhCDri6Tri5nri4jri6QKQ29tbWVudFtrdV09TGkgdG9yw6ogYmlnZXJlCkNvbW1lbnRbbHRdPU5hcsWheWtpdGUgaW50ZXJuZXRlCkNvbW1lbnRbbmJdPVN1cmYgcMOlIG5ldHRldApDb21tZW50W25sXT1WZXJrZW4gaGV0IGludGVybmV0CkNvbW1lbnRbbm5dPVN1cmYgcMOlIG5ldHRldApDb21tZW50W25vXT1TdXJmIHDDpSBuZXR0ZXQKQ29tbWVudFtwbF09UHJ6ZWdsxIVkYW5pZSBzdHJvbiBXV1cKQ29tbWVudFtwdF09TmF2ZWd1ZSBuYSBJbnRlcm5ldApDb21tZW50W3B0X0JSXT1OYXZlZ3VlIG5hIEludGVybmV0CkNvbW1lbnRbcm9dPU5hdmlnYcibaSBwZSBJbnRlcm5ldApDb21tZW50W3J1XT3QlNC+0YHRgtGD0L8g0LIg0JjQvdGC0LXRgNC90LXRggpDb21tZW50W3NrXT1QcmVobGlhZGFuaWUgaW50ZXJuZXR1CkNvbW1lbnRbc2xdPUJyc2thanRlIHBvIHNwbGV0dQpDb21tZW50W3N2XT1TdXJmYSBww6Ugd2ViYmVuCkNvbW1lbnRbdHJdPcSwbnRlcm5ldCd0ZSBHZXppbmluCkNvbW1lbnRbdWddPdiv24fZhtmK2KfYr9mJ2YPZiSDYqtmI2LHYqNuV2KrZhNuV2LHZhtmJINmD24bYsdqv2YnZhNmJINio2YjZhNmJ2K/bhwpDb21tZW50W3VrXT3Qn9C10YDQtdCz0LvRj9C0INGB0YLQvtGA0ZbQvdC+0Log0IbQvdGC0LXRgNC90LXRgtGDCkNvbW1lbnRbdmldPcSQ4buDIGR1eeG7h3QgY8OhYyB0cmFuZyB3ZWIKQ29tbWVudFt6aF9DTl095rWP6KeI5LqS6IGU572RCkNvbW1lbnRbemhfVFddPeeAj+imvee2sumam+e2sui3rwpFeGVjPSUlJUVYVFJBQ1RfRElSJSUlL2ZpcmVmb3ggJXUKSWNvbj0lJSVFWFRSQUNUX0RJUiUlJS9icm93c2VyL2Nocm9tZS9pY29ucy9kZWZhdWx0L2RlZmF1bHQxMjgucG5nClRlcm1pbmFsPWZhbHNlClR5cGU9QXBwbGljYXRpb24KTWltZVR5cGU9dGV4dC9odG1sO3RleHQveG1sO2FwcGxpY2F0aW9uL3hodG1sK3htbDthcHBsaWNhdGlvbi92bmQubW96aWxsYS54dWwreG1sO3RleHQvbW1sO3gtc2NoZW1lLWhhbmRsZXIvaHR0cDt4LXNjaGVtZS1oYW5kbGVyL2h0dHBzOwpTdGFydHVwTm90aWZ5PXRydWUKU3RhcnR1cFdNQ2xhc3M9RmlyZWZveCUlJVJFTEVBU0VfVFlQRSUlJQpDYXRlZ29yaWVzPU5ldHdvcms7V2ViQnJvd3NlcjsKS2V5d29yZHM9d2ViO2Jyb3dzZXI7aW50ZXJuZXQ7CkFjdGlvbnM9bmV3LXdpbmRvdztuZXctcHJpdmF0ZS13aW5kb3c7cHJvZmlsZS1tYW5hZ2VyLXdpbmRvdzsKCltEZXNrdG9wIEFjdGlvbiBuZXctd2luZG93XQpOYW1lPU5ldyBXaW5kb3cKTmFtZVthY2hdPURpcmljYSBtYW55ZW4KTmFtZVthZl09TnV3ZSB2ZW5zdGVyCk5hbWVbYW5dPU51ZXZhIGZpbmVzdHJhCk5hbWVbYXJdPdmG2KfZgdiw2Kkg2KzYr9mK2K/YqQpOYW1lW2FzXT3gpqjgpqTgp4Hgpqgg4KaJ4KaH4Kao4KeN4Kah4KeLCk5hbWVbYXN0XT1WZW50YW5hIG51ZXZhCk5hbWVbYXpdPVllbmkgUMmZbmPJmXLJmQpOYW1lW2JlXT3QndC+0LLQsNC1INCw0LrQvdC+Ck5hbWVbYmddPdCd0L7QsiDQv9GA0L7Qt9C+0YDQtdGGCk5hbWVbYm5fQkRdPeCmqOCmpOCngeCmqCDgpongpofgpqjgp43gpqHgp4sgKE4pCk5hbWVbYm5fSU5dPeCmqOCmpOCngeCmqCDgpongpofgpqjgp43gpqHgp4sKTmFtZVticl09UHJlbmVzdHIgbmV2ZXoKTmFtZVticnhdPeCkl+Cli+CkpuCkvuCkqCDgpIngpIfgpKjgpY3gpKEnKE4pCk5hbWVbYnNdPU5vdmkgcHJvem9yCk5hbWVbY2FdPUZpbmVzdHJhIG5vdmEKTmFtZVtjYWtdPUsnYWsnYScgdHp1d8OkY2gKTmFtZVtjc109Tm92w6kgb2tubwpOYW1lW2N5XT1GZmVuZXN0ciBOZXd5ZGQKTmFtZVtkYV09Tnl0IHZpbmR1ZQpOYW1lW2RlXT1OZXVlcyBGZW5zdGVyCk5hbWVbZHNiXT1Ob3dlIHdva25vCk5hbWVbZWxdPc6dzq3OvyDPgM6xz4HOrM64z4XPgc6/Ck5hbWVbZW5fR0JdPU5ldyBXaW5kb3cKTmFtZVtlbl9VU109TmV3IFdpbmRvdwpOYW1lW2VuX1pBXT1OZXcgV2luZG93Ck5hbWVbZW9dPU5vdmEgZmVuZXN0cm8KTmFtZVtlc19BUl09TnVldmEgdmVudGFuYQpOYW1lW2VzX0NMXT1OdWV2YSB2ZW50YW5hCk5hbWVbZXNfRVNdPU51ZXZhIHZlbnRhbmEKTmFtZVtlc19NWF09TnVldmEgdmVudGFuYQpOYW1lW2V0XT1VdXMgYWtlbgpOYW1lW2V1XT1MZWlobyBiZXJyaWEKTmFtZVtmYV092b7Zhtis2LHZhyDYrNiv24zYrwpOYW1lW2ZmXT1IZW5vcmRlIEhlc2VyZQpOYW1lW2ZpXT1VdXNpIGlra3VuYQpOYW1lW2ZyXT1Ob3V2ZWxsZSBmZW7DqnRyZQpOYW1lW2Z5X05MXT1OaWogZmluc3RlcgpOYW1lW2dhX0lFXT1GdWlubmVvZyBOdWEKTmFtZVtnZF09VWlubmVhZyDDuXIKTmFtZVtnbF09Tm92YSB4YW5lbGEKTmFtZVtnbl09T3ZldMOjIHB5YWh1Ck5hbWVbZ3VfSU5dPeCqqOCqteCrgCDgqrXgqr/gqqjgq43gqqHgq4sKTmFtZVtoZV0915fXnNeV158g15fXk9epCk5hbWVbaGlfSU5dPeCkqOCkr+CkviDgpLXgpL/gpILgpKHgpYsKTmFtZVtocl09Tm92aSBwcm96b3IKTmFtZVtoc2JdPU5vd2Ugd29rbm8KTmFtZVtodV09w5pqIGFibGFrCk5hbWVbaHlfQU1dPdWG1bjWgCDVitWh1b/VuNaC1bDVodW2Ck5hbWVbaWRdPUplbmRlbGEgQmFydQpOYW1lW2lzXT1Ow71yIGdsdWdnaQpOYW1lW2l0XT1OdW92YSBmaW5lc3RyYQpOYW1lW2phXT3mlrDjgZfjgYTjgqbjgqPjg7Pjg4njgqYKTmFtZVtqYV9KUC1tYWNdPeaWsOimj+OCpuOCpOODs+ODieOCpgpOYW1lW2thXT3hg5Dhg67hg5Dhg5rhg5gg4YOk4YOQ4YOc4YOv4YOQ4YOg4YOQCk5hbWVba2tdPdCW0LDSo9CwINGC0LXRgNC10LfQtQpOYW1lW2ttXT3hnpThnoThn5LhnqLhnr3hnoXhnpDhn5LhnpjhnrgKTmFtZVtrbl094LK54LOK4LK4IOCyleCyv+Cyn+CyleCyvwpOYW1lW2tvXT3sg4gg7LC9Ck5hbWVba29rXT3gpKjgpLXgpYfgpIIg4KSc4KSo4KWH4KSyCk5hbWVba3NdPdmG2KbYpiDZiNmQ2YbaiNmICk5hbWVbbGlqXT1OZXV2byBiYXJjb24KTmFtZVtsb1094Lqr4LqZ4LuJ4Lqy4LqV4LuI4Lqy4LqH4LuD4Lqr4Lqh4LuICk5hbWVbbHRdPU5hdWphcyBsYW5nYXMKTmFtZVtsdGddPUphdW5zIGzFq2dzCk5hbWVbbHZdPUphdW5zIGxvZ3MKTmFtZVttYWldPeCkqOCktSDgpLXgpL/gpILgpKHgpYsKTmFtZVtta1090J3QvtCyINC/0YDQvtC30L7RgNC10YYKTmFtZVttbF094LSq4LWB4LSk4LS/4LSvIOC0nOC0vuC0suC0leC0ggpOYW1lW21yXT3gpKjgpLXgpYDgpKgg4KSq4KSf4KSyCk5hbWVbbXNdPVRldGluZ2thcCBCYXJ1Ck5hbWVbbXldPeGAneGAhOGAuuGAuOGAkuGAreGAr+GAuOGAoeGAnuGAheGAugpOYW1lW25iX05PXT1OeXR0IHZpbmR1Ck5hbWVbbmVfTlBdPeCkqOCkr+CkvuCkgSDgpLjgpJ7gpY3gpJ3gpY3gpK/gpL7gpLIKTmFtZVtubF09TmlldXcgdmVuc3RlcgpOYW1lW25uX05PXT1OeXR0IHZpbmRhdWdlCk5hbWVbb3JdPeCsqOCtguCspOCsqCDgrbHgrL/grKPgrY3grKHgrYsKTmFtZVtwYV9JTl094Kio4Ki14KmA4KiCIOCoteCov+CpsOCooeCpiwpOYW1lW3BsXT1Ob3dlIG9rbm8KTmFtZVtwdF9CUl09Tm92YSBqYW5lbGEKTmFtZVtwdF9QVF09Tm92YSBqYW5lbGEKTmFtZVtybV09Tm92YSBmYW5lc3RyYQpOYW1lW3JvXT1GZXJlYXN0csSDIG5vdcSDCk5hbWVbcnVdPdCd0L7QstC+0LUg0L7QutC90L4KTmFtZVtzYXRdPeCkqOCkvuCkteCkviDgpLXgpL/gpILgpKHgpYsgKE4pCk5hbWVbc2ldPeC2seC3gCDgtprgt4Dgt5Tgt4Xgt5Tgt4Dgtprgt4oKTmFtZVtza109Tm92w6kgb2tubwpOYW1lW3NsXT1Ob3ZvIG9rbm8KTmFtZVtzb25dPVphbmZ1biB0YWFnYQpOYW1lW3NxXT1Ecml0YXJlIGUgUmUKTmFtZVtzcl090J3QvtCy0Lgg0L/RgNC+0LfQvtGACk5hbWVbc3ZfU0VdPU55dHQgZsO2bnN0ZXIKTmFtZVt0YV094K6q4K+B4K6k4K6/4K6vIOCumuCuvuCus+CusOCuruCvjQpOYW1lW3RlXT3gsJXgsYrgsKTgsY3gsKQg4LC14LC/4LCC4LCh4LGLCk5hbWVbdGhdPeC4q+C4meC5ieC4suC4leC5iOC4suC4h+C5g+C4q+C4oeC5iApOYW1lW3RyXT1ZZW5pIHBlbmNlcmUKTmFtZVt0c3pdPUVyYWF0YXJha3VhIGppbXBhbmkKTmFtZVt1a1090J3QvtCy0LUg0LLRltC60L3QvgpOYW1lW3VyXT3ZhtuM2Kcg2K/YsduM2obbgQpOYW1lW3V6XT1ZYW5naSBveW5hCk5hbWVbdmldPUPhu61hIHPhu5UgbeG7m2kKTmFtZVt3b109UGFsYW50ZWVyIGJ1IGJlZXMKTmFtZVt4aF09SWZlc3RpbGUgZW50c2hhCk5hbWVbemhfQ05dPeaWsOW7uueql+WPowpOYW1lW3poX1RXXT3plovmlrDoppbnqpcKRXhlYz0lJSVFWFRSQUNUX0RJUiUlJS9maXJlZm94IC0tbmV3LXdpbmRvdyAldQoKW0Rlc2t0b3AgQWN0aW9uIG5ldy1wcml2YXRlLXdpbmRvd10KTmFtZT1OZXcgUHJpdmF0ZSBXaW5kb3cKTmFtZVthY2hdPURpcmljYSBtYW55ZW4gbWUgbXVuZwpOYW1lW2FmXT1OdXdlIHByaXZhYXR2ZW5zdGVyCk5hbWVbYW5dPU51ZXZhIGZpbmVzdHJhIHByaXZhZGEKTmFtZVthcl092YbYp9mB2LDYqSDYrtin2LXYqSDYrNiv2YrYr9ipCk5hbWVbYXNdPeCmqOCmpOCngeCmqCDgpqzgp43gpq/gppXgp43gpqTgpr/gppfgpqQg4KaJ4KaH4Kao4KeN4Kah4KeLCk5hbWVbYXN0XT1WZW50YW5hIHByaXZhZGEgbnVldmEKTmFtZVthel09WWVuaSBNyZl4ZmkgUMmZbmPJmXLJmQpOYW1lW2JlXT3QndC+0LLQsNC1INCw0LrQvdC+INCw0LTQsNGB0LDQsdC70LXQvdC90Y8KTmFtZVtiZ1090J3QvtCyINC/0YDQvtC30L7RgNC10YYg0LfQsCDQv9C+0LLQtdGA0LjRgtC10LvQvdC+INGB0YrRgNGE0LjRgNCw0L3QtQpOYW1lW2JuX0JEXT3gpqjgpqTgp4Hgpqgg4Kas4KeN4Kav4KaV4KeN4Kak4Ka/4KaX4KakIOCmieCmh+CmqOCnjeCmoeCniwpOYW1lW2JuX0lOXT3gpqjgpqTgp4Hgpqgg4Kas4KeN4Kav4KaV4KeN4Kak4Ka/4KaX4KakIOCmieCmh+CmqOCnjeCmoeCniwpOYW1lW2JyXT1QcmVuZXN0ciBtZXJkZWnDsSBwcmV2ZXogbmV2ZXoKTmFtZVticnhdPeCkl+Cli+CkpuCkvuCkqCDgpKrgpY3gpLDgpL7gpIfgpK3gpYfgpJ8g4KSJ4KSH4KSo4KWN4KShJwpOYW1lW2JzXT1Ob3ZpIHByaXZhdG5pIHByb3pvcgpOYW1lW2NhXT1GaW5lc3RyYSBwcml2YWRhIG5vdmEKTmFtZVtjYWtdPUsnYWsnYScgaWNoaW5hbiB0enV3w6RjaApOYW1lW2NzXT1Ob3bDqSBhbm9ueW1uw60gb2tubwpOYW1lW2N5XT1GZmVuZXN0ciBCcmVpZmF0IE5ld3lkZApOYW1lW2RhXT1OeXQgcHJpdmF0IHZpbmR1ZQpOYW1lW2RlXT1OZXVlcyBwcml2YXRlcyBGZW5zdGVyCk5hbWVbZHNiXT1Ob3dlIHByaXdhdG5lIHdva25vCk5hbWVbZWxdPc6dzq3OvyDPgM6xz4HOrM64z4XPgc6/IM65zrTOuc+Jz4TOuc66zq7PgiDPgM61z4HOuc6uzrPOt8+DzrfPggpOYW1lW2VuX0dCXT1OZXcgUHJpdmF0ZSBXaW5kb3cKTmFtZVtlbl9VU109TmV3IFByaXZhdGUgV2luZG93Ck5hbWVbZW5fWkFdPU5ldyBQcml2YXRlIFdpbmRvdwpOYW1lW2VvXT1Ob3ZhIHByaXZhdGEgZmVuZXN0cm8KTmFtZVtlc19BUl09TnVldmEgdmVudGFuYSBwcml2YWRhCk5hbWVbZXNfQ0xdPU51ZXZhIHZlbnRhbmEgcHJpdmFkYQpOYW1lW2VzX0VTXT1OdWV2YSB2ZW50YW5hIHByaXZhZGEKTmFtZVtlc19NWF09TnVldmEgdmVudGFuYSBwcml2YWRhCk5hbWVbZXRdPVV1cyBwcml2YWF0bmUgYWtlbgpOYW1lW2V1XT1MZWlobyBwcmliYXR1IGJlcnJpYQpOYW1lW2ZhXT3ZvtmG2KzYsdmHINmG2KfYtNmG2KfYsyDYrNiv24zYrwpOYW1lW2ZmXT1IZW5vcmRlIFN1dHVybyBIZXNlcmUKTmFtZVtmaV09VXVzaSB5a3NpdHlpbmVuIGlra3VuYQpOYW1lW2ZyXT1Ob3V2ZWxsZSBmZW7DqnRyZSBkZSBuYXZpZ2F0aW9uIHByaXbDqWUKTmFtZVtmeV9OTF09TmlqIHByaXZlZWZpbnN0ZXIKTmFtZVtnYV9JRV09RnVpbm5lb2cgTnVhIFBocsOtb2Jow6FpZGVhY2gKTmFtZVtnZF09VWlubmVhZyBwaHLDrG9iaGFpZGVhY2ggw7lyCk5hbWVbZ2xdPU5vdmEgeGFuZWxhIHByaXZhZGEKTmFtZVtnbl09T3ZldMOjIMOxZW1pIHB5YWh1Ck5hbWVbZ3VfSU5dPeCqqOCqteCrgCDgqpbgqr7gqqjgqpfgq4Ag4Kq14Kq/4Kqo4KuN4Kqh4KuLCk5hbWVbaGVdPdeX15zXldefINek16jXmNeZINeX15PXqQpOYW1lW2hpX0lOXT3gpKjgpK/gpYAg4KSo4KS/4KSc4KWAIOCkteCkv+CkguCkoeCliwpOYW1lW2hyXT1Ob3ZpIHByaXZhdG5pIHByb3pvcgpOYW1lW2hzYl09Tm93ZSBwcml3YXRuZSB3b2tubwpOYW1lW2h1XT3DmmogcHJpdsOhdCBhYmxhawpOYW1lW2h5X0FNXT3VjdWv1b3VpdWsINSz1aHVstW/1bbVqyDVpNWr1b/VodaA1a/VuNaC1bQKTmFtZVtpZF09SmVuZGVsYSBNb2RlIFByaWJhZGkgQmFydQpOYW1lW2lzXT1Ow71yIGh1bGnDsHNnbHVnZ2kKTmFtZVtpdF09TnVvdmEgZmluZXN0cmEgYW5vbmltYQpOYW1lW2phXT3mlrDjgZfjgYTjg5fjg6njgqTjg5njg7zjg4jjgqbjgqPjg7Pjg4njgqYKTmFtZVtqYV9KUC1tYWNdPeaWsOimj+ODl+ODqeOCpOODmeODvOODiOOCpuOCpOODs+ODieOCpgpOYW1lW2thXT3hg5Dhg67hg5Dhg5rhg5gg4YOe4YOY4YOg4YOQ4YOT4YOYIOGDpOGDkOGDnOGDr+GDkOGDoOGDkApOYW1lW2trXT3QltCw0qPQsCDQttC10LrQtdC70ZbQuiDRgtC10YDQtdC30LUKTmFtZVtrbV094Z6U4Z6E4Z+S4Z6i4Z694Z6F4Z6v4Z6A4Z6H4Z6T4Z6Q4Z+S4Z6Y4Z64Ck5hbWVba25dPeCyueCziuCyuCDgspbgsr7gsrjgspfgsr8g4LKV4LK/4LKf4LKV4LK/Ck5hbWVba29dPeyDiCDsgqzsg53tmZwg67O07Zi4IOuqqOuTnApOYW1lW2tva1094KSo4KS14KWLIOCkluCkvuCknOCkl+ClgCDgpLXgpL/gpILgpKHgpYsKTmFtZVtrc1092YbZktmIINm+2LHYp9uM2YjZuSDZiNuM2YbaiNmICk5hbWVbbGlqXT1Ow6p1dm8gYmFyY8OzbiBwcml2w7J1Ck5hbWVbbG9dPeC7gOC6m+C6teC6lOC6q+C6meC7ieC6suC6leC7iOC6suC6h+C6quC6p+C6meC6leC6u+C6p+C6guC6t+C7ieC6meC6oeC6suC7g+C6q+C6oeC7iApOYW1lW2x0XT1OYXVqYXMgcHJpdmF0YXVzIG5hcsWheW1vIGxhbmdhcwpOYW1lW2x0Z109SmF1bnMgcHJpdmF0YWlzIGzFq2dzCk5hbWVbbHZdPUphdW5zIHByaXbEgXRhaXMgbG9ncwpOYW1lW21haV094KSo4KSv4KS+IOCkqOCkv+CknCDgpLXgpL/gpILgpKHgpYsgKFcpCk5hbWVbbWtdPdCd0L7QsiDQv9GA0LjQstCw0YLQtdC9INC/0YDQvtC30L7RgNC10YYKTmFtZVttbF094LSq4LWB4LSk4LS/4LSvIOC0uOC1jeC0teC0leC0vuC0sOC1jeC0ryDgtJzgtL7gtLLgtJXgtIIKTmFtZVttcl094KSo4KS14KWA4KSoIOCkteCliOCkr+CkleCljeCkpOCkv+CklSDgpKrgpJ/gpLIKTmFtZVttc109VGV0aW5na2FwIFBlcnNlbmRpcmlhbiBCYWhhcnUKTmFtZVtteV09TmV3IFByaXZhdGUgV2luZG93Ck5hbWVbbmJfTk9dPU55dHQgcHJpdmF0IHZpbmR1Ck5hbWVbbmVfTlBdPeCkqOCkr+CkvuCkgSDgpKjgpL/gpJzgpYAg4KS44KSe4KWN4KSd4KWN4KSv4KS+4KSyCk5hbWVbbmxdPU5pZXV3IHByaXbDqXZlbnN0ZXIKTmFtZVtubl9OT109Tnl0dCBwcml2YXQgdmluZGF1Z2UKTmFtZVtvcl094Kyo4K2C4Kyk4KyoIOCsrOCtjeCtn+CsleCtjeCspOCsv+Csl+CspCDgrbHgrL/grKPgrY3grKHgrYsKTmFtZVtwYV9JTl094Kio4Ki14KmA4KiCIOCoquCpjeCosOCovuCoiOCoteCph+ConyDgqLXgqL/gqbDgqKHgqYsKTmFtZVtwbF09Tm93ZSBva25vIHByeXdhdG5lCk5hbWVbcHRfQlJdPU5vdmEgamFuZWxhIHByaXZhdGl2YQpOYW1lW3B0X1BUXT1Ob3ZhIGphbmVsYSBwcml2YWRhCk5hbWVbcm1dPU5vdmEgZmFuZXN0cmEgcHJpdmF0YQpOYW1lW3JvXT1GZXJlYXN0csSDIHByaXZhdMSDIG5vdcSDCk5hbWVbcnVdPdCd0L7QstC+0LUg0L/RgNC40LLQsNGC0L3QvtC1INC+0LrQvdC+Ck5hbWVbc2F0XT3gpKjgpL7gpLXgpL4g4KSo4KS/4KSc4KWH4KSw4KS+4KSV4KWNIOCkteCkv+CkguCkoeCliyAoVyApCk5hbWVbc2ldPeC2seC3gCDgtrTgt5Tgtq/gt4rgtpzgtr3gt5Lgtpog4Laa4LeA4LeU4LeF4LeU4LeAIChXKQpOYW1lW3NrXT1Ob3bDqSBva25vIHYgcmXFvmltZSBTw7prcm9tbsOpIHByZWhsaWFkYW5pZQpOYW1lW3NsXT1Ob3ZvIHphc2Vibm8gb2tubwpOYW1lW3Nvbl09U3V0dXJhIHphbmZ1biB0YWFnYQpOYW1lW3NxXT1Ecml0YXJlIGUgUmUgUHJpdmF0ZQpOYW1lW3NyXT3QndC+0LLQuCDQv9GA0LjQstCw0YLQsNC9INC/0YDQvtC30L7RgApOYW1lW3N2X1NFXT1OeXR0IHByaXZhdCBmw7Zuc3RlcgpOYW1lW3RhXT3grqrgr4HgrqTgrr/grq8g4K6k4K6p4K6/4K6q4K+N4K6q4K6f4K+N4K6fIOCumuCuvuCus+CusOCuruCvjQpOYW1lW3RlXT3gsJXgsYrgsKTgsY3gsKQg4LCG4LCC4LCk4LCw4LCC4LCX4LC/4LCVIOCwteCwv+CwguCwoeCxiwpOYW1lW3RoXT3guKvguJnguYnguLLguJXguYjguLLguIfguKrguYjguKfguJnguJXguLHguKfguYPguKvguKHguYgKTmFtZVt0cl09WWVuaSBnaXpsaSBwZW5jZXJlCk5hbWVbdHN6XT1KdWNoaWl0aSBlcmFhdGFyYWt1YSBqaW1wYW5pCk5hbWVbdWtdPdCf0YDQuNCy0LDRgtC90LUg0LLRltC60L3QvgpOYW1lW3VyXT3ZhtuM2Kcg2YbYrNuMINiv2LHbjNqG24EKTmFtZVt1el09WWFuZ2kgbWF4Zml5IG95bmEKTmFtZVt2aV09Q+G7rWEgc+G7lSByacOqbmcgdMawIG3hu5tpCk5hbWVbd29dPVBhbmxhbnRlZXJ1IGJpaXIgYnUgYmVlcwpOYW1lW3hoXT1JZmVzdGlsZSB5YW5nYXNlc2UgZW50c2hhCk5hbWVbemhfQ05dPeaWsOW7uumakOengea1j+iniOeql+WPowpOYW1lW3poX1RXXT3mlrDlop7pmrHnp4HoppbnqpcKRXhlYz0lJSVFWFRSQUNUX0RJUiUlJS9maXJlZm94IC0tcHJpdmF0ZS13aW5kb3cgJXUKCltEZXNrdG9wIEFjdGlvbiBwcm9maWxlLW1hbmFnZXItd2luZG93XQpOYW1lPU9wZW4gdGhlIFByb2ZpbGUgTWFuYWdlcgpOYW1lW2NzXT1TcHLDoXZhIHByb2ZpbMWvCkV4ZWM9JSUlRVhUUkFDVF9ESVIlJSUvZmlyZWZveCAtLVByb2ZpbGVNYW5hZ2VyCg=='
    )
    desktop_data = desktop_data.replace(
        b"%%%RELEASE_TYPE%%%", product_select.encode("utf-8")
    )
    desktop_data = desktop_data.replace(
        b"%%%EXTRACT_DIR%%%", extract_dir.encode("utf-8")
    )
    applications_dir = path_join(get_xdg_data_home(), "applications")
    makedirs(applications_dir, exist_ok=True)
    with open(
        expanduser(
            f"{applications_dir}/rany2_firefox_installer-firefox_{_release_type}_{platform_select}_{language_select}.desktop"
        ),
        "w+b",
    ) as fp:
        fp.write(desktop_data)


def main():
    doc = parsed_download_page()

    product_select = get_product_selection(doc)
    platform_select = get_platform_selection(doc, product_select)
    language_select = get_language_selection(doc, product_select)
    current_href = get_current_href(
        doc, product_select, language_select, platform_select
    )
    extract_dir = path_join(
        get_xdg_data_home(),
        "rany2_firefox_installer",
        f"firefox_{product_select[len('desktop_'):]}-{platform_select}-{language_select}",
    )
    makedirs(dirname(extract_dir), exist_ok=True)
    download_and_extract(current_href, extract_dir)

    print()
    print("Creating desktop file.")
    create_desktop(product_select, platform_select, language_select, extract_dir)
    print("Desktop file created.")


if __name__ == "__main__":
    main()
