from flask import Flask, request, send_file
from rembg import remove
import io
import os

app = Flask(__name__)

@app.route('/', methods=['POST'])
def remove_watermark():
    try:
        # Получаем фото от бота
        file = request.files['image']
        img_bytes = file.read()
        
        # Удаляем фон/водяной знак
        result = remove(img_bytes)
        
        # Отправляем обратно
        return send_file(
            io.BytesIO(result),
            mimetype='image/png',
            as_attachment=True,
            download_name='clean_image.png'
        )
    except Exception as e:
        print(f"Ошибка: {e}")
        return f"Ошибка: {str(e)}", 500

if __name__ == '__main__':
    print("✅ Сервер запущен! Жду фото от Робочата...")
    app.run(host='0.0.0.0', port=5000)