# Client Form Testing

This section documents the settings,view,forms,urls and models inside clients

# Projects: Database Models

Projects are the primary units of work in the CRM. Every project must be associated with a client and can contain multiple tasks and invoices.

## Project Entity

The `Project` model tracks the high-level progress of a freelance engagement. It defines the budget and the final deadline which affects task scheduling.

### Project Statuses
The status field helps filter the dashboard and identify active work:
* **New**: Project initialized, planning phase.
* **In Progress**: Active execution of tasks.
* **Done**: All deliverables met, ready for final invoicing.
* **Canceled**: Work stopped without completion.

## Forms
::: projects.forms
    options:
          show_root_heading: true
          show_source: true
          members_order: source

## Views
::: projects.views
    options:
      show_root_heading: true
      show_source: true
      members_order: source

## Models
::: projects.models
    options:
      show_root_heading: true
      show_source: true
      members_order: source

## Endpoint Overview

| URL Pattern | Name | View Function | Description |
| :--- | :--- | :--- | :--- |
| `/projects/` | `list` | `project_list` | Dashboard of all active and archived projects |
| `/projects/add/` | `create` | `project_create` | Wizard for initializing a new project |
| `/projects/<pk>/` | `detail` | `project_detail` | In-depth view of project progress, tasks, and billing |
| `/projects/<pk>/update/` | `update` | `project_update` | Modify project scope, budget, or deadlines |
| `/projects/<pk>/delete/` | `delete` | `project_delete` | Remove a project and its associated data |
| `/projects/overdue/` | `overdue_tasks` | `overdue_tasks` | **Global Monitor**: View all overdue tasks across all projects |