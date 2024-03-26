from pprint import pprint

import requests

cookies = {
    'gdpr': '0',
    '_ym_uid': '1631993328912305714',
    'my': 'YwA=',
    'yandexuid': '813901861631993327',
    'yuidss': '813901861631993327',
    'ymex': '1995951301.yrts.1680591301#1993746740.yrtsi.1678386740',
    'yashr': '3410016991696332990',
    'font_loaded': 'YSv1',
    'KIykI': '1',
    'amcuid': '2216652521705504642',
    'L': 'Q2h9BkJyfUNlBkEKBlB8dVxdVgB1S29JM15aHCUdQx8kDREEcX51.1706286164.15600.370264.58ac281d8ebfbae6d3dfed1d6799240a',
    'yandex_login': 'egorkopitov1709',
    'bltsr': '1',
    'isa': '/EbjIV11VAr3XPmBfUlPUpeaQh5mhPsVMRr8GCtAVpoSQ39pndGIJmSyKu7rVnni28caGHp8pkeRk+l11bljBa/I6Vw=',
    'sae': '0:AC02012B-0538-4290-AE86-189D31078218:p:24.1.4.827:w:d:RU:20210918',
    'Session_id': '3:1711395477.5.0.1638006993869:rTDivA:b.1.1:czoxNjMxOTkzOTk3MDE4OnJURGl2QToxMQ.2:1|342740726.12621811.2.2:23329268|1230704413.692676.2.2:692676|1656479062.23870476.402.2:23870476|3:10285059.162332.hn8F1tsXTWPK58cd-HIHzvcaX8w',
    'sessar': '1.1188.CiDzc2hbW8wv7gXLxiOw315Gn7FQGOJd0RAcybhtfpH9wA.OVhjzA19fM18JCBRYWpW2CZ8bWdjPUIPDBRm3hHVy2w',
    'sessionid2': '3:1711395477.5.0.1638006993869:rTDivA:b.1.1:czoxNjMxOTkzOTk3MDE4OnJURGl2QToxMQ.2:1|342740726.12621811.2.2:23329268|1230704413.692676.2.2:692676|1656479062.23870476.402.2:23870476|3:10285059.162332.fakesign0000000000000000000',
    'i': 'fD/WN4GL993Aa5YIsBH0pPulH/ITCTywZXOal8F/xt92zgg9i4x54k3S1aKLxdvZMmwFRwAEV8f2Z5Qg7GF/gZxl/Uw=',
    'ys': 'def_bro.1#udn.cDrQldCz0L7RgCDQmtC%2B0L%2FRi9GC0L7Qsg%3D%3D#wprid.1711466139112517-10626953683844039971-balancer-l7leveler-kubr-yp-sas-32-BAL#c_chck.3892397048',
    'PHPSESSID': 'd1a0940bb9794e3c934b25de73cefdba',
    'bh': 'Ek8iTm90X0EgQnJhbmQiO3Y9IjgiLCAiQ2hyb21pdW0iO3Y9IjEyMCIsICJZYUJyb3dzZXIiO3Y9IjI0LjEiLCAiWW93c2VyIjt2PSIyLjUiGgUieDg2IiIMIjI0LjEuNC44MjciKgI/MDoJIldpbmRvd3MiQggiMTAuMC4wIkoEIjY0IlJmIk5vdF9BIEJyYW5kIjt2PSI4LjAuMC4wIiwgIkNocm9taXVtIjt2PSIxMjAuMC42MDk5LjI5MSIsICJZYUJyb3dzZXIiO3Y9IjI0LjEuNC44MjciLCAiWW93c2VyIjt2PSIyLjUiWgI/MA==',
    'is_gdpr': '0',
    'is_gdpr_b': 'CLj5IhDi8gEoAg==',
    'yp': '1711529357.uc.ru#1711529357.duc.us#1735237446.cld.2270452#1735237446.brd.6400000000#1726979850.szm.1:2560x1080:2560x958#2021646164.udn.cDrQldCz0L7RgCDQmtC%2B0L/Ri9GC0L7Qsg%3D%3D#1986028070.multib.1#2026826139.pcs.1#1711913370.hdrc.1#1713824441.v_smr_onb.t%3D2:1706048441390#1713866111.csc.1#1739957412.sp.bhtt:0:family:0#1711475960.gpauto.56_838013:60_597466:100000:3:1711468760#4294967295.yrntf.disaster%2Emsk20240322:c7d9:1711223173',
    '_yasc': '3u0z2d3iT35gAdGWbw7sHdCB2FjLsP9N3FatlZjIkXwBz7eziCEiz9bZMf6Ur46N6puwcpcMMLtRtkQOFlM=',
    'eda_web': '{%22app%22:{%22analyticsSession%22:{%22id%22:%22lu8ir1vh-820bljdlkh-1rk3ljmm8np-4lb6978co0g%22%2C%22start%22:1711466141%2C%22update%22:1711468886}%2C%22deliveryTime%22:null%2C%22themeVariantKey%22:%22light%22%2C%22lat%22:56.81340060222499%2C%22lon%22:60.582223576927944%2C%22xDeviceId%22:%22lm0gkz7m-p39a8nt3zff-9icusputium-hedsws4buw%22%2C%22appBannerShown%22:false%2C%22yandexPlusCashbackOptInChecked%22:false%2C%22testRunId%22:null%2C%22initialPromocode%22:null%2C%22translateMenu%22:false}}',
}

headers = {
    'authority': 'eda.yandex.ru',
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'ru',
    'content-type': 'application/json;charset=UTF-8',
    # 'cookie': 'gdpr=0; _ym_uid=1631993328912305714; my=YwA=; yandexuid=813901861631993327; yuidss=813901861631993327; ymex=1995951301.yrts.1680591301#1993746740.yrtsi.1678386740; yashr=3410016991696332990; font_loaded=YSv1; KIykI=1; amcuid=2216652521705504642; L=Q2h9BkJyfUNlBkEKBlB8dVxdVgB1S29JM15aHCUdQx8kDREEcX51.1706286164.15600.370264.58ac281d8ebfbae6d3dfed1d6799240a; yandex_login=egorkopitov1709; bltsr=1; isa=/EbjIV11VAr3XPmBfUlPUpeaQh5mhPsVMRr8GCtAVpoSQ39pndGIJmSyKu7rVnni28caGHp8pkeRk+l11bljBa/I6Vw=; sae=0:AC02012B-0538-4290-AE86-189D31078218:p:24.1.4.827:w:d:RU:20210918; Session_id=3:1711395477.5.0.1638006993869:rTDivA:b.1.1:czoxNjMxOTkzOTk3MDE4OnJURGl2QToxMQ.2:1|342740726.12621811.2.2:23329268|1230704413.692676.2.2:692676|1656479062.23870476.402.2:23870476|3:10285059.162332.hn8F1tsXTWPK58cd-HIHzvcaX8w; sessar=1.1188.CiDzc2hbW8wv7gXLxiOw315Gn7FQGOJd0RAcybhtfpH9wA.OVhjzA19fM18JCBRYWpW2CZ8bWdjPUIPDBRm3hHVy2w; sessionid2=3:1711395477.5.0.1638006993869:rTDivA:b.1.1:czoxNjMxOTkzOTk3MDE4OnJURGl2QToxMQ.2:1|342740726.12621811.2.2:23329268|1230704413.692676.2.2:692676|1656479062.23870476.402.2:23870476|3:10285059.162332.fakesign0000000000000000000; i=fD/WN4GL993Aa5YIsBH0pPulH/ITCTywZXOal8F/xt92zgg9i4x54k3S1aKLxdvZMmwFRwAEV8f2Z5Qg7GF/gZxl/Uw=; ys=def_bro.1#udn.cDrQldCz0L7RgCDQmtC%2B0L%2FRi9GC0L7Qsg%3D%3D#wprid.1711466139112517-10626953683844039971-balancer-l7leveler-kubr-yp-sas-32-BAL#c_chck.3892397048; PHPSESSID=d1a0940bb9794e3c934b25de73cefdba; bh=Ek8iTm90X0EgQnJhbmQiO3Y9IjgiLCAiQ2hyb21pdW0iO3Y9IjEyMCIsICJZYUJyb3dzZXIiO3Y9IjI0LjEiLCAiWW93c2VyIjt2PSIyLjUiGgUieDg2IiIMIjI0LjEuNC44MjciKgI/MDoJIldpbmRvd3MiQggiMTAuMC4wIkoEIjY0IlJmIk5vdF9BIEJyYW5kIjt2PSI4LjAuMC4wIiwgIkNocm9taXVtIjt2PSIxMjAuMC42MDk5LjI5MSIsICJZYUJyb3dzZXIiO3Y9IjI0LjEuNC44MjciLCAiWW93c2VyIjt2PSIyLjUiWgI/MA==; is_gdpr=0; is_gdpr_b=CLj5IhDi8gEoAg==; yp=1711529357.uc.ru#1711529357.duc.us#1735237446.cld.2270452#1735237446.brd.6400000000#1726979850.szm.1:2560x1080:2560x958#2021646164.udn.cDrQldCz0L7RgCDQmtC%2B0L/Ri9GC0L7Qsg%3D%3D#1986028070.multib.1#2026826139.pcs.1#1711913370.hdrc.1#1713824441.v_smr_onb.t%3D2:1706048441390#1713866111.csc.1#1739957412.sp.bhtt:0:family:0#1711475960.gpauto.56_838013:60_597466:100000:3:1711468760#4294967295.yrntf.disaster%2Emsk20240322:c7d9:1711223173; _yasc=3u0z2d3iT35gAdGWbw7sHdCB2FjLsP9N3FatlZjIkXwBz7eziCEiz9bZMf6Ur46N6puwcpcMMLtRtkQOFlM=; eda_web={%22app%22:{%22analyticsSession%22:{%22id%22:%22lu8ir1vh-820bljdlkh-1rk3ljmm8np-4lb6978co0g%22%2C%22start%22:1711466141%2C%22update%22:1711468886}%2C%22deliveryTime%22:null%2C%22themeVariantKey%22:%22light%22%2C%22lat%22:56.81340060222499%2C%22lon%22:60.582223576927944%2C%22xDeviceId%22:%22lm0gkz7m-p39a8nt3zff-9icusputium-hedsws4buw%22%2C%22appBannerShown%22:false%2C%22yandexPlusCashbackOptInChecked%22:false%2C%22testRunId%22:null%2C%22initialPromocode%22:null%2C%22translateMenu%22:false}}',
    'origin': 'https://eda.yandex.ru',
    'referer': 'https://eda.yandex.ru/ekaterinburg?shippingType=delivery',
    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "YaBrowser";v="24.1", "Yowser";v="2.5"',
    'sec-ch-ua-arch': '"x86"',
    'sec-ch-ua-bitness': '"64"',
    'sec-ch-ua-full-version-list': '"Not_A Brand";v="8.0.0.0", "Chromium";v="120.0.6099.291", "YaBrowser";v="24.1.4.827", "Yowser";v="2.5"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-ch-ua-platform-version': '"10.0.0"',
    'sec-ch-ua-wow64': '?0',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 YaBrowser/24.1.0.0 Safari/537.36',
    'x-app-version': '16.43.0',
    'x-client-session': 'lu8ir1vh-820bljdlkh-1rk3ljmm8np-4lb6978co0g',
    'x-device-id': 'lm0gkz7m-p39a8nt3zff-9icusputium-hedsws4buw',
    'x-platform': 'desktop_web',
    'x-taxi': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 YaBrowser/24.1.0.0 Safari/537.36 platform=eats_desktop_web',
    'x-ya-coordinates': 'latitude=56.81340060222499,longitude=60.582223576927944',
}

json_data = {
    'location': {
        'latitude': 56.81340060222499,
        'longitude': 60.582223576927944,
    },
}

response = requests.post(
    'https://eda.yandex.ru/eats/v1/layout-constructor/v1/layout',
    cookies=cookies,
    headers=headers,
    json=json_data,
)


pprint(response.json())
