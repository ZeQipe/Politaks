"""
Views для раздачи фронтенда (Next.js build)
"""
import os
import mimetypes
from django.http import HttpResponse, Http404, FileResponse
from django.conf import settings
from django.views.decorators.cache import cache_control


def serve_frontend(request, path=''):
    """
    Раздача статических файлов фронтенда
    """
    client_dir = settings.CLIENT_DIR
    
    # Если путь пустой - отдаём index.html
    if not path or path == '/':
        file_path = client_dir / 'index.html'
    else:
        # Убираем начальный слэш если есть
        path = path.lstrip('/')
        file_path = client_dir / path
    
    # Проверяем существование файла
    if file_path.exists() and file_path.is_file():
        return _serve_file(file_path)
    
    # Если файл не найден, пробуем добавить .html
    html_path = client_dir / f"{path}.html"
    if html_path.exists() and html_path.is_file():
        return _serve_file(html_path)
    
    # Если это директория, ищем index.html внутри
    if file_path.exists() and file_path.is_dir():
        index_path = file_path / 'index.html'
        if index_path.exists():
            return _serve_file(index_path)
    
    # Для SPA - отдаём index.html для всех несуществующих путей
    # Но только если это не запрос к _next или api
    if not path.startswith('_next') and not path.startswith('api'):
        index_path = client_dir / 'index.html'
        if index_path.exists():
            return _serve_file(index_path)
    
    # 404
    not_found_path = client_dir / '404.html'
    if not_found_path.exists():
        response = _serve_file(not_found_path)
        response.status_code = 404
        return response
    
    raise Http404("Страница не найдена")


@cache_control(max_age=31536000, immutable=True)
def serve_next_static(request, path):
    """
    Раздача статических файлов _next с кешированием
    """
    client_dir = settings.CLIENT_DIR
    file_path = client_dir / '_next' / path
    
    if file_path.exists() and file_path.is_file():
        return _serve_file(file_path)
    
    raise Http404("Файл не найден")


def _serve_file(file_path):
    """
    Отдача файла с правильным Content-Type
    """
    content_type, _ = mimetypes.guess_type(str(file_path))
    
    if content_type is None:
        content_type = 'application/octet-stream'
    
    # Для HTML файлов
    if content_type == 'text/html':
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return HttpResponse(content, content_type='text/html; charset=utf-8')
    
    # Для остальных файлов используем FileResponse
    return FileResponse(open(file_path, 'rb'), content_type=content_type)

