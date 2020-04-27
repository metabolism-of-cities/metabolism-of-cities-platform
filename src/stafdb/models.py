from django.db import models
from django.contrib.gis.db import models
from django.urls import reverse

# The geocode scheme defines a particular standard, for instance 3166-1 or the South African postal code system
class GeocodeScheme(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    coverage = models.ForeignKey("ReferenceSpace", on_delete=models.SET_NULL, null=True, blank=True)
    is_comprehensive = models.BooleanField(default=True, db_index=True)
    is_deleted = models.BooleanField(default=False, db_index=True)
    icon = models.CharField(max_length=50, null=True, blank=True) # Web field
    def __str__(self):
        return self.name
    class Meta:
        db_table = "stafdb_geocode_scheme"
    def get_absolute_url(self):
        return reverse("stafcp_geocode", args=[self.id])

# Lists all the different levels within the system. Could be a single level (e.g. Postal Code), but it 
# could also include various levels, e.g.: Country > Province > City
# Depth should start at 0 and go up from there
class Geocode(models.Model):
    scheme = models.ForeignKey(GeocodeScheme, on_delete=models.CASCADE, related_name="geocodes")
    name = models.CharField(max_length=255)
    depth = models.PositiveSmallIntegerField()
    description = models.TextField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False, db_index=True)
    def __str__(self):
        return self.name

# The reference space, for instance the country "South Africa", the city "Cape Town", or the postal code 8000
class ReferenceSpace(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(null=True, blank=True)
    slug = models.CharField(max_length=100, null=True)
    location = models.ForeignKey("ReferenceSpaceLocation", on_delete=models.SET_NULL, null=True, blank=True)
    is_deleted = models.BooleanField(default=False, db_index=True)
    geocodes = models.ManyToManyField(Geocode, through="ReferenceSpaceGeocode")
    def __str__(self):
        return self.name

class ReferenceSpaceLocation(models.Model):
    space = models.ForeignKey(ReferenceSpace, on_delete=models.CASCADE)
    description = models.TextField(null=True, blank=True)
    start = models.DateField(null=True, blank=True, db_index=True)
    end = models.DateField(null=True, blank=True, db_index=True)
    geometry = models.GeometryField()
    is_deleted = models.BooleanField(default=False, db_index=True)
    def __str__(self):
        return "Location for " + self.space.name
    class Meta:
        ordering = ["-start"]
        db_table = "stafdb_referencespace_location"

class ReferenceSpaceGeocode(models.Model):
    geocode = models.ForeignKey(Geocode, on_delete=models.CASCADE)
    space = models.ForeignKey(ReferenceSpace, on_delete=models.CASCADE)
    identifier = models.CharField(max_length=255, db_index=True, null=True, blank=True)
    class Meta:
        db_table = "stafdb_referencespace_geocode"

class ActivityCatalog(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    def __str__(self):
        return self.name

class Activity(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    catalog = models.ForeignKey(ActivityCatalog, on_delete=models.CASCADE)
    code = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    description = models.TextField(null=True, blank=True)
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
    def get_absolute_url(self):
        return reverse("stafcp_flowdiagram", args=[self.id])
    def __str__(self):
        return self.name

# The 
class FlowBlocks(models.Model):
    diagram = models.ForeignKey(FlowDiagram, on_delete=models.CASCADE, related_name="blocks")
    origin = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name="blocks_from")
    destination = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name="blocks_to")
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
