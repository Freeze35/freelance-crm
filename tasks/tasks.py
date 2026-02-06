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

    # Функция для красивой группировки
    def format_section(tasks, title_emoji, section_name):
        if not tasks.exists():
            return ""

        section_text = f"{title_emoji} *{section_name}*\n"

        # Группируем задачи по проектам в словаре
        projects = {}
        for task in tasks:
            project_name = task.project.name if task.project else "Без проекта"
            if project_name not in projects:
                projects[project_name] = []
            projects[project_name].append(task)

        # Собираем текст из сгруппированных данных
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

