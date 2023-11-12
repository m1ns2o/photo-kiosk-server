import win32gui
import win32ui
import win32con
import win32api


def capture_window(hwnd):
    # 윈도우의 디바이스 컨텍스트(DC)를 가져옴
    wDC = win32gui.GetWindowDC(hwnd)
    dcObj = win32ui.CreateDCFromHandle(wDC)
    cDC = dcObj.CreateCompatibleDC()

    # 윈도우의 크기를 구함
    left, top, right, bot = win32gui.GetClientRect(hwnd)
    width = right - left
    height = bot - top

    # 캡처할 이미지를 위한 비트맵 생성
    bmp = win32ui.CreateBitmap()
    bmp.CreateCompatibleBitmap(dcObj, width, height)

    # 준비된 비트맵과 호환되는 DC에 그림을 그림
    cDC.SelectObject(bmp)

    # 실제 윈도우에서 비트맵으로 복사
    cDC.BitBlt((0, 0), (width, height), dcObj, (left, top), win32con.SRCCOPY)

    # 결과 이미지를 파일로 저장
    bmp.SaveBitmapFile(cDC, 'screenshot.bmp')

    # 리소스 정리
    dcObj.DeleteDC()
    cDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, wDC)
    win32gui.DeleteObject(bmp.GetHandle())


# 프로세스의 윈도우 핸들을 얻는 예시 함수 (프로세스 이름으로부터)
def get_window_handle(process_name):
    def callback(hwnd, extra):
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd) == process_name:
            extra.append(hwnd)
        return True

    windows = []
    win32gui.EnumWindows(callback, windows)
    return windows[0] if windows else None


# 사용 예시
hwnd = get_window_handle('Notepad')
if hwnd:
    capture_window(hwnd)
else:
    print("No window found.")
