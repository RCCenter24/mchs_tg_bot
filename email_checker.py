from icecream import ic
import asyncio
from email import message_from_bytes
from email.header import decode_header
import imaplib
import os

from config import EMAIL, PASSWORD, SAVE_DIR


async def fetch_and_save_files():
    email_id = None
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

    async def decode_file_name(encoded_name):
        d_header = decode_header(encoded_name)[0]
        if isinstance(d_header[0], bytes):
            return d_header[0].decode(d_header[1] or 'utf-8')
        return d_header[0]

    async def save_file(part, filename):
        filepath = os.path.join(SAVE_DIR, filename)
        # Открытие файла в отдельном потоке
        await asyncio.to_thread(lambda: open(filepath, 'wb').write(part.get_payload(decode=True)))
        return filepath

    async def extract_content(email_message):
        mail_content = ""
        for part in email_message.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            if "attachment" not in content_disposition and content_type == "text/plain":
                mail_content += part.get_payload(decode=True).decode()
        return mail_content

    mail = imaplib.IMAP4_SSL('imap.rambler.ru')
    await asyncio.to_thread(mail.login, EMAIL, PASSWORD)
    await asyncio.to_thread(mail.select, 'inbox')

    result, data = await asyncio.to_thread(mail.search, None, 'ALL')
    email_nums = data[0].split()

    saved_files = []
    subject = None
    content = None

    # Извлекаем данные из последнего email
    num = email_nums[-1]
    result, email_data = await asyncio.to_thread(mail.fetch, num, '(RFC822)')
    raw_email = email_data[0][1]
    msg = message_from_bytes(raw_email)

    subject_header = msg["Subject"]
    if subject_header is not None:
        decoded_subject = decode_header(subject_header)[0][0]
        subject = decoded_subject.decode() if isinstance(decoded_subject, bytes) else decoded_subject
    else:
        subject = ""
    content = await extract_content(msg)  # Асинхронный вызов

    global global_email_id
    email_id = msg["Message-ID"]
    
    global_email_id = email_id

    if msg.is_multipart():
        text_part_found = False
        for part in msg.walk():
            print(f"Processing part with Content-Type: {part.get_content_type()}")

            content_type = part.get_content_type()
            content_disposition = part.get("Content-Disposition")
            if content_disposition and "attachment" in content_disposition:
                filename = part.get_filename()
                if filename:
                    print(f"Found attachment: {filename}")
                    filename = await decode_file_name(filename)  # Асинхронный вызов
                    print(f"Decoded filename: {filename}")
                    filepath = os.path.join(SAVE_DIR, filename)
                    print(f"File path: {filepath}")
                    await save_file(part, filename)  # Асинхронный вызов

                    saved_files.append(filepath)
                    print(f"Processing attachment: {filename}")
            elif not text_part_found and content_type in ['text/plain', 'text/html']:
                if content_disposition is None or "attachment" not in content_disposition:
                    print("Extracting text content")
                    content = part.get_payload(decode=True).decode()
                    text_part_found = True

    await asyncio.to_thread(mail.logout)
    ic(email_id)
    return saved_files, subject, content, email_id