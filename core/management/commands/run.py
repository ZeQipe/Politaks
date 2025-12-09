"""
Django management command для запуска всех сервисов.

Использование:
    python manage.py run              # Django + микросервисы (в отдельных окнах для dev)
    python manage.py run --django     # Только Django
    python manage.py run --services   # Только микросервисы
    python manage.py run --no-window  # Всё в одном процессе (для Docker)
"""

import os
import sys
import signal
import subprocess
import platform
import time
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Запуск Django сервера и микросервисов'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.processes = []
        self.base_dir = Path(__file__).resolve().parent.parent.parent.parent

    def add_arguments(self, parser):
        parser.add_argument(
            '--django',
            action='store_true',
            help='Запустить только Django сервер',
        )
        parser.add_argument(
            '--services',
            action='store_true',
            help='Запустить только микросервисы',
        )
        parser.add_argument(
            '--no-window',
            action='store_true',
            help='Запустить всё в одном процессе (для Docker/CI)',
        )
        parser.add_argument(
            '--host',
            default='0.0.0.0',
            help='Хост для Django (по умолчанию: 0.0.0.0)',
        )
        parser.add_argument(
            '--port',
            default='8000',
            help='Порт для Django (по умолчанию: 8000)',
        )

    def handle(self, *args, **options):
        # Определяем окружение
        env_info = self._detect_environment()
        self.stdout.write(self.style.SUCCESS(f"🔍 Окружение: {env_info['name']}"))
        self.stdout.write(f"   Платформа: {env_info['platform']}")
        self.stdout.write(f"   Docker: {'Да' if env_info['is_docker'] else 'Нет'}")
        self.stdout.write("")

        # Определяем режим запуска
        run_django = not options['services']
        run_services = not options['django']
        use_windows = not options['no_window'] and not env_info['is_docker']

        # Регистрируем обработчик сигналов для корректного завершения
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        try:
            # Запускаем микросервисы
            if run_services:
                self._start_services(env_info, use_windows)
                if use_windows:
                    time.sleep(2)  # Даём время на запуск

            # Запускаем Django
            if run_django:
                self._start_django(options['host'], options['port'], env_info, use_windows)

        except KeyboardInterrupt:
            self._cleanup()
        except Exception as e:
            self._cleanup()
            raise CommandError(f"Ошибка запуска: {e}")

    def _detect_environment(self):
        """Определяем окружение запуска"""
        system = platform.system().lower()
        
        # Проверяем Docker
        is_docker = (
            os.path.exists('/.dockerenv') or
            os.environ.get('DOCKER_CONTAINER', False) or
            os.environ.get('KUBERNETES_SERVICE_HOST', False)
        )

        # Определяем платформу
        if system == 'windows':
            plat = 'windows'
            name = 'Windows'
        elif system == 'darwin':
            plat = 'macos'
            name = 'macOS'
        else:
            plat = 'linux'
            name = 'Linux'

        if is_docker:
            name = f'Docker ({name})'

        return {
            'platform': plat,
            'name': name,
            'is_docker': is_docker,
            'python': sys.executable,
        }

    def _start_services(self, env_info, use_windows):
        """Запуск микросервисов"""
        python = env_info['python']
        
        # Команды для микросервисов
        assistants_cmd = [python, str(self.base_dir / 'service' / 'assistants' / 'main.py')]
        sheets_cmd = [python, '-m', 'service.sheets.main']

        if use_windows:
            self._start_in_window('Assistants (7999)', assistants_cmd, env_info)
            self._start_in_window('Sheets (7998)', sheets_cmd, env_info)
        else:
            # Docker/CI режим — фоновые процессы
            self.stdout.write(self.style.WARNING("🚀 Запуск Assistants (порт 7999)..."))
            proc1 = subprocess.Popen(
                assistants_cmd,
                cwd=str(self.base_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            self.processes.append(('Assistants', proc1))

            self.stdout.write(self.style.WARNING("🚀 Запуск Sheets (порт 7998)..."))
            proc2 = subprocess.Popen(
                sheets_cmd,
                cwd=str(self.base_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            self.processes.append(('Sheets', proc2))

    def _start_in_window(self, title, cmd, env_info):
        """Запуск команды в новом окне терминала"""
        platform_type = env_info['platform']
        cmd_str = ' '.join(cmd)

        self.stdout.write(self.style.WARNING(f"🚀 Запуск {title} в новом окне..."))

        try:
            if platform_type == 'windows':
                # Windows: start cmd /k
                subprocess.Popen(
                    f'start "{title}" cmd /k "{cmd_str}"',
                    shell=True,
                    cwd=str(self.base_dir),
                )
            elif platform_type == 'macos':
                # macOS: osascript для Terminal.app
                script = f'''
                tell application "Terminal"
                    do script "cd {self.base_dir} && {cmd_str}"
                    activate
                end tell
                '''
                subprocess.Popen(['osascript', '-e', script])
            else:
                # Linux: пробуем разные терминалы
                terminals = [
                    ['gnome-terminal', '--', 'bash', '-c', f'cd {self.base_dir} && {cmd_str}; exec bash'],
                    ['konsole', '-e', 'bash', '-c', f'cd {self.base_dir} && {cmd_str}; exec bash'],
                    ['xfce4-terminal', '-e', f'bash -c "cd {self.base_dir} && {cmd_str}; exec bash"'],
                    ['xterm', '-e', f'bash -c "cd {self.base_dir} && {cmd_str}; exec bash"'],
                ]
                
                launched = False
                for term_cmd in terminals:
                    try:
                        subprocess.Popen(term_cmd, cwd=str(self.base_dir))
                        launched = True
                        break
                    except FileNotFoundError:
                        continue
                
                if not launched:
                    # Fallback: фоновый процесс
                    self.stdout.write(self.style.WARNING(
                        f"   ⚠️  Не найден терминал, запуск в фоне"
                    ))
                    proc = subprocess.Popen(
                        cmd,
                        cwd=str(self.base_dir),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                    )
                    self.processes.append((title, proc))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   ❌ Ошибка запуска {title}: {e}"))

    def _start_django(self, host, port, env_info, use_windows):
        """Запуск Django сервера"""
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"🌐 Запуск Django сервера на {host}:{port}"))
        self.stdout.write(self.style.SUCCESS("=" * 50))
        self.stdout.write("")

        # Django запускаем в текущем процессе
        try:
            call_command('runserver', f'{host}:{port}')
        except KeyboardInterrupt:
            pass

    def _signal_handler(self, signum, frame):
        """Обработчик сигналов для корректного завершения"""
        self.stdout.write("")
        self.stdout.write(self.style.WARNING("⚠️  Получен сигнал завершения..."))
        self._cleanup()
        sys.exit(0)

    def _cleanup(self):
        """Завершение дочерних процессов"""
        for name, proc in self.processes:
            try:
                self.stdout.write(f"   Завершение {name}...")
                proc.terminate()
                proc.wait(timeout=5)
            except Exception:
                proc.kill()
        self.processes.clear()

