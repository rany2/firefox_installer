#!/usr/bin/env python3

from base64 import b64decode
from os.path import expanduser
from shutil import copyfileobj, move, rmtree
from tarfile import open as topen
from tempfile import NamedTemporaryFile, mkdtemp
from typing import Any, List, Tuple, Union
from urllib.request import urlopen

from lxml.html import parse


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


def create_desktop(release_type: str, extract_dir: str):
    _release_type = release_type
    if release_type == "desktop_release":
        release_type == ""
    elif release_type == "desktop_beta":
        release_type = " Beta"
    elif release_type == "desktop_developer":
        release_type = " Developer Edition"
    elif release_type == "desktop_nightly":
        release_type = " Nightly"
    elif release_type == "desktop_esr":
        release_type = " ESR"

    desktop_data = b64decode(
        b"CltEZXNrdG9wIEVudHJ5XQpOYW1lPUZpcmVmb3glJSVSRUxFQVNFX1RZUEUlJSUKR2VuZXJpY05hbWU9V2ViIEJyb3dzZXIKR2VuZXJpY05hbWVbYXJdPdmF2KrYtdmB2K0g2YjZkNioCkdlbmVyaWNOYW1lW2FzdF09UmVzdG9sYWRvciBXZWIKR2VuZXJpY05hbWVbYm5dPeCmk+Cmr+CmvOCnh+CmrCDgpqzgp43gprDgpr7gpongppzgpr7gprAKR2VuZXJpY05hbWVbY2FdPU5hdmVnYWRvciB3ZWIKR2VuZXJpY05hbWVbY3NdPVdlYm92w70gcHJvaGzDrcW+ZcSNCkdlbmVyaWNOYW1lW2RhXT1XZWJicm93c2VyCkdlbmVyaWNOYW1lW2RlXT1XZWJicm93c2VyCkdlbmVyaWNOYW1lW2VsXT3OoM61z4HOuc63zrPOt8+Ezq7PgiDOtM65zrHOtM65zrrPhM+Nzr/PhQpHZW5lcmljTmFtZVtlc109TmF2ZWdhZG9yIHdlYgpHZW5lcmljTmFtZVtldF09VmVlYmlicmF1c2VyCkdlbmVyaWNOYW1lW2ZhXT3Zhdix2YjYsdqv2LEg2KfbjNmG2KrYsdmG2KrbjApHZW5lcmljTmFtZVtmaV09V1dXLXNlbGFpbgpHZW5lcmljTmFtZVtmcl09TmF2aWdhdGV1ciBXZWIKR2VuZXJpY05hbWVbZ2xdPU5hdmVnYWRvciBXZWIKR2VuZXJpY05hbWVbaGVdPdeT16TXk9ek158g15DXmdeg15jXqNeg15gKR2VuZXJpY05hbWVbaHJdPVdlYiBwcmVnbGVkbmlrCkdlbmVyaWNOYW1lW2h1XT1XZWJiw7ZuZ8Opc3rFkQpHZW5lcmljTmFtZVtpdF09QnJvd3NlciBXZWIKR2VuZXJpY05hbWVbamFdPeOCpuOCp+ODluODu+ODluODqeOCpuOCtgpHZW5lcmljTmFtZVtrb1097Ju5IOu4jOudvOyasOyggApHZW5lcmljTmFtZVtrdV09R2Vyb2thIHRvcsOqCkdlbmVyaWNOYW1lW2x0XT1JbnRlcm5ldG8gbmFyxaF5a2zElwpHZW5lcmljTmFtZVtuYl09TmV0dGxlc2VyCkdlbmVyaWNOYW1lW25sXT1XZWJicm93c2VyCkdlbmVyaWNOYW1lW25uXT1OZXR0bGVzYXIKR2VuZXJpY05hbWVbbm9dPU5ldHRsZXNlcgpHZW5lcmljTmFtZVtwbF09UHJ6ZWdsxIVkYXJrYSBXV1cKR2VuZXJpY05hbWVbcHRdPU5hdmVnYWRvciBXZWIKR2VuZXJpY05hbWVbcHRfQlJdPU5hdmVnYWRvciBXZWIKR2VuZXJpY05hbWVbcm9dPU5hdmlnYXRvciBJbnRlcm5ldApHZW5lcmljTmFtZVtydV090JLQtdCxLdCx0YDQsNGD0LfQtdGACkdlbmVyaWNOYW1lW3NrXT1JbnRlcm5ldG92w70gcHJlaGxpYWRhxI0KR2VuZXJpY05hbWVbc2xdPVNwbGV0bmkgYnJza2FsbmlrCkdlbmVyaWNOYW1lW3N2XT1XZWJibMOkc2FyZQpHZW5lcmljTmFtZVt0cl09V2ViIFRhcmF5xLFjxLEKR2VuZXJpY05hbWVbdWddPdiq2YjYsdmD24bYsdqv24gKR2VuZXJpY05hbWVbdWtdPdCS0LXQsS3QsdGA0LDRg9C30LXRgApHZW5lcmljTmFtZVt2aV09VHLDrG5oIGR1eeG7h3QgV2ViCkdlbmVyaWNOYW1lW3poX0NOXT3nvZHnu5zmtY/op4jlmagKR2VuZXJpY05hbWVbemhfVFddPee2sui3r+eAj+imveWZqApDb21tZW50PUJyb3dzZSB0aGUgV2ViCkNvbW1lbnRbYXJdPdiq2LXZgditINin2YTZiNmQ2KgKQ29tbWVudFthc3RdPVJlc3RvbGEgcGVsYSBSZWRlCkNvbW1lbnRbYm5dPeCmh+CmqOCnjeCmn+CmvuCmsOCmqOCnh+CmnyDgpqzgp43gprDgpr7gpongppwg4KaV4Kaw4KeB4KaoCkNvbW1lbnRbY2FdPU5hdmVndWV1IHBlciBlbCB3ZWIKQ29tbWVudFtjc109UHJvaGzDrcW+ZW7DrSBzdHLDoW5layBXb3JsZCBXaWRlIFdlYnUKQ29tbWVudFtkYV09U3VyZiBww6UgaW50ZXJuZXR0ZXQKQ29tbWVudFtkZV09SW0gSW50ZXJuZXQgc3VyZmVuCkNvbW1lbnRbZWxdPc6cz4DOv8+BzrXOr8+EzrUgzr3OsSDPgM61z4HOuc63zrPOt864zrXOr8+EzrUgz4PPhM6/IM60zrnOsc60zq/Ous+Ez4XOvyAoV2ViKQpDb21tZW50W2VzXT1OYXZlZ3VlIHBvciBsYSB3ZWIKQ29tbWVudFtldF09TGVoaXRzZSB2ZWViaQpDb21tZW50W2ZhXT3YtdmB2K3Yp9iqINi02KjaqdmHINis2YfYp9mG24wg2KfbjNmG2KrYsdmG2Kog2LHYpyDZhdix2YjYsSDZhtmF2KfbjNuM2K8KQ29tbWVudFtmaV09U2VsYWEgSW50ZXJuZXRpbiBXV1ctc2l2dWphCkNvbW1lbnRbZnJdPU5hdmlndWVyIHN1ciBsZSBXZWIKQ29tbWVudFtnbF09TmF2ZWdhciBwb2xhIHJlZGUKQ29tbWVudFtoZV0915LXnNeZ16nXlCDXkdeo15fXkdeZINeU15DXmdeg15jXqNeg15gKQ29tbWVudFtocl09UHJldHJhxb5pdGUgd2ViCkNvbW1lbnRbaHVdPUEgdmlsw6FnaMOhbMOzIGLDtm5nw6lzesOpc2UKQ29tbWVudFtpdF09RXNwbG9yYSBpbCB3ZWIKQ29tbWVudFtqYV0944Km44Kn44OW44KS6Zay6Kan44GX44G+44GZCkNvbW1lbnRba29dPeybueydhCDrj4zslYQg64uk64uZ64uI64ukCkNvbW1lbnRba3VdPUxpIHRvcsOqIGJpZ2VyZQpDb21tZW50W2x0XT1OYXLFoXlraXRlIGludGVybmV0ZQpDb21tZW50W25iXT1TdXJmIHDDpSBuZXR0ZXQKQ29tbWVudFtubF09VmVya2VuIGhldCBpbnRlcm5ldApDb21tZW50W25uXT1TdXJmIHDDpSBuZXR0ZXQKQ29tbWVudFtub109U3VyZiBww6UgbmV0dGV0CkNvbW1lbnRbcGxdPVByemVnbMSFZGFuaWUgc3Ryb24gV1dXCkNvbW1lbnRbcHRdPU5hdmVndWUgbmEgSW50ZXJuZXQKQ29tbWVudFtwdF9CUl09TmF2ZWd1ZSBuYSBJbnRlcm5ldApDb21tZW50W3JvXT1OYXZpZ2HIm2kgcGUgSW50ZXJuZXQKQ29tbWVudFtydV090JTQvtGB0YLRg9C/INCyINCY0L3RgtC10YDQvdC10YIKQ29tbWVudFtza109UHJlaGxpYWRhbmllIGludGVybmV0dQpDb21tZW50W3NsXT1CcnNrYWp0ZSBwbyBzcGxldHUKQ29tbWVudFtzdl09U3VyZmEgcMOlIHdlYmJlbgpDb21tZW50W3RyXT3EsG50ZXJuZXQndGUgR2V6aW5pbgpDb21tZW50W3VnXT3Yr9uH2YbZitin2K/ZidmD2Ykg2KrZiNix2Kjbldiq2YTbldix2YbZiSDZg9uG2LHar9mJ2YTZiSDYqNmI2YTZidiv24cKQ29tbWVudFt1a1090J/QtdGA0LXQs9C70Y/QtCDRgdGC0L7RgNGW0L3QvtC6INCG0L3RgtC10YDQvdC10YLRgwpDb21tZW50W3ZpXT3EkOG7gyBkdXnhu4d0IGPDoWMgdHJhbmcgd2ViCkNvbW1lbnRbemhfQ05dPea1j+iniOS6kuiBlOe9kQpDb21tZW50W3poX1RXXT3ngI/opr3ntrLpmpvntrLot68KRXhlYz0lJSVFWFRSQUNUX0RJUiUlJS9maXJlZm94ICV1Ckljb249JSUlRVhUUkFDVF9ESVIlJSUvYnJvd3Nlci9jaHJvbWUvaWNvbnMvZGVmYXVsdC9kZWZhdWx0MTI4LnBuZwpUZXJtaW5hbD1mYWxzZQpUeXBlPUFwcGxpY2F0aW9uCk1pbWVUeXBlPXRleHQvaHRtbDt0ZXh0L3htbDthcHBsaWNhdGlvbi94aHRtbCt4bWw7YXBwbGljYXRpb24vdm5kLm1vemlsbGEueHVsK3htbDt0ZXh0L21tbDt4LXNjaGVtZS1oYW5kbGVyL2h0dHA7eC1zY2hlbWUtaGFuZGxlci9odHRwczsKU3RhcnR1cE5vdGlmeT10cnVlClN0YXJ0dXBXTUNsYXNzPUZpcmVmb3glJSVSRUxFQVNFX1RZUEUlJSUKQ2F0ZWdvcmllcz1OZXR3b3JrO1dlYkJyb3dzZXI7CktleXdvcmRzPXdlYjticm93c2VyO2ludGVybmV0OwpBY3Rpb25zPW5ldy13aW5kb3c7bmV3LXByaXZhdGUtd2luZG93OwoKW0Rlc2t0b3AgQWN0aW9uIG5ldy13aW5kb3ddCk5hbWU9TmV3IFdpbmRvdwpOYW1lW2FjaF09RGlyaWNhIG1hbnllbgpOYW1lW2FmXT1OdXdlIHZlbnN0ZXIKTmFtZVthbl09TnVldmEgZmluZXN0cmEKTmFtZVthcl092YbYp9mB2LDYqSDYrNiv2YrYr9ipCk5hbWVbYXNdPeCmqOCmpOCngeCmqCDgpongpofgpqjgp43gpqHgp4sKTmFtZVthc3RdPVZlbnRhbmEgbnVldmEKTmFtZVthel09WWVuaSBQyZluY8mZcsmZCk5hbWVbYmVdPdCd0L7QstCw0LUg0LDQutC90L4KTmFtZVtiZ1090J3QvtCyINC/0YDQvtC30L7RgNC10YYKTmFtZVtibl9CRF094Kao4Kak4KeB4KaoIOCmieCmh+CmqOCnjeCmoeCniyAoTikKTmFtZVtibl9JTl094Kao4Kak4KeB4KaoIOCmieCmh+CmqOCnjeCmoeCniwpOYW1lW2JyXT1QcmVuZXN0ciBuZXZlegpOYW1lW2JyeF094KSX4KWL4KSm4KS+4KSoIOCkieCkh+CkqOCljeCkoScoTikKTmFtZVtic109Tm92aSBwcm96b3IKTmFtZVtjYV09RmluZXN0cmEgbm92YQpOYW1lW2Nha109SydhaydhJyB0enV3w6RjaApOYW1lW2NzXT1Ob3bDqSBva25vCk5hbWVbY3ldPUZmZW5lc3RyIE5ld3lkZApOYW1lW2RhXT1OeXQgdmluZHVlCk5hbWVbZGVdPU5ldWVzIEZlbnN0ZXIKTmFtZVtkc2JdPU5vd2Ugd29rbm8KTmFtZVtlbF09zp3Orc6/IM+AzrHPgc6szrjPhc+Bzr8KTmFtZVtlbl9HQl09TmV3IFdpbmRvdwpOYW1lW2VuX1VTXT1OZXcgV2luZG93Ck5hbWVbZW5fWkFdPU5ldyBXaW5kb3cKTmFtZVtlb109Tm92YSBmZW5lc3RybwpOYW1lW2VzX0FSXT1OdWV2YSB2ZW50YW5hCk5hbWVbZXNfQ0xdPU51ZXZhIHZlbnRhbmEKTmFtZVtlc19FU109TnVldmEgdmVudGFuYQpOYW1lW2VzX01YXT1OdWV2YSB2ZW50YW5hCk5hbWVbZXRdPVV1cyBha2VuCk5hbWVbZXVdPUxlaWhvIGJlcnJpYQpOYW1lW2ZhXT3ZvtmG2KzYsdmHINis2K/bjNivCk5hbWVbZmZdPUhlbm9yZGUgSGVzZXJlCk5hbWVbZmldPVV1c2kgaWtrdW5hCk5hbWVbZnJdPU5vdXZlbGxlIGZlbsOqdHJlCk5hbWVbZnlfTkxdPU5paiBmaW5zdGVyCk5hbWVbZ2FfSUVdPUZ1aW5uZW9nIE51YQpOYW1lW2dkXT1VaW5uZWFnIMO5cgpOYW1lW2dsXT1Ob3ZhIHhhbmVsYQpOYW1lW2duXT1PdmV0w6MgcHlhaHUKTmFtZVtndV9JTl094Kqo4Kq14KuAIOCqteCqv+CqqOCrjeCqoeCriwpOYW1lW2hlXT3Xl9ec15XXnyDXl9eT16kKTmFtZVtoaV9JTl094KSo4KSv4KS+IOCkteCkv+CkguCkoeCliwpOYW1lW2hyXT1Ob3ZpIHByb3pvcgpOYW1lW2hzYl09Tm93ZSB3b2tubwpOYW1lW2h1XT3DmmogYWJsYWsKTmFtZVtoeV9BTV091YbVuNaAINWK1aHVv9W41oLVsNWh1bYKTmFtZVtpZF09SmVuZGVsYSBCYXJ1Ck5hbWVbaXNdPU7DvXIgZ2x1Z2dpCk5hbWVbaXRdPU51b3ZhIGZpbmVzdHJhCk5hbWVbamFdPeaWsOOBl+OBhOOCpuOCo+ODs+ODieOCpgpOYW1lW2phX0pQLW1hY1095paw6KaP44Km44Kk44Oz44OJ44KmCk5hbWVba2FdPeGDkOGDruGDkOGDmuGDmCDhg6Thg5Dhg5zhg6/hg5Dhg6Dhg5AKTmFtZVtra1090JbQsNKj0LAg0YLQtdGA0LXQt9C1Ck5hbWVba21dPeGelOGehOGfkuGeouGeveGeheGekOGfkuGemOGeuApOYW1lW2tuXT3gsrngs4rgsrgg4LKV4LK/4LKf4LKV4LK/Ck5hbWVba29dPeyDiCDssL0KTmFtZVtrb2tdPeCkqOCkteClh+CkgiDgpJzgpKjgpYfgpLIKTmFtZVtrc1092YbYptimINmI2ZDZhtqI2YgKTmFtZVtsaWpdPU5ldXZvIGJhcmNvbgpOYW1lW2xvXT3guqvgupngu4ngurLgupXgu4jgurLguofgu4PguqvguqHgu4gKTmFtZVtsdF09TmF1amFzIGxhbmdhcwpOYW1lW2x0Z109SmF1bnMgbMWrZ3MKTmFtZVtsdl09SmF1bnMgbG9ncwpOYW1lW21haV094KSo4KS1IOCkteCkv+CkguCkoeCliwpOYW1lW21rXT3QndC+0LIg0L/RgNC+0LfQvtGA0LXRhgpOYW1lW21sXT3gtKrgtYHgtKTgtL/gtK8g4LSc4LS+4LSy4LSV4LSCCk5hbWVbbXJdPeCkqOCkteClgOCkqCDgpKrgpJ/gpLIKTmFtZVttc109VGV0aW5na2FwIEJhcnUKTmFtZVtteV094YCd4YCE4YC64YC44YCS4YCt4YCv4YC44YCh4YCe4YCF4YC6Ck5hbWVbbmJfTk9dPU55dHQgdmluZHUKTmFtZVtuZV9OUF094KSo4KSv4KS+4KSBIOCkuOCknuCljeCkneCljeCkr+CkvuCksgpOYW1lW25sXT1OaWV1dyB2ZW5zdGVyCk5hbWVbbm5fTk9dPU55dHQgdmluZGF1Z2UKTmFtZVtvcl094Kyo4K2C4Kyk4KyoIOCtseCsv+Cso+CtjeCsoeCtiwpOYW1lW3BhX0lOXT3gqKjgqLXgqYDgqIIg4Ki14Ki/4Kmw4Kih4KmLCk5hbWVbcGxdPU5vd2Ugb2tubwpOYW1lW3B0X0JSXT1Ob3ZhIGphbmVsYQpOYW1lW3B0X1BUXT1Ob3ZhIGphbmVsYQpOYW1lW3JtXT1Ob3ZhIGZhbmVzdHJhCk5hbWVbcm9dPUZlcmVhc3RyxIMgbm91xIMKTmFtZVtydV090J3QvtCy0L7QtSDQvtC60L3QvgpOYW1lW3NhdF094KSo4KS+4KS14KS+IOCkteCkv+CkguCkoeCliyAoTikKTmFtZVtzaV094Lax4LeAIOC2muC3gOC3lOC3heC3lOC3gOC2muC3igpOYW1lW3NrXT1Ob3bDqSBva25vCk5hbWVbc2xdPU5vdm8gb2tubwpOYW1lW3Nvbl09WmFuZnVuIHRhYWdhCk5hbWVbc3FdPURyaXRhcmUgZSBSZQpOYW1lW3NyXT3QndC+0LLQuCDQv9GA0L7Qt9C+0YAKTmFtZVtzdl9TRV09Tnl0dCBmw7Zuc3RlcgpOYW1lW3RhXT3grqrgr4HgrqTgrr/grq8g4K6a4K6+4K6z4K6w4K6u4K+NCk5hbWVbdGVdPeCwleCxiuCwpOCxjeCwpCDgsLXgsL/gsILgsKHgsYsKTmFtZVt0aF094Lir4LiZ4LmJ4Liy4LiV4LmI4Liy4LiH4LmD4Lir4Lih4LmICk5hbWVbdHJdPVllbmkgcGVuY2VyZQpOYW1lW3Rzel09RXJhYXRhcmFrdWEgamltcGFuaQpOYW1lW3VrXT3QndC+0LLQtSDQstGW0LrQvdC+Ck5hbWVbdXJdPdmG24zYpyDYr9ix24zahtuBCk5hbWVbdXpdPVlhbmdpIG95bmEKTmFtZVt2aV09Q+G7rWEgc+G7lSBt4bubaQpOYW1lW3dvXT1QYWxhbnRlZXIgYnUgYmVlcwpOYW1lW3hoXT1JZmVzdGlsZSBlbnRzaGEKTmFtZVt6aF9DTl095paw5bu656qX5Y+jCk5hbWVbemhfVFddPemWi+aWsOimlueqlwpFeGVjPSUlJUVYVFJBQ1RfRElSJSUlL2ZpcmVmb3ggLS1uZXctd2luZG93ICV1CgpbRGVza3RvcCBBY3Rpb24gbmV3LXByaXZhdGUtd2luZG93XQpOYW1lPU5ldyBQcml2YXRlIFdpbmRvdwpOYW1lW2FjaF09RGlyaWNhIG1hbnllbiBtZSBtdW5nCk5hbWVbYWZdPU51d2UgcHJpdmFhdHZlbnN0ZXIKTmFtZVthbl09TnVldmEgZmluZXN0cmEgcHJpdmFkYQpOYW1lW2FyXT3Zhtin2YHYsNipINiu2KfYtdipINis2K/Zitiv2KkKTmFtZVthc1094Kao4Kak4KeB4KaoIOCmrOCnjeCmr+CmleCnjeCmpOCmv+Cml+CmpCDgpongpofgpqjgp43gpqHgp4sKTmFtZVthc3RdPVZlbnRhbmEgcHJpdmFkYSBudWV2YQpOYW1lW2F6XT1ZZW5pIE3JmXhmaSBQyZluY8mZcsmZCk5hbWVbYmVdPdCd0L7QstCw0LUg0LDQutC90L4g0LDQtNCw0YHQsNCx0LvQtdC90L3RjwpOYW1lW2JnXT3QndC+0LIg0L/RgNC+0LfQvtGA0LXRhiDQt9CwINC/0L7QstC10YDQuNGC0LXQu9C90L4g0YHRitGA0YTQuNGA0LDQvdC1Ck5hbWVbYm5fQkRdPeCmqOCmpOCngeCmqCDgpqzgp43gpq/gppXgp43gpqTgpr/gppfgpqQg4KaJ4KaH4Kao4KeN4Kah4KeLCk5hbWVbYm5fSU5dPeCmqOCmpOCngeCmqCDgpqzgp43gpq/gppXgp43gpqTgpr/gppfgpqQg4KaJ4KaH4Kao4KeN4Kah4KeLCk5hbWVbYnJdPVByZW5lc3RyIG1lcmRlacOxIHByZXZleiBuZXZlegpOYW1lW2JyeF094KSX4KWL4KSm4KS+4KSoIOCkquCljeCksOCkvuCkh+CkreClh+CknyDgpIngpIfgpKjgpY3gpKEnCk5hbWVbYnNdPU5vdmkgcHJpdmF0bmkgcHJvem9yCk5hbWVbY2FdPUZpbmVzdHJhIHByaXZhZGEgbm92YQpOYW1lW2Nha109SydhaydhJyBpY2hpbmFuIHR6dXfDpGNoCk5hbWVbY3NdPU5vdsOpIGFub255bW7DrSBva25vCk5hbWVbY3ldPUZmZW5lc3RyIEJyZWlmYXQgTmV3eWRkCk5hbWVbZGFdPU55dCBwcml2YXQgdmluZHVlCk5hbWVbZGVdPU5ldWVzIHByaXZhdGVzIEZlbnN0ZXIKTmFtZVtkc2JdPU5vd2UgcHJpd2F0bmUgd29rbm8KTmFtZVtlbF09zp3Orc6/IM+AzrHPgc6szrjPhc+Bzr8gzrnOtM65z4nPhM65zrrOrs+CIM+AzrXPgc65zq7Os863z4POt8+CCk5hbWVbZW5fR0JdPU5ldyBQcml2YXRlIFdpbmRvdwpOYW1lW2VuX1VTXT1OZXcgUHJpdmF0ZSBXaW5kb3cKTmFtZVtlbl9aQV09TmV3IFByaXZhdGUgV2luZG93Ck5hbWVbZW9dPU5vdmEgcHJpdmF0YSBmZW5lc3RybwpOYW1lW2VzX0FSXT1OdWV2YSB2ZW50YW5hIHByaXZhZGEKTmFtZVtlc19DTF09TnVldmEgdmVudGFuYSBwcml2YWRhCk5hbWVbZXNfRVNdPU51ZXZhIHZlbnRhbmEgcHJpdmFkYQpOYW1lW2VzX01YXT1OdWV2YSB2ZW50YW5hIHByaXZhZGEKTmFtZVtldF09VXVzIHByaXZhYXRuZSBha2VuCk5hbWVbZXVdPUxlaWhvIHByaWJhdHUgYmVycmlhCk5hbWVbZmFdPdm+2YbYrNix2Ycg2YbYp9i02YbYp9izINis2K/bjNivCk5hbWVbZmZdPUhlbm9yZGUgU3V0dXJvIEhlc2VyZQpOYW1lW2ZpXT1VdXNpIHlrc2l0eWluZW4gaWtrdW5hCk5hbWVbZnJdPU5vdXZlbGxlIGZlbsOqdHJlIGRlIG5hdmlnYXRpb24gcHJpdsOpZQpOYW1lW2Z5X05MXT1OaWogcHJpdmVlZmluc3RlcgpOYW1lW2dhX0lFXT1GdWlubmVvZyBOdWEgUGhyw61vYmjDoWlkZWFjaApOYW1lW2dkXT1VaW5uZWFnIHBocsOsb2JoYWlkZWFjaCDDuXIKTmFtZVtnbF09Tm92YSB4YW5lbGEgcHJpdmFkYQpOYW1lW2duXT1PdmV0w6Mgw7FlbWkgcHlhaHUKTmFtZVtndV9JTl094Kqo4Kq14KuAIOCqluCqvuCqqOCql+CrgCDgqrXgqr/gqqjgq43gqqHgq4sKTmFtZVtoZV0915fXnNeV158g16TXqNeY15kg15fXk9epCk5hbWVbaGlfSU5dPeCkqOCkr+ClgCDgpKjgpL/gpJzgpYAg4KS14KS/4KSC4KSh4KWLCk5hbWVbaHJdPU5vdmkgcHJpdmF0bmkgcHJvem9yCk5hbWVbaHNiXT1Ob3dlIHByaXdhdG5lIHdva25vCk5hbWVbaHVdPcOaaiBwcml2w6F0IGFibGFrCk5hbWVbaHlfQU1dPdWN1a/VvdWl1awg1LPVodWy1b/VttWrINWk1avVv9Wh1oDVr9W41oLVtApOYW1lW2lkXT1KZW5kZWxhIE1vZGUgUHJpYmFkaSBCYXJ1Ck5hbWVbaXNdPU7DvXIgaHVsacOwc2dsdWdnaQpOYW1lW2l0XT1OdW92YSBmaW5lc3RyYSBhbm9uaW1hCk5hbWVbamFdPeaWsOOBl+OBhOODl+ODqeOCpOODmeODvOODiOOCpuOCo+ODs+ODieOCpgpOYW1lW2phX0pQLW1hY1095paw6KaP44OX44Op44Kk44OZ44O844OI44Km44Kk44Oz44OJ44KmCk5hbWVba2FdPeGDkOGDruGDkOGDmuGDmCDhg57hg5jhg6Dhg5Dhg5Phg5gg4YOk4YOQ4YOc4YOv4YOQ4YOg4YOQCk5hbWVba2tdPdCW0LDSo9CwINC20LXQutC10LvRltC6INGC0LXRgNC10LfQtQpOYW1lW2ttXT3hnpThnoThn5LhnqLhnr3hnoXhnq/hnoDhnofhnpPhnpDhn5LhnpjhnrgKTmFtZVtrbl094LK54LOK4LK4IOCyluCyvuCyuOCyl+CyvyDgspXgsr/gsp/gspXgsr8KTmFtZVtrb1097IOIIOyCrOyDne2ZnCDrs7TtmLgg66qo65OcCk5hbWVba29rXT3gpKjgpLXgpYsg4KSW4KS+4KSc4KSX4KWAIOCkteCkv+CkguCkoeCliwpOYW1lW2tzXT3ZhtmS2Ygg2b7Ysdin24zZiNm5INmI24zZhtqI2YgKTmFtZVtsaWpdPU7DqnV2byBiYXJjw7NuIHByaXbDsnUKTmFtZVtsb1094LuA4Lqb4Lq14LqU4Lqr4LqZ4LuJ4Lqy4LqV4LuI4Lqy4LqH4Lqq4Lqn4LqZ4LqV4Lq74Lqn4LqC4Lq34LuJ4LqZ4Lqh4Lqy4LuD4Lqr4Lqh4LuICk5hbWVbbHRdPU5hdWphcyBwcml2YXRhdXMgbmFyxaF5bW8gbGFuZ2FzCk5hbWVbbHRnXT1KYXVucyBwcml2YXRhaXMgbMWrZ3MKTmFtZVtsdl09SmF1bnMgcHJpdsSBdGFpcyBsb2dzCk5hbWVbbWFpXT3gpKjgpK/gpL4g4KSo4KS/4KScIOCkteCkv+CkguCkoeCliyAoVykKTmFtZVtta1090J3QvtCyINC/0YDQuNCy0LDRgtC10L0g0L/RgNC+0LfQvtGA0LXRhgpOYW1lW21sXT3gtKrgtYHgtKTgtL/gtK8g4LS44LWN4LS14LSV4LS+4LSw4LWN4LSvIOC0nOC0vuC0suC0leC0ggpOYW1lW21yXT3gpKjgpLXgpYDgpKgg4KS14KWI4KSv4KSV4KWN4KSk4KS/4KSVIOCkquCkn+CksgpOYW1lW21zXT1UZXRpbmdrYXAgUGVyc2VuZGlyaWFuIEJhaGFydQpOYW1lW215XT1OZXcgUHJpdmF0ZSBXaW5kb3cKTmFtZVtuYl9OT109Tnl0dCBwcml2YXQgdmluZHUKTmFtZVtuZV9OUF094KSo4KSv4KS+4KSBIOCkqOCkv+CknOClgCDgpLjgpJ7gpY3gpJ3gpY3gpK/gpL7gpLIKTmFtZVtubF09TmlldXcgcHJpdsOpdmVuc3RlcgpOYW1lW25uX05PXT1OeXR0IHByaXZhdCB2aW5kYXVnZQpOYW1lW29yXT3grKjgrYLgrKTgrKgg4Kys4K2N4K2f4KyV4K2N4Kyk4Ky/4KyX4KykIOCtseCsv+Cso+CtjeCsoeCtiwpOYW1lW3BhX0lOXT3gqKjgqLXgqYDgqIIg4Kiq4KmN4Kiw4Ki+4KiI4Ki14KmH4KifIOCoteCov+CpsOCooeCpiwpOYW1lW3BsXT1Ob3dlIG9rbm8gcHJ5d2F0bmUKTmFtZVtwdF9CUl09Tm92YSBqYW5lbGEgcHJpdmF0aXZhCk5hbWVbcHRfUFRdPU5vdmEgamFuZWxhIHByaXZhZGEKTmFtZVtybV09Tm92YSBmYW5lc3RyYSBwcml2YXRhCk5hbWVbcm9dPUZlcmVhc3RyxIMgcHJpdmF0xIMgbm91xIMKTmFtZVtydV090J3QvtCy0L7QtSDQv9GA0LjQstCw0YLQvdC+0LUg0L7QutC90L4KTmFtZVtzYXRdPeCkqOCkvuCkteCkviDgpKjgpL/gpJzgpYfgpLDgpL7gpJXgpY0g4KS14KS/4KSC4KSh4KWLIChXICkKTmFtZVtzaV094Lax4LeAIOC2tOC3lOC2r+C3iuC2nOC2veC3kuC2miDgtprgt4Dgt5Tgt4Xgt5Tgt4AgKFcpCk5hbWVbc2tdPU5vdsOpIG9rbm8gdiByZcW+aW1lIFPDumtyb21uw6kgcHJlaGxpYWRhbmllCk5hbWVbc2xdPU5vdm8gemFzZWJubyBva25vCk5hbWVbc29uXT1TdXR1cmEgemFuZnVuIHRhYWdhCk5hbWVbc3FdPURyaXRhcmUgZSBSZSBQcml2YXRlCk5hbWVbc3JdPdCd0L7QstC4INC/0YDQuNCy0LDRgtCw0L0g0L/RgNC+0LfQvtGACk5hbWVbc3ZfU0VdPU55dHQgcHJpdmF0IGbDtm5zdGVyCk5hbWVbdGFdPeCuquCvgeCupOCuv+CuryDgrqTgrqngrr/grqrgr43grqrgrp/gr43grp8g4K6a4K6+4K6z4K6w4K6u4K+NCk5hbWVbdGVdPeCwleCxiuCwpOCxjeCwpCDgsIbgsILgsKTgsLDgsILgsJfgsL/gsJUg4LC14LC/4LCC4LCh4LGLCk5hbWVbdGhdPeC4q+C4meC5ieC4suC4leC5iOC4suC4h+C4quC5iOC4p+C4meC4leC4seC4p+C5g+C4q+C4oeC5iApOYW1lW3RyXT1ZZW5pIGdpemxpIHBlbmNlcmUKTmFtZVt0c3pdPUp1Y2hpaXRpIGVyYWF0YXJha3VhIGppbXBhbmkKTmFtZVt1a1090J/RgNC40LLQsNGC0L3QtSDQstGW0LrQvdC+Ck5hbWVbdXJdPdmG24zYpyDZhtis24wg2K/YsduM2obbgQpOYW1lW3V6XT1ZYW5naSBtYXhmaXkgb3luYQpOYW1lW3ZpXT1D4butYSBz4buVIHJpw6puZyB0xrAgbeG7m2kKTmFtZVt3b109UGFubGFudGVlcnUgYmlpciBidSBiZWVzCk5hbWVbeGhdPUlmZXN0aWxlIHlhbmdhc2VzZSBlbnRzaGEKTmFtZVt6aF9DTl095paw5bu66ZqQ56eB5rWP6KeI56qX5Y+jCk5hbWVbemhfVFddPeaWsOWinumaseengeimlueqlwpFeGVjPSUlJUVYVFJBQ1RfRElSJSUlL2ZpcmVmb3ggLS1wcml2YXRlLXdpbmRvdyAldQo="
    )
    desktop_data = desktop_data.replace(
        b"%%%RELEASE_TYPE%%%", release_type.encode("utf-8")
    )
    desktop_data = desktop_data.replace(
        b"%%%EXTRACT_DIR%%%", extract_dir.encode("utf-8")
    )
    with open(
        expanduser(f"~/.local/share/applications/firefox_{_release_type}.desktop"),
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
    extract_dir = expanduser(
        f"~/Applications/firefox_{product_select[len('desktop_'):]}-{platform_select}-{language_select}"
    )
    download_and_extract(current_href, extract_dir)

    print()
    print("Creating desktop file.")
    create_desktop(product_select, extract_dir)
    print("Desktop file created.")


if __name__ == "__main__":
    main()
