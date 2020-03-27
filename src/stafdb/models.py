from django.db import models

# The geocode system defines a particular standard, for instance 3166-1 or the South African postal code system
class GeocodeSystem(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    def __str__(self):
        return self.name

# Lists all the different levels within the system. Could be a single level (e.g. Postal Code), but it 
# could also include various levels, e.g.: Country > Province > City
class Geocode(models.Model):
    name = models.CharField(max_length=255)
    system = models.ForeignKey(GeocodeSystem, on_delete=models.CASCADE)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    def __str__(self):
        return self.name

# The reference space, for instance the country "South Africa", the city "Cape Town", or the postal code 8000
#class ReferenceSpace(models.Model):
#    name = models.CharField(max_length=255, db_index=True)
#    geocode = models.ForeignKey(Geocode, on_delete=models.CASCADE)
#    city = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='city_location')
#    country = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='country_location')
#    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='child')
#    description = models.TextField(null=True, blank=True)
#    url = models.CharField(max_length=255, null=True, blank=True)
#    slug = models.SlugField(db_index=True, max_length=255, null=True)
#    location = models.ForeignKey('multiplicity.ReferenceSpaceLocation', on_delete=models.SET_NULL, null=True, blank=True)
#    active = models.BooleanField(default=True, db_index=True)

class Process(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    code = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    description = models.TextField(null=True, blank=True)
    slug = models.SlugField(db_index=True, max_length=255, null=True, blank=True)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="children")
    is_separator = models.BooleanField()
    def __str__(self):
        if self.code:
            return self.code + " - " + self.name
        else:
            return self.name

    class Meta:
        ordering = ["id"]

# The Flow Diagram describes a system (e.g. the Water sector) and describes the life-cycle based on 
# the processes that take place within it (e.g. Water collection > Water treatment > Use > Wastewater treatment)
class FlowDiagram(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    def __str__(self):
        return self.name

# The 
class FlowBlocks(models.Model):
    diagram = models.ForeignKey(FlowDiagram, on_delete=models.CASCADE)
    origin = models.ForeignKey(Process, on_delete=models.CASCADE, related_name="blocks_from")
    destination = models.ForeignKey(Process, on_delete=models.CASCADE, related_name="blocks_to")
    description = models.TextField(null=True, blank=True)
    def __str__(self):
        return self.origin.name + " - " + self.destination.name

class MaterialCatalog(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    url = models.CharField(max_length=255, null=True, blank=True)
    def __str__(self):
        return self.name

class Material(models.Model):
    name = models.TextField(db_index=True)
    code = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="children")
    catalog = models.ForeignKey(MaterialCatalog, on_delete=models.CASCADE, blank=True, null=True)
    #is_separator = models.BooleanField()
    description = models.TextField(null=True, blank=True)
    def __str__(self):
        return self.code + " - " + self.name

