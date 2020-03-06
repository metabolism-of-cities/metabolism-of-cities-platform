# Metabolism of Cities Style Guide

In principle we adopt the Google Style Guides for our projects (see https://github.com/google/styleguide). In particular, the Python, HTML/CSS, and Javascript style guides apply:

- Python: https://google.github.io/styleguide/pyguide.html
- HTML/CSS: https://google.github.io/styleguide/htmlcssguide.html
- Javascript: https://google.github.io/styleguide/jsguide.html

There may be reasons to define expections to these rules that apply to our projects. If these exist, please define them below and ensure they are substantiated. 

## Exceptions

There are currently no exceptions to the aforementioned style guides.

## Libraries

We may use a variety of external libraries or other files, for example javascript libraries, web fonts, or external CSS stylesheets. Please see LIBRARIES.md for more information.

## Coding templates

We provide a set of templates for any developer to use when adding or editing pages within Metabolism of Cities. These templates make it easy to re-use existing code, and to kickstart work. We recommend new contributors to check out our templates at: http://localhost:8000/templates/

## File naming conventions and locations

Let's define how files should be named and where they should be saved.

## Git 

We should define a workflow.
https://nvie.com/posts/a-successful-git-branching-model/ ?
Maybe a slightly simplified version of that.

## Front-end guidelines

This is a list of front-end specific guidelines. Please keep in mind that as the project progresses, some guidelines will be added to the list, some will change, and perhaps a few will be removed.

However, a few general rules will always apply:

- Be consistent. Use the defined variables and helper classes whenever they're applicable. Don't add arbitrary padding or margins, don't give objects colours that aren't defined already, etc. 
- Ensure responsiveness. Whatever you make, make sure it works well on phones, tablets, laptop screens, and external monitors.

### Colours

The primary and secondary colours are set, but are subject to change. A few useful shades of black are defined and those should be used using their variable names rather than creating new shades. It's possible more are needed in the future.

### Fonts

The global typeface at the moment is Lato. This will probably stay this way unless there are objections from the client. This typeface is used throught the website. At the moment there are no exceptions.

### Margin and padding

Bootstrap has built-in helpers to make adding margins and padding easier (https://getbootstrap.com/docs/4.4/utilities/spacing/). This early into the project it's difficult to know what will work best. Sometimes it's useful to use these, other times it makes more sense to add a custom amount of margin and padding.

### Shadows

A shadow extend exists for when hovering over an item. So far these are only used for thumbnail buttons but might be useful in the future. 

### HTML elements

Whenever applicable, please make use of relevant HTML elements such as `article`, `aside`, and `section`. See https://developer.mozilla.org/en-US/docs/Web/HTML for a full list. Using these consistently and appropriately saves time and effort while at the same time make things easier for search engines and screen readers.
