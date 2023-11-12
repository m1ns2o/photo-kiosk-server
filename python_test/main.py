import asyncio
from pyppeteer import launch
import numpy as np
import cv2
import time
from io import BytesIO

async def capture():
    # 브라우저 시작
    #C:\Users\srjms\AppData\Local\pyppeteer\pyppeteer\local-chromium\588429\chrome-win32\chrome.exe
    browser = await launch(headless=True, executablePath='C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe', args=['--window-size=1920,1080','--enable-webgl',
            '--use-gl=desktop',])
    page = await browser.newPage()
    await page.setViewport({'width': 400, 'height': 600, 'deviceScaleFactor': 2})

    # 웹페이지로 이동
    await page.goto('http://127.0.0.1:5173/pinia')

    await page.waitForSelector('#img')
    # 캡쳐 설정
    capture_duration = 10  # 캡쳐할 시간 (초)
    # capture_interval = 0.001  # 캡쳐 간격 (초)
    frame_rate = 15  # 영상 프레임레이트

    # 캡쳐 이미지 저장할 리스트
    images = []

    start_time = time.time()
    while (time.time() - start_time) < capture_duration:
        # 특정 요소 스크린샷 찍기
        element = await page.querySelector('#img')
        png = await element.screenshot()
        image_np = np.frombuffer(png, dtype=np.uint8)
        image_cv = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
        images.append(image_cv)

        # 설정한 간격만큼 대기
        # await asyncio.sleep(capture_interval)

    # 브라우저 종료
    await browser.close()

    # 영상으로 저장
    height, width, layers = images[0].shape
    size = (width, height)

    out = cv2.VideoWriter('output_video.avi', cv2.VideoWriter_fourcc(*'DIVX'), frame_rate, size)

    for img in images:
        out.write(img)

    out.release()

# 비동기 함수 실행
asyncio.get_event_loop().run_until_complete(capture())
