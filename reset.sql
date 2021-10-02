#############################################################################
# 
# If you ever need to reset the database, then the easiest thing to do
# is to run the query below. After doing that, you can run the migrations
# or import the SQL directly from a data dump
#
#############################################################################

DROP SCHEMA public CASCADE;
CREATE SCHEMA public;

#############################################################################
#
# The following code is used to create the common table expression 
# for the hierarchical data
#
# Implemented similar to the system outlined at 
# https://schinckel.net/2016/01/23/adjacency-lists-in-django-with-postgres/
# 
# This should be run AFTER the database has been migrated. It will create
# a 'view' in the database (not a real table, but a query-based table)
# 
#############################################################################

CREATE RECURSIVE VIEW stafdb_material_tree(root_id, node_id, ancestors) AS

SELECT record_ptr_id, record_ptr_id, ARRAY[]::INTEGER[]
FROM stafdb_material WHERE parent_id IS NULL

UNION ALL

SELECT tree.root_id, node.record_ptr_id, tree.ancestors || node.parent_id
FROM stafdb_material node INNER JOIN stafdb_material_tree tree ON (node.parent_id = tree.node_id)
