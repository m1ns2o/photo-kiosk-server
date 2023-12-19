from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import uuid
from cryptography.fernet import Fernet
from pydantic import BaseModel
import base64
import aiohttp
from aiohttp import FormData
import logging
from fastapi.staticfiles import StaticFiles
from pyppeteer import launch
from PIL import Image
import cv2
import numpy as np
import asyncio
from selenium import webdriver
import time
import traceback
import os

import subprocess





logging.basicConfig(level=logging.DEBUG)


app = FastAPI()

key = Fernet.generate_key()
cipher_suite = Fernet(key)

physical_uuid: int = 0
external_server:int = ""
dir:str = ''
comand =[]

# CORS Middleware 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    # allow_origins=["http://127.0.0.1:5173"],  # 모든 출처를 허용하거나 특정 도메인들의 리스트를 제공하십시오.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

class ImageData(BaseModel):
    # image_addr: str #이미지 qr코드 주소
    image_data: str #파일 이미지


# async def send_file_using_httpx(file_name: str, file_buffer):
#     async with httpx.AsyncClient() as client:
#         response = await client.post("https://yourserver.com/receive", files={"file": (f"{file_name}.mp4", file_buffer)})
#     return response



# @app.on_event("startup")
# async def run_on_startup():
#     global physical_uuid, dir, external_server
#     with open('settings.json', 'r') as file:
#         data = json.load(file)
#     physical_uuid = data["uuid"]
#     dir = data["dir"]
#     external_server = data["external_server"]
#     input_file = dir + "test.mp4"
#     output_file = "output.mp4"
#     target_bitrate = "5000k"  # Set your desired bitrate
#
#     command = [
#         "ffmpeg",
#         "-i", input_file,
#         "-b:v", target_bitrate,
#         "-c:a", "copy",  # Copy audio codec without re-encoding
#         output_file
#     ]

@app.on_event("startup")
async def run_on_startup():
    global physical_uuid, dir, external_server, command
    with open('settings.json', 'r') as file:
        data = json.load(file)
    physical_uuid = data["uuid"]
    dir = data["dir"]
    external_server = data["external_server"]
    input_file = dir + "test.mp4"
    output_file = "output.mp4"
    target_bitrate = "5000k"  # Set your desired bitrate

    command = [
        "ffmpeg",
        "-i", input_file,
        "-b:v", target_bitrate,
        "-c:a", "copy",  # Copy audio codec without re-encoding
        output_file
    ]


@app.get("/file/{file_name}", response_class=FileResponse)
def img_list(file_name: str):
    file_response = FileResponse(dir + file_name)
    file_response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
    return file_response


@app.get("/imgprocess/grayscale")
def img_convert_grayscale():
    for i in range(0, 8):
        image = Image.open(dir + str(i) + '.JPG')
        gray_image = image.convert("L")
        gray_image_path = dir + str(i) + "_g.jpg"
        gray_image.save(gray_image_path)
    return {"message": "success"}


@app.get("/file/{file_name}/grayscale", response_class=FileResponse)
def img_list_grayscale(file_name: str):
    file_response = FileResponse(dir + file_name[0] + "_g.jpg")
    file_response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
    return file_response


@app.get("/capture/{file_name}", response_class=FileResponse)
def img_list(file_name: str):
    file_response = FileResponse(dir + file_name)
    # file_response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
    return file_response





# @app.get("/test/addr")
# def testfunc():
#     return {"text": "test"}


@app.get("/qr")
def qr_uuid_random():
    global physical_uuid
    uuid_v1 = str(uuid.uuid1())
    # encrypted_text = cipher_suite.encrypt(physical_uuid.encode())
    text = uuid_v1[:20] + physical_uuid + uuid_v1[20:]
    # print(len(encrypted_text))
    return {"qr": text, "length": len(text)}

@app.post("/save")
def save_image_async(data: ImageData):
    image_data = data.image_data.split(",")[1]
    decoded_image_data = base64.b64decode(image_data)

    # 고유한 .jpg 파일 이름 생성
    # 이미지를 로컬 디렉토리에 .jpg 형식으로 저장
    with open("print_img.jpg", 'wb') as image_file:
        image_file.write(decoded_image_data)

    # 이미지 파일 경로를 DB에 저장

    return {"id": "img_Save"}


# @app.get("/print/{size}")
# def img_list_grayscale(size: int):
#     if size==0:
#
#     elif size==1:
#
#     return {"print_success"}
# @app.get("/mp4/{file_name}")
# async def send_mp4(file_name: str, file: UploadFile = UploadFile(...)):
#     print("call")
#     re = requests.get(external_server+"/img/safsa")
#     print(re)
#     try:
#         # 파일 저장
#         file_location = dir + "test.mp4"
#         with open(file_location, "wb+") as buffer:
#             buffer.write(file.file.read())
#
#         # 파일을 원격 서버로 전송
#         with open(file_location, "rb") as file_buffer:
#             # response = requests.post(external_server+"/receive", files={"file": (f"{file_name}.mp4", file_buffer)})
#             response = await send_file_using_httpx(file_name, file_buffer)
#             print(response.status_code)
#             print(response.text)
#
#         if response.status_code == 200:
#             return {"id": id}
#         else:
#             return {"error": "Failed to send the file to the remote server."}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail="File upload or send failed")


# async def send_file_using_aiohttp(file_name: str, file_buffer) -> tuple:
#     async with aiohttp.ClientSession() as session:
#         data = {'file': (file_name, file_buffer, 'video/mp4')}
#         async with session.post(external_server + "/receive/", data=data) as response:
#             return response.status, await response.text()




async def send_file_using_aiohttp(file_name: str, file_buffer) -> tuple:
    async with aiohttp.ClientSession() as session:
        data = FormData()
        data.add_field('file', file_buffer, filename=file_name, content_type='video/mp4')
        async with session.post(external_server+ "/receive", data=data) as response:
            print(external_server+"/receive")
            return response.status, await response.text()


# @app.get("/downsampling")
# def downsampling_mp4():
#     try:
#         print(command)
#         result = subprocess.run(command, capture_output=True, text=True)
#         print(result.stdout)
#         print("After subprocess.run")
#         return {"mp4 file downscale complete"}
#
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"File upload or send failed: {str(e)}")

@app.get("/mp4/{file_name}")
async def send_mp4(file_name: str):
    try:
        # 로컬에서 파일 불러오기
        print(command)
        result = subprocess.run(command, capture_output=True, text=True)
        print(result.stdout)
        print("After subprocess.run")

        with open("output.mp4", "rb") as file_buffer:
            status_code, response_text = await send_file_using_aiohttp(file_name, file_buffer)
            print(status_code)
            print(response_text)
            delete_file("output.mp4")

        if status_code == 200:
            return {"file_name": file_name}
        else:
            return {"error": "Failed to send the file to the remote server."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"File upload or send failed: {str(e)}")



def delete_file(path:str):
    try:
        os.remove(path)
        print(f"{path} deleted successfully.")
    except FileNotFoundError:
        print(f"File not found: {path}")
    except Exception as e:
        print(f"An error occurred: {e}")
# @app.get("/mp4/{file_name}")
# async def send_mp4(file_name: str):
#     try:
#         # 파일 저장
#         file_location = dir + "test.mp4"
#         with open(file_location, "wb+") as buffer:
#             buffer.write(file.file.read())
#
#         # 파일을 원격 서버로 전송
#         with open(file_location, "rb") as file_buffer:
#             status_code, response_text = await send_file_using_aiohttp(file_name, file_buffer)
#             print(status_code)
#             print(response_text)
#
#         if status_code == 200:
#             return {"file_name": file_name}
#         else:
#             return {"error": "Failed to send the file to the remote server."}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail="File upload or send failed")



#비디오 출력
# ... 기존의 코드 ...


