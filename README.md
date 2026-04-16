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
