wagtail_admin_files
===================

Easily share files through the wagtail admin, only for admins.

Useful for easily grouping files submitted through a contact form, or files bound to another model.

`SharedFile` object creation can either:

1. Create a copy of the actual file contents in the backend.
2. Store the path to a file which already exists in a backend.

Quick start
-----------

1. Install the package via pip:

   ```bash
   pip install wagtail_admin_files
   ```
2. Add 'wagtail_admin_files' to your INSTALLED_APPS setting like this:

   ```
   INSTALLED_APPS = [
   ...,
      'wagtail_admin_files',
   ]
   ```
3. Add the following header to your `settings.py`

   ```python
   X_FRAME_OPTIONS = "SAMEORIGIN"
   ```

A settings menu item will be automatically registered.

The `WAGTAIL_ADMIN_FILES_MENU_HOOK` setting can be set to register the menu item to a different menu.

By default, the hook it registers to is `register_settings_menu_item`

## Public Views

Public views are available, but can be disabled by setting `WAGTAIL_ADMIN_FILES_ALLOW_PUBLIC` to `False` in `settings.py`.

In this case, the admin will take over, all public views will return a 404 status code.

The public views extend `base.html` by default, this can be overridden by setting `WAGTAIL_ADMIN_FILES_TEMPLATE_EXTENDS` in `settings.py` to point to a different file.

The public views use the generic `{% block content %}...{% endblock content %}` in order to override the content block of the above mentioned ``WAGTAIL_ADMIN_FILES_TEMPLATE_EXTENDS`` file.
