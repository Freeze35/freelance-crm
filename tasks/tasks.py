import requests
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from celery import shared_task
from .models import Task


@shared_task
def send_telegram_notifications():
    now = timezone.now().date()
    tomorrow = now + timedelta(days=1)

    overdue = Task.objects.filter(deadline__lt=now).exclude(status='completed').select_related('project')
    upcoming = Task.objects.filter(deadline=tomorrow).exclude(status='completed').select_related('project')

    if not overdue.exists() and not upcoming.exists():
        return "No tasks to notify"

    message = "📊 *CRM REPORT* 📊\n"
    message += "—" * 15 + "\n\n"

    def format_section(tasks, title_emoji, section_name):
        if not tasks.exists():
            return ""

        section_text = f"{title_emoji} *{section_name}*\n"

        # Group tasks by projects in the dictionary
        projects = {}
        for task in tasks:
            project_name = task.project.name if task.project else "Без проекта"
            if project_name not in projects:
                projects[project_name] = []
            projects[project_name].append(task)

        # Collect text from grouped data
        for project, task_list in projects.items():
            section_text += f"\n📁 _Project: {project}_\n"
            for t in task_list:
                section_text += f" • {t.title} (`{t.deadline.strftime('%d.%m.%Y')}`)\n"

        return section_text + "\n"

    message += format_section(overdue, "🔴", "ПРОСРОЧЕНО")
    message += format_section(upcoming, "🟡", "КРАЙНИЙ СРОК ЗАВТРА")

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": settings.TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return "Success"
    except Exception as e:
        return f"Error: {str(e)}"

@shared_task
def send_telegram(chat_id: int | str, text: str = None, document_bytes: bytes = None, filename: str = None, caption: str = None):
    """
    Одна задача для всех отправок в Telegram:
    - text → отправляет сообщение
    - document_bytes → отправляет файл (PDF, фото и т.д.)
    """
    base_url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/"

    try:
        if document_bytes:
            url = base_url + "sendDocument"
            files = {'document': (filename or 'file.pdf', document_bytes, 'application/pdf')}
            data = {'chat_id': chat_id}
            if caption:
                data['caption'] = caption
                data['parse_mode'] = 'HTML'
            response = requests.post(url, data=data, files=files, timeout=15)
        else:
            url = base_url + "sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': text or 'Сообщение без текста',
                'parse_mode': 'HTML' if caption else 'Markdown'
            }
            response = requests.post(url, json=payload, timeout=10)

        response.raise_for_status()
        return "Отправлено успешно"

    except Exception as e:
        return f"Ошибка отправки: {str(e)}"