# Client Form Testing

This section documents the settings,view,forms,urls and models inside tasks

## TaskForm Overview

The `TaskForm` handles the input validation and styling for individual tasks. It is optimized for clarity, using placeholders to guide the user.

### UI Enhancements
* **Visual Consistency**: Inherits the `common_classes` (blue borders and rounded corners) used throughout the CRM.
* **Contextual Helpers**: Includes placeholders like *"Что нужно сделать?"* to improve accessibility.
* **Native Date Picker**: The `deadline` field uses `type='date'`, ensuring cross-browser compatibility for selecting dates.

### Layout Integration
This form is typically rendered within a modal or a dedicated project view, utilizing **Django-HTMX** for asynchronous submission where applicable.

## Forms
::: tasks.forms
    options:
          show_root_heading: true
          show_source: true
          members_order: source

## Views
::: tasks.views
    options:
      show_root_heading: true
      show_source: true
      members_order: source

## Models
::: tasks.models
    options:
      show_root_heading: true
      show_source: true
      members_order: source

## Tasks
::: tasks.tasks
    options:
      show_root_heading: true
      show_source: true
      members_order: source

## Endpoint Overview

| URL Pattern | Name | View Function | Description |
| :--- | :--- | :--- | :--- |
| `projects/<int:project_id>/tasks/add/` | `create` | `task_create` | Initializes a new task for the specified project |
| `tasks/<int:pk>/` | `detail` | `task_detail` | Detailed view of task description, status, and deadline |
| `tasks/<int:pk>/update/` | `update` | `task_update` | Edit task priority, status, or due date |
| `tasks/<int:pk>/delete/` | `delete` | `task_delete` | Permanently remove a task record |