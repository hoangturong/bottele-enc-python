import telebot
import base64
import subprocess
import os
import time

bot = telebot.TeleBot('6348531467:AAExVAa-ycfy06fiGmT-hpQqn-E5-d4n8fQ')

@bot.message_handler(content_types=['document'])
def handle_document(message):
    try:
        file_info = bot.get_file(message.document.file_id)
        file_name = message.document.file_name

        downloaded_file = bot.download_file(file_info.file_path)

        # Tạo tên tệp tạm thời duy nhất dựa trên thời gian
        temp_file_path = f"temp_{int(time.time())}_{file_name}"
        with open(temp_file_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        bot.send_message(message.chat.id, "Nhập mật khẩu:")

        # Lưu thông tin tệp tạm thời vào session để truy cập được từ hàm xử lý mật khẩu
        bot.register_next_step_handler(message, get_password, temp_file_path)

    except Exception as e:
        bot.reply_to(message, f"Có lỗi xảy ra: {e}")

def get_password(message, temp_file_path):
    if message.text:
        try:
            with open(temp_file_path, 'r', encoding='latin1') as file:
                python_code = file.read()

            encoded_bytes = base64.b64encode(python_code.encode('utf-8'))
            encoded_code = encoded_bytes.decode('utf-8')
            encoded_code_with_password = f"""
import base64
password = "{message.text}"
if input("Enter password: ") != password:
    print("Incorrect password.")
    exit()
encoded_string = '{encoded_code}'
decoded_bytes = base64.b64decode(encoded_string)
decoded_string = decoded_bytes.decode('utf-8')
exec(decoded_string)
"""

            output_file_path = f"output_{int(time.time())}.py"  # Tạo tên tệp đầu ra duy nhất
            with open(output_file_path, 'w', encoding='utf-8') as output:
                output.write(encoded_code_with_password)

            subprocess.run(["python", "enc.py"])

            with open(output_file_path, 'rb') as enc_file:
                bot.send_document(message.chat.id, enc_file)

            bot.reply_to(message, "FILE ĐÃ MÃ HOÁ CỦA BẠN.")

            # Xóa tệp tạm thời và tệp đầu ra
            os.remove(temp_file_path)
            os.remove(output_file_path)

        except Exception as e:
            bot.reply_to(message, f"Có lỗi xảy ra: {e}")

bot.polling()
