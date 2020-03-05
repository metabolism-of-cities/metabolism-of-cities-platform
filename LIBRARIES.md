# Libraries

We may use a variety of external libraries or other files, for example javascript libraries, web fonts, or external CSS stylesheets. Please take into account the following considerations when loading external libraries:

- Every different external domain adds a new dependency and thus risk factor to the site (i.e. if this external website is down, we may lose key functionality of our own website). We should therefore try to limit the number of different, remote sites that we use.
- Open source libraries and files that are part of the XXX CND (let's define a big one here) can be included from this CDN. 
- Other files should be downloaded to our own project and included locally instead.
- It is very easy to lose track of which libraries we use, and what we use them for. We therefore keep track of all our libraries in a central location (see LIBRARIES.md). When considering using a new library, please check if nothing similar has not already been used and where possible re-use this instead.

## General rules

- If available, use minified versions of libraries

## Libraries to use

- Bootstrap for design framework
- Leaflet for maps
- DataTables for tables

## Static folder

The src/core/static folder contains three folders: css, img, js. Libraries we want to load locally are housed there and should go into the appropriate folder: CSS files in css, JavaScript files in js, and images in img.

There is generally no need to create subfolders. For example, the DataTables JavaScript file (datatables.min.js) can go directly in the js folder. However, there are exceptions. For example, the Bootstrap scss files are generated locally. As such, there are a *lot* of files. They're in their own directory since they're all realted and otherwise it would make finding other css files far more difficult.