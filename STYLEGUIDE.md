# Metabolism of Cities Style Guide

In principle we adopt the Google Style Guides for our projects (see https://github.com/google/styleguide). In particular, the Python, HTML/CSS, and Javascript style guides apply:

- Python: https://google.github.io/styleguide/pyguide.html
- HTML/CSS: https://google.github.io/styleguide/htmlcssguide.html
- Javascript: https://google.github.io/styleguide/jsguide.html

There may be reasons to define expections to these rules that apply to our projects. If these exist, please define them below and ensure they are substantiated. 

## Exceptions

### HTML

- Please keep using the optional tags as described in 3.1.7 (https://google.github.io/styleguide/htmlcssguide.html#Optional_Tags). Technically it's not necessary to, for example, close `<p>` tags. However, as already mentioned in the styleguide documents, this is "significantly different from what web developers are typically taught". The stated benefits are "file size optimization and scannability", but I don't think these really apply for this project.

### CSS

- Please use double quotation marks ("") instead of single ('') as suggested in section 4.2.8 (https://google.github.io/styleguide/htmlcssguide.html#CSS_Quotation_Marks). I think it makes sense being consistent throughout all of our code.

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

## Comments

Help out others and your future self by adding concise, useful comments. This includes explanations of what parts of code are for, how it interacts with other code, links to relevant documentation, links that have helped you write the code, etc.

This is not a complete list. Use your own judgement, but remember that it's possible others will be reading your code without prior knowledge of the project, the libraries you used, or your intentions. Also keep in mind that you will absolutely forget things you have written. Copy-pasting the URL of a relevant StackOverflow answer you used to solve a problem takes 3 seconds. Finding that specific answer again in the future can take an hour. Write comments to help yourself as much as others.

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

## Back-end guidelines

This project contains lots of moving pieces and it is daunting to grasp for new contributors. We therefore value *simplicity* and *consistency*. Use the following conventions to make things easier.

### Database queries and looping

When querying the database, use the following naming conventions for the variables:

*list* = when you except various records
You use this name when there is one "main" model that you interact with. 

Example: you are viewing the page with all the projects.

list = Project.objects.all()

--------------

*name of model in plural* = when you expect various records, but this is NOT the only model you interact with

Example: you are viewing an article, and on the side you want to show relevant news and events

events = Event.objects.all()[:10]
news = News.objects.all()[:10]

--------------

*info* = when querying a single principal record

Example: you want to retrieve the current video the user is viewing

info = Video.objects.get(pk=id)

--------------

*context* = used to pass variables from your views to your templates. This is a dictionary. You have two ways of constructing this: you can either define the variables earlier on and then reference them (if you do, use the same names in the dictionary), or you can define each item in the actual dictionary. As a general guideline, if a query if very simple and there is no additional code required (no conditions, etc), then do it straight in the dictionary. If not, define first.

Define it first:

if id:
  info = Video.objects.get(pk=id)
  events = None
  news = None
else:
  info = Video.objects.filter(active=True)[0]
  events = Event.objects.all()
  news = News.objects.all()

context = { 
  "info": info,
  "events": events,
  "news": news,
}

Define it straight in the context:

context = {
  "info": Photo.objects.get(pk=id),
  "list": Photo.objects.all(),
}

-------------

When looping through a list, please use these keywords:

Use *each* when looping through a queryset:

for each in list:
  print(each.id)
