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
def img_list(file_name: str):
    file_response = FileResponse(file_name)
    file_response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
    return file_response

@app.get("/imgprocess/grayscale")
def img_convert_grayscale():
    for i in range(0,8):
        image = Image.open(str(i) + '.JPG')
        gray_image = image.convert("L")
        gray_image_path = str(i)+"_g.jpg"
        gray_image.save(gray_image_path)
    return {"message": "success"}

@app.get("/file/{file_name}/grayscale", response_class=FileResponse)
def img_list_grayscale(file_name: str):
    file_response = FileResponse(file_name[0]+"_g.jpg")
    file_response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
    return file_response

