import io
import random
import string
import base64
from flask import Flask, render_template_string, request, session
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)
# Секретный ключ нужен для работы сессий (хранения правильного ответа)
app.secret_key = "super_secret_key_123"


def create_captcha():
    """Генерирует текст капчи и возвращает её изображение в формате Base64"""
    text = "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
    session["captcha_text"] = text  # Сохраняем правильный ответ в сессию

    # Создание изображения
    width, height = 180, 60
    image = Image.new("RGB", (width, height), color=(240, 240, 240))
    draw = ImageDraw.Draw(image)

    # Добавление шума (линии)
    for _ in range(10):
        draw.line(
            [
                (random.randint(0, width), random.randint(0, height)),
                (random.randint(0, width), random.randint(0, height)),
            ],
            fill=(180, 180, 180),
            width=2,
        )

    # Отрисовка текста
    try:
        font = ImageFont.truetype("arial.ttf", 36)
    except IOError:
        font = ImageFont.load_default()

    draw.text((30, 10), text, fill=(50, 50, 50), font=font)

    # Конвертация изображения в строку Base64 для HTML
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format="PNG")
    img_byte_arr = img_byte_arr.getvalue()
    return base64.b64encode(img_byte_arr).decode("utf-8")


# HTML-шаблон страницы с кликабельной подписью
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Проверка капчи</title>
    <style>
        body { font-family: Arial, sans-serif; display: flex; justify-content: center; align-content: center; height: 100vh; margin-top: 10%; background: #f5f5f5; }
        .captcha-box { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; position: relative; }
        .message { font-weight: bold; margin-bottom: 15px; padding: 8px; border-radius: 4px; }
        .success { color: #155724; background: #d4edda; }
        .error { color: #721c24; background: #f8d7da; }
        input[type="text"] { padding: 10px; font-size: 16px; width: 150px; text-transform: uppercase; margin-top: 10px; }
        button { padding: 10px 20px; font-size: 16px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #0056b3; }
        .powered-by { font-size: 11px; color: #888; margin-top: 20px; font-style: italic; }
        .powered-by a { color: #007bff; text-decoration: none; }
        .powered-by a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="captcha-box">
        <h2>Введите код с картинки</h2>
        
        {% if message %}
            <div class="message {{ 'success' if is_correct else 'error' }}">{{ message }}</div>
        {% endif %}

        <img src="data:image/png;base64,{{ captcha_img }}" alt="Капча"><br>
        
        <form method="POST">
            <input type="text" name="user_input" placeholder="Код здесь" autocomplete="off" required><br><br>
            <button type="submit">Проверить</button>
        </form>

        <div class="powered-by">Powered by <a href="https://github.com/MaxonchikDev/crona-captcha/tree/main" target="_blank" rel="noopener noreferrer">Crona Captcha</a></div>
    </div>
</body>
</html>
"""



@app.route("/", methods=["GET", "POST"])
def index():
    message = None
    is_correct = False

    if request.method == "POST":
        user_input = request.form.get("user_input", "").strip().upper()
        correct_text = session.get("captcha_text", "")

        if user_input == correct_text:
            message = "🎉 Капча пройдена успешно!"
            is_correct = True
        else:
            message = "❌ Неверный код. Попробуйте еще раз."

    # Генерируем новую капчу для следующего отображения
    captcha_img = create_captcha()
    return render_template_string(
        HTML_TEMPLATE,
        captcha_img=captcha_img,
        message=message,
        is_correct=is_correct,
    )


if __name__ == "__main__":
    app.run(debug=True)
