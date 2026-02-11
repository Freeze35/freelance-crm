# Client Form Testing

This section documents the view,forms,urls and models inside clients

## Forms
::: clients.forms
    options:
          show_root_heading: true
          show_source: true
          members_order: source

## Models
::: clients.models
    options:
      show_root_heading: true
      show_source: true
      members_order: source

## Views
::: clients.views
    options:
      show_root_heading: true
      show_source: true
      members_order: source

## Endpoint Overview

| URL Pattern | Name | View Function | Description |
| :--- | :--- | :--- | :--- |
| `/clients/` | `list` | `client_list` | Display all clients |
| `/clients/add/` | `create` | `client_create` | Add a new client |
| `/clients/<pk>/` | `detail` | `client_detail` | View specific client details |
| `/clients/<pk>/update/` | `update` | `client_update` | Edit client information |
| `/clients/<pk>/delete/` | `delete` | `client_delete` | Remove a client record |