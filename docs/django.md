# Django

1. Django is a Python-based web framework. It follows a model-template-view pattern.

2. core/templates/ holds the main meat of the HTML.
   - base.html holds the pieces that are constant across all pages (mainly stylesheet references right now).
   - index.html is the home page which presents as a login page.
   - register.html is where the account creation form lives.
   - dashboard.html is the homepage for users that are logged in.
   - We can add as many pages as we want, as long as we setup the routing so Django can do something with them.

3. Stylesheets
   - I decided to use [Bootstrap](https://github.com/twbs/bootstrap) stylesheets, which look very nice out of the box.
   - I have also written some manual CSS overrides to reflect our latest "branding". We can override Bootstrap as much or as little as we want. Overrides live in `core/static/core/css/custom.css`
   - I also imported fonts from [Google Fonts](https://fonts.google.com/) to ensure the look is consistent across devices.
   - You can see the Bootstrap and Google Font references in `core/templates/base.html`.
   - Remember to include `{ % extends "base.html" %}` on any new pages to pick up the stylesheet references
