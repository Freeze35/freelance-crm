import requests
from django.conf import settings
from django.utils import timezone
from datetime import timedelta, date
from celery import shared_task
from .models import Task
from django.db.models import QuerySet
from typing import Dict, List, Optional, Union, Any


@shared_task
def send_telegram_notifications() -> str:
    """Identify overdue and upcoming tasks and send a summary report to Telegram."""
    now: date = timezone.now().date()
    tomorrow: date = now + timedelta(days=1)

    # Note: Using 'completed' instead of 'done' based on your provided task logic
    overdue: QuerySet[Task] = Task.objects.filter(deadline__lt=now).exclude(status='completed').select_related(
        'project')
    upcoming: QuerySet[Task] = Task.objects.filter(deadline=tomorrow).exclude(status='completed').select_related(
        'project')

    if not overdue.exists() and not upcoming.exists():
        return "No tasks to notify"

    message: str = "📊 *CRM REPORT* 📊\n"
    message += "—" * 15 + "\n\n"

    def format_section(tasks: QuerySet[Task], title_emoji: str, section_name: str) -> str:
        """Helper to group tasks by project and format the text section."""
        if not tasks.exists():
            return ""

        section_text: str = f"{title_emoji} *{section_name}*\n"

        # Group tasks by projects
        projects_map: Dict[str, List[Task]] = {}
        for task in tasks:
            project_name: str = task.project.name if task.project else "Без проекта"
            if project_name not in projects_map:
                projects_map[project_name] = []
            projects_map[project_name].append(task)

        # Build formatted text from mapping
        for project, task_list in projects_map.items():
            section_text += f"\n📁 _Project: {project}_\n"
            for t in task_list:
                deadline_str: str = t.deadline.strftime('%d.%m.%Y') if t.deadline else "No deadline"
                section_text += f" • {t.title} (`{deadline_str}`)\n"

        return section_text + "\n"

    message += format_section(overdue, "🔴", "ПРОСРОЧЕНО")
    message += format_section(upcoming, "🟡", "КРАЙНИЙ СРОК ЗАВТРА")

    url: str = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload: Dict[str, Any] = {
        "chat_id": settings.TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        response: requests.Response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return "Success"
    except Exception as e:
        return f"Error: {str(e)}"


@shared_task
def send_telegram(
        chat_id: Union[int, str],
        text: Optional[str] = None,
        document_bytes: Optional[bytes] = None,
        filename: Optional[str] = None,
        caption: Optional[str] = None
) -> str:
    """
    Unified task for Telegram messaging:
    - Sends text messages via sendMessage
    - Sends files (PDF, images) via sendDocument
    """
    base_url: str = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/"

    try:
        if document_bytes:
            url: str = base_url + "sendDocument"
            files: Dict[str, Any] = {
                'document': (filename or 'file.pdf', document_bytes, 'application/pdf')
            }
            data: Dict[str, Any] = {'chat_id': chat_id}
            if caption:
                data['caption'] = caption
                # Using HTML for caption if explicitly requested via structure
                data['parse_mode'] = 'HTML'

            response: requests.Response = requests.post(url, data=data, files=files, timeout=15)
        else:
            url = base_url + "sendMessage"
            payload: Dict[str, Any] = {
                'chat_id': chat_id,
                'text': text or 'Сообщение без текста',
                'parse_mode': 'HTML' if caption else 'Markdown'
            }
            response = requests.post(url, json=payload, timeout=10)

        response.raise_for_status()
        return "Отправлено успешно"

    except Exception as e:
        return f"Ошибка отправки: {str(e)}"