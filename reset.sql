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
# The following code is used to create a recursive view, dynamically 
# storing a materialised path for the hierarchical data.
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

----

CREATE RECURSIVE VIEW stafdb_material_tree_closure(path, ancestor_id, descendant_id, depth) AS

SELECT ARRAY[record_ptr_id], record_ptr_id, record_ptr_id, 0 FROM stafdb_material

UNION ALL

SELECT parent_id || path, parent_id, descendant_id, depth + 1
FROM stafdb_material INNER JOIN stafdb_material_tree_closure ON (ancestor_id = record_ptr_id)
WHERE parent_id IS NOT NULL;



class MaterialTreeClosure(models.Model):
    path = ArrayField(base_field=models.IntegerField(), primary_key=True)
    ancestor = models.ForeignKey(MaterialTree, related_name='+', on_delete=models.CASCADE)
    descendant = models.ForeignKey(MaterialTree, related_name='+', on_delete=models.CASCADE)
    depth = models.IntegerField()

    class Meta:
        db_table = "stafdb_material_tree_closure"
        managed = False

class Closure(models.Model):
    path = ArrayField(base_field=models.IntegerField(), primary_key=True)
    ancestor = models.ForeignKey('tree.Node', related_name='+')
    descendant = models.ForeignKey('tree.Node', related_name='+')
    depth = models.IntegerField()

    class Meta:
        app_label = 'tree'
        managed = False

----

UPDATE stafdb_material SET parent_id = NULL WHERE parent_id = 25935;
DELETE FROM "stafdb_material"
WHERE "catalog_id" = '18998' AND "parent_id" IS NULL AND (("record_ptr_id" = '25935'));

