# Metabolism of Cities Style Guide

In principle we adopt the Google Style Guides for our projects (see https://github.com/google/styleguide). In particular, the Python, HTML/CSS, and Javascript style guides apply:

- Python: https://google.github.io/styleguide/pyguide.html
- HTML/CSS: https://google.github.io/styleguide/htmlcssguide.html
- Javascript: https://google.github.io/styleguide/jsguide.html

There may be reasons to define expections to these rules that apply to our projects. If these exist, please define them below and ensure they are substantiated. 

## Exceptions

There are currently no exceptions to the aforementioned style guides.

## External Libraries

We may use a variety of external libraries or other files, for example javascript libraries, web fonts, or external CSS stylesheets. Please take into account the following considerations when loading external libraries:

- Every different external domain adds a new dependency and thus risk factor to the site (i.e. if this external website is down, we may lose key functionality of our own website). We should therefore try to limit the number of different, remote sites that we use.
- Open source libraries and files that are part of the XXX CND (let's define a big one here) can be included from this CDN. 
- Other files should be downloaded to our own project and included locally instead.
- It is very easy to lose track of which libraries we use, and what we use them for. We therefore keep track of all our libraries in a central location (see LIBRARIES.md). When considering using a new library, please check if nothing similar has not already been used and where possible re-use this instead.

## Coding templates

We provide a set of templates for any developer to use when adding or editing pages within Metabolism of Cities. These templates make it easy to re-use existing code, and to kickstart work. We recommend new contributors to check out our templates at: XXXXXXX

## File naming conventions and locations

Let's define how files should be named and where they should be saved.

## Git 

We should define a workflow.
https://nvie.com/posts/a-successful-git-branching-model/ ?
Maybe a slightly simplified version of that.
