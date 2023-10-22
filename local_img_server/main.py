from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import json
import uuid
from cryptography.fernet import Fernet
from pydantic import BaseModel
import base64

app = FastAPI()

key = Fernet.generate_key()
cipher_suite = Fernet(key)

physical_uuid: int = 0

# CORS Middleware 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173"],  # 모든 출처를 허용하거나 특정 도메인들의 리스트를 제공하십시오.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ImageData(BaseModel):
    # image_addr: str #이미지 qr코드 주소
    image_data: str #파일 이미지

@app.on_event("startup")
async def run_on_startup():
    global physical_uuid
    with open('settings.json', 'r') as file:
        data = json.load(file)
    physical_uuid = data["uuid"]

@app.get("/file/{file_name}", response_class=FileResponse)
def img_list(file_name: str):
    file_response = FileResponse(file_name)
    file_response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
    return file_response


@app.get("/imgprocess/grayscale")
def img_convert_grayscale():
    for i in range(0, 8):
        image = Image.open(str(i) + '.JPG')
        gray_image = image.convert("L")
        gray_image_path = str(i) + "_g.jpg"
        gray_image.save(gray_image_path)
    return {"message": "success"}


@app.get("/file/{file_name}/grayscale", response_class=FileResponse)
def img_list_grayscale(file_name: str):
    file_response = FileResponse(file_name[0] + "_g.jpg")
    file_response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
    return file_response


@app.get("/test/addr")
def testfunc():
    return {"text": "test"}


@app.get("/qr")
def qr_uuid_random():
    global physical_uuid
    uuid_v1 = str(uuid.uuid1())
    # encrypted_text = cipher_suite.encrypt(physical_uuid.encode())
    text = uuid_v1[:20] + physical_uuid + uuid_v1[20:]
    # print(len(encrypted_text))
    return {"qr": text, "length": len(text)}

@app.post("/save")
async def save_image_async(data: ImageData):
    image_data = data.image_data.split(",")[1]
    decoded_image_data = base64.b64decode(image_data)

    # 고유한 .jpg 파일 이름 생성
    # 이미지를 로컬 디렉토리에 .jpg 형식으로 저장
    with open("print_img.jpg", 'wb') as image_file:
        image_file.write(decoded_image_data)

    # 이미지 파일 경로를 DB에 저장

    return {"id": "img_Save"}
