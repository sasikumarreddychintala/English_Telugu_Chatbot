# from fastapi.staticfiles import StaticFiles
# from fastapi.templating import Jinja2Templates
# from googletrans import Translator
# from PIL import Image
# import pytesseract
# import io
# import cgi



# app = FastAPI(title="English to Telugu Chatbot")

# # Template setup
# templates = Jinja2Templates(directory="templates")

# translator = Translator()


# @app.get("/", response_class=HTMLResponse)
# async def home(request: Request):
#     return templates.TemplateResponse("index.html", {"request": request})


# @app.post("/chat/")
# async def chat(
#     request: Request,
#     message: str = Form(None),
#     file: UploadFile = File(None)
# ):
#     try:
#         english_text = ""

#         # If image uploaded
#         if file:
#             image_bytes = await file.read()
#             image = Image.open(io.BytesIO(image_bytes))
#             english_text = pytesseract.image_to_string(image, lang="eng").strip()
#             if not english_text:
#                 return JSONResponse({"error": "No readable text found in the image."}, status_code=400)

#         # If text message sent
#         elif message:
#             english_text = message.strip()

#         else:
#             return JSONResponse({"error": "No input provided."}, status_code=400)

#         # Translate
#         translation = translator.translate(english_text, src="en", dest="te")

#         return {"english_text": english_text, "telugu_translation": translation.text}

#     except Exception as e:
#         return JSONResponse({"error": str(e)}, status_code=500)

from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from googletrans import Translator
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import io
from indic_transliteration.sanscript import transliterate, ITRANS, TELUGU



app = FastAPI(title="English to Telugu Chatbot")

templates = Jinja2Templates(directory="templates")
translator = Translator()


def enhance_image(image: Image.Image) -> Image.Image:
    """Preprocess image for better OCR accuracy."""
    image = image.convert("L")  # convert to grayscale
    image = image.filter(ImageFilter.MedianFilter())  # reduce noise
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2)  # increase contrast
    image = image.point(lambda x: 0 if x < 140 else 255)  # simple threshold
    return image


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/chat/")
async def chat(
    request: Request,
    message: str = Form(None),
    file: UploadFile = File(None)
):
    try:
        english_text = ""

        # 🖼️ If image uploaded
        if file:
            image_bytes = await file.read()
            image = Image.open(io.BytesIO(image_bytes))

            # Enhance image before OCR
            processed_image = enhance_image(image)

            # OCR to extract English text
            english_text = pytesseract.image_to_string(processed_image, lang="eng").strip()
            print("🧾 OCR Output:", english_text)  # Debugging

            if not english_text:
                return JSONResponse({"error": "No readable text found in the image."}, status_code=400)

            # Convert English letters to Telugu readable script (phonetic)
            telugu_readable = transliterate(english_text, ITRANS, TELUGU)

            return {
                "input_type": "image",
                "english_text": english_text,
                "telugu_readable": telugu_readable
            }

        # 💬 If text message sent
        elif message:
            english_text = message.strip()
            translation = translator.translate(english_text, src="en", dest="te")

            return {
                "input_type": "text",
                "english_text": english_text,
                "telugu_translation": translation.text
            }

        else:
            return JSONResponse({"error": "No input provided."}, status_code=400)

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
