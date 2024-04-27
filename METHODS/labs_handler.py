from pyrogram import filters
import os
from time import sleep
# from DATABASE import tdatabase,pgdatabase
import os
from DATABASE import tdatabase
from Buttons import buttons


PDF_MESSAGE = f"""
```PDF STATUS
STATUS : Receiving
```
"""


async def download_pdf(bot, message):
    chat_id = message.chat.id
    download_folder = "pdfs"
    # Checks the Status
    status = await tdatabase.fetch_pdf_status(chat_id)
    # If the status is recieve then only it recieves the pdf.
    if status[0] == "Recieve":
        # Checks if the message is document or not.
        if message.document:
            mime_type = message.document.mime_type
            if mime_type == "application/pdf":
                # If download_folder does not exist then it creates a directory
                if not os.path.exists(download_folder):
                    os.makedirs(download_folder)
                # Message Receiving the PDF.
                message_in_receive = await bot.send_message(chat_id,PDF_MESSAGE)
                # Download the PDF file with progress callback
                await message.download(
                    file_name=os.path.join(download_folder, f"C-{chat_id}.pdf"),
                )
                # Send a completion message
                RECEIVED_PDF_MSG = f"""
```PDF STATUS
STATUS : Received.

PDF SIZE : Checking.
```
"""
                # Message After Receiving the PDF.
                message_after_recieve = await bot.edit_message_text(chat_id,message_in_receive.id, RECEIVED_PDF_MSG)
                # check_pdf_size returns 2 values whether the pdf is above 1mb or not and size of pdf
                check ,size = await check_pdf_size(chat_id)
                if check is True:
                    PDF_ABOVE_1MB_DELETED = f"""
```PDF STATUS
STATUS : Received.

PDF SIZE : {size} MB.

The PDF file exceeds the allowable size limit of 1MB and has been deleted.

Please resend a PDF file that is under 1MB.

```
"""
                    PDF_ABOVE_1MB_ERROR_DELETE = f"""
```PDF STATUS
STATUS : Received.

PDF SIZE : {size} MB.

The PDF file exceeds the allowable size limit of 1MB.

Error Deleting the PDF.

Please resend a PDF file that is under 1MB.

```
"""
                    if await remove_pdf_file(bot,chat_id) is True:
                        await bot.edit_message_text(
                            chat_id,
                            message_after_recieve.id,
                            PDF_ABOVE_1MB_DELETED)
                    else:
                        await bot.edit_message_text(
                            chat_id,
                            message_after_recieve.id,
                            PDF_ABOVE_1MB_ERROR_DELETE)
                    
                else:
                    LESS_THAN_1_MB = f"""
```PDF STATUS
STATUS : Received.

PDF SIZE : {size} MB.

```                    
"""
                    # Remove the Status of pdf.
                    await tdatabase.delete_pdf_status_info(chat_id)   
                    await bot.edit_message_text(chat_id,message_after_recieve.id,LESS_THAN_1_MB)
            else:
                await bot.send_message(chat_id, "This File type is not supported.")


async def check_pdf_size(chat_id):
        """This Function checks whether the pdf file is above 1 mb o not,
        If the file is above 1mb then it returns true and the file size ."""
        file_size= os.path.getsize(os.path.abspath(f"pdfs/C-{chat_id}.pdf"))
        file_size_mb = round((file_size/(1024*1024)),3)
        if file_size_mb > 1:
            return True, file_size_mb
        else:
            return False, file_size_mb
        
async def get_title_from_user(bot, message):
    """This Function Gets the title from the message that user has sent."""
    chat_id = message.chat.id
    # Checks the status
    status = await tdatabase.fetch_title_status(chat_id)
    # if the status is recieve then only it receives the text.
    if status[0] == "Recieve":
        messages = message.text
        chat_id = message.chat.id
        if "TITLE" in messages.upper() and ":" in messages.upper():
            parts = messages.split(":")
            # Extract the title part (excluding "TITLE" if present)
            title = parts[-1].strip()
            if title:
                await bot.send_message(chat_id,f"The title you provided is :\n{title}")
                # Stores the title in temporary labupload database.
                await tdatabase.store_title(chat_id,title=title)
                # Deletes the Status so that next title cannot be sent again directly.
                await tdatabase.delete_title_status_info(chat_id)

async def remove_pdf_file(bot,chat_id):
    """This function retreive the file is present or not and compressed or not from the check_recieved_pdf_file function,
    Based on that result it deletes the pdf file"""
    pdf_folder = "pdfs"
    check_present , check_compress = await check_recieved_pdf_file(bot,chat_id)
    if check_present and check_compress:
        pdf_location = os.path.join(pdf_folder, f"C-{chat_id}-comp.pdf")
    elif check_present and not check_compress:
        pdf_location = os.path.join(pdf_folder, f"C-{chat_id}.pdf")
    else:
        # If neither present nor compress, no action needed
        return False

    pdf_location_path = os.path.abspath(pdf_location)
    
    try:
        os.remove(pdf_location_path)
        return True
    except OSError as e:
        await bot.send_message(chat_id,f"Error deleting pdf : {e}")
        return False

async def check_recieved_pdf_file(bot,chat_id):
    """This Function Can be used to check whether the file is present or not,
    and Whether the current pdf file is compressed or not."""
    pdf_folder = "pdfs"
    pdf_folder = os.path.abspath(pdf_folder)
    file_name = f"C-{chat_id}.pdf"
    file_name_compressed = f"C-{chat_id}-comp.pdf"
    # Checks if the directory is present or not
    try:
        all_pdf_files = os.listdir(pdf_folder)
    except:
        return False,None
    try:
        # Checks if the Normal pdf is present in the directory and returns
        # indicating it as uncompressed file
        if file_name in all_pdf_files:
            return True, False
        elif file_name_compressed in all_pdf_files:
            return True, True
        else:
            return False, None
    except Exception as e:
        await bot.send_message(chat_id,f"There is an error finding pdf : {e}")


