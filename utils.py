def read_txt_file(file_path: str):
    # Open the file in read mode
    with open(file_path, "r") as file:
        # Read the content of the file
        content = file.read()

    return content
