def send_message(username: str, text: str):
    message = Message(username=username, text=text, timestamp=datetime.now(), read_by=[])
    db.add_message(message)
    return message

def get_messages():
    return db.get_messages()

def add_emoticon(name: str, url: str, size: str, animated: bool):
    emoticon = Emoticon(name=name, url=url, size=size, animated=animated)
    db.add_emoticon(emoticon)
    return emoticon

def get_emoticons():
    return db.get_emoticons()

def upload_file(filename: str, url: str, edited_by: List[str]):
    file = File(filename=filename, url=url, version=1, uploaded_at=datetime.now(), edited_by=edited_by)
    db.add_file(file)
    return file

def update_file_version(filename: str, edited_by: List[str]):
    files = db.get_files()
    for file in files:
        if file.filename == filename:
            new_version = file.version + 1
            updated_file = File(
                filename=file.filename,
                url=file.url,
                version=new_version,
                uploaded_at=datetime.now(),
                edited_by=edited_by
            )
            db.update_file(updated_file)
            return updated_file
    return None
