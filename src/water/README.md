# INTRODUCTION

This system was built within the framework of the Metabolism of Cities website. It runs as a separate project within this framework, with project files, templates, static files, all etc being included in sub-folders within the Metabolism of Cities repository. On a database level, the system uses its own dedicated table, all prefixed with "Water" and clearly demarcated in their own block in the models.py file for this project (at the time of writing, starting at line 3688 in the models file). All these tables are exclusively used for this system, and can be adjusted at liberty for the needs of this project. Similarly, the templates, static files, and views are not shared in any way and can be adjusted freely to suit the needs of this particular project. There are a few instances where Metabolism of Cities-specific pages and functionalities are being used. An example is found in some part of the Control Panel (such as the tools to manage web page content or adjust the administrators for this website). These pages or functionalities should _not_ be changed at will, but should be coordinated with the Metabolism of Cities team. However, the location of the files (whether or not they are inside a 'water' folder) makes it very clear to see if the files are being shared or not. 

System development has gone through a number of different phases, and the requirements for this system have changed along the way. As a consequence, a number of features were built using more of Metabolism of Cities' functionality (such as the data visualization system, mapping system, and stocks and flows data structures). However, it was decided at some stage that those features were not to be used at this stage for this website, but features already built were not to be completely discarded. For this reason, the views, urls, and templates might refer to pages not currently in use. If at any point these features are to be re-embedded, then some of the work done in the past might be used for this. 

For an overview of the technical requirements for this website, and the general data structure and functioning of the platform it is built around, please see the Metabolism of Cities general readme: https://github.com/metabolism-of-cities/metabolism-of-cities-platform#readme

# SANKEY DIAGRAMS

At the core of this platform are sankey diagrams (and a set of bar-charts for the Material Stock section). These diagrams display the flows (or stocks) for the chosen territory, time period, and material. The user can change these filters to show exactly what is of interest. In addition, different levels of detail are possible, with level 1 sankeys showing a more aggregated level of data, and level 2 showing a more disaggregated, complex picture of the situation.

The sankeys include nodes which are connected with lines. The width of the lines as well as the labels on the nodes (displaying how much of a material flows 'into' the node) are dynamically generated, depending on the chosen filter. This happens by placing an ajax call with the relevant parameters. The returned json object is then processed in a javascript script and the relevant elements are adjusted. Furthermore, the user can click any of the lines to pull up a chart, table, and description of the chosen flow. These details are also generated on-the-fly, by placing another ajax query to a different function, and again receiving a json object. 

The core files to manage all this are:

- sankey.html -> the HTML page with the general skeleton for the different elements
- \_javascript.html -> the javascript code for all the ajax requests and different manipulations of the SVG files etc. It is saved as an HTML file in order to more easily be able to include Django templating code inside this file. 
- the .svg files with the actual drawings in the templates/water/svg folder
- the views.py file in the water project; specifically the sankey, ajax, and ajax\_chart\_data functions (separate but very similar function exists for the stock data)

Code comments are available in the sankey.html, \_javascript and Django views.py files to understand what is happening in different places. 

# GENERAL FUNCTIONING OF SANKEYS

- Water level 1 is calculated based on the level-2 flows. For each level-2 flow in the back-end, there is a configuration saved that indicates which level-1 flow this should contribute to. This 'adding up' is done dynamically, when creating the json response that is created through an ajax request at the moment of generating the sankey. 
- Water level 2 has different 'variants' of the sankey. Some of the nodes and flows are manually hidden because of particular features in the data which makes things NOT conform to the previously outlined rules (which state that nodes/lines should only be hidden if 0, and shown if > 0. These 'variants' are called alternative designs, and the \_javascript.html file contains enough comments to understand what happens when.
- Energy level 1 and 2 are calculated like water; with level 2 data stored in the database, and level 1 data calculated on the fly. 
- For the materials level 1 chart it was NOT possible to calculate them based on level-2 data, so an exception is built into the ajax function that returns the json object. For this sankey, level 1 data is simply stored separately in the database and retrieved directly from the db when building the sankey. 
- An unplanned chart called 'Level 2 circulair' was added to the materials sankeys. In order not to complexify the database this is stored and managed as 'level 3' data, but shown to the user as 'Level 2 circulair'.

# GENERAL DESIGN WORKFLOW

In the past, sankeys have been generated by converting the original design files into .svg files, and then marking up the code to conform to certain standards so that they can be used online. For the general steps taken by the designers, see water.svg comments for the 10 most important steps. As a web developer, this was the workflow I used upon receiving the SVG files from the designers:

1. Ensuring the SVG has the id "sankey\_svg" (without this ID, the SAVE button will not work)
2. Ensuring the BASEMAP layers includes the right code. It is as simple as copying the 6 image tags from a previous file.
3. Ensuring that all the flows (elements with class="path") have been added to the database. Can be checked in the control panel. 
4. Ensuring that all the nodes (elements with class="node") have been added to the database. The id of the node is the identifier in the database.
5. Ensuring that all the nodes have the right flows moving into and out of the node configured in the database. Can all be set up in the control panel. These entry/exit flows are used to calculate the total quantity shown in the label of the node and to ensure they are hidden of no flow whatsoever moved into or out of this node when particular filters are applied.

# DYNAMIC IMAGES IN SANKEYS

For materials where icons need to be dynamically shown (e.g. when selecting a metal, a 'metal' icon should appear in some of the nodes):
1. Identify the nodes that have dynamic icons based on the graphic design instructions.
2. Remove any 'image' tag that might be present inside this node.
3. Add a separate image tag with a 'data-node' attribute which sets the number of the node it pertains to.
4. That same image tag should have the class 'swapimage' and the x and y attributes should be used to position it on the page (will require some trial and error to get them right).

SAMPLE CODE:

  `<image data-node="1" width="20" height="20" xlink:href="" class="swapimage" x="247.5" y="84" />`

Notes:
- Easiest way is to copy this from a previous file (e.g. materials.svg) and just change the node IDs and the x/y settings.
- The way this works is that in the javascript code, the xlink:href attribute is being changed to reflect the path to the appropriate image file depending on the chosen flow.


# ELEMENTS TO CHECK:

- Images that represent the background map are called "space-X" with X being the ID of this territory in the database. This is used to highlight the chosen territory on the map.
- Paths (flows) have three classes: 
  - path -> required class
  - COLOR -> either the name of a color class (see the javascript file with definitions), or colorX with X being a number 1-5, for those with dynamic colors that change upon selecting a material type (only applies to materials/stock sankeys)
  - forward/backward -> this defines the direction of the flow. Sometimes counter-intuitive because it all depends on the start and end point chosen when drawing the line. Simply swap it around in case they flow in the wrong direction when animated.
- Paths have a data-id which refers to the number of the flow as defined in the database (field: "identifier") and in the data spreadsheets that are being uploaded
- Nodes have an id "node-X" with X being a number denoting the ID of this node. This ID is used in the database (see nodes: identifier) and it allows us to correctly print the quantity of this node (not all nodes show quantities, but many do), and to hide this node if the quantity is 0. 
- The text inside the node that displays the quantity should have the class "qty"

# Changelog

December 3, 2023 - First version written by Paul Hoekman
