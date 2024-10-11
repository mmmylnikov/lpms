from django.templatetags.static import static


def run(*args: str) -> None:
    if len(args) < 1:
        print("Usage: python manage.py runscript get_url_static_file --script-args <file_name>")
        return
    file_name = args[0]
    url = static(file_name)
    print(url)
