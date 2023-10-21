from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image

app = FastAPI()

# CORS Middleware 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173"],  # 모든 출처를 허용하거나 특정 도메인들의 리스트를 제공하십시오.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/file/{file_name}", response_class=FileResponse)
async def img_list(file_name: str):
    file_response = FileResponse(file_name)
    file_response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
    return file_response

@app.get("/file/{file_name}/grayscale", response_class=FileResponse)
async def img_list(file_name: str):
    image = Image.open(file_name)

    # 그레이스케일로 변환
    gray_image = image.convert("L")

    # 결과 저장
    gray_image_path = file_name[0]+"_g.jpg"
    gray_image.save(gray_image_path)
    file_response = FileResponse(gray_image_path)
    file_response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
    return file_response

