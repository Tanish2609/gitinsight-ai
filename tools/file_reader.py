from pathlib import Path


def read_file(file_path: Path) -> str:
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as file:

            content = file.read()

            if not content.strip():
                return "Empty File"

            return content

    except FileNotFoundError:
        return f"File Not Found : {file_path}"

    except PermissionError:
        return f"Permission Denied : {file_path}"

    except Exception as e:
        return f"Error Reading File : {str(e)}"


