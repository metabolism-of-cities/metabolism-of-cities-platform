from django.shortcuts import render
from core.mocfunctions import *
from staf import views as staf

def index(request):
    input = [
        #{"name": "Precipitation", "logo": "cloud-showers-heavy"},
        {"name": "Ground water extraction", "logo": "water-rise"},
        {"name": "Surface water", "logo": "water"},
        {"name": "Rain water harvesting", "logo": "raindrops"},
        {"name": "Imports", "logo": "arrow-to-right"},
    ]
    output = [
        {"name": "Exports", "logo": "arrow-from-left"},
        {"name": "Leaks and losses", "logo": "house-flood"},
        {"name": "Dissipative use", "logo": "sprinkler"},
    ]
    consumption = [
        {"name": "Residents", "logo": "shower"},
        {"name": "Government", "logo": "faucet-drip"},
        {"name": "Industry", "logo": "industry"},
        {"name": "Agriculture", "logo": "tractor"},
    ]
    distribution = [
        {"name": "Reservoirs", "logo": "rectangle-wide"},
        {"name": "Reticulation system", "logo": "chart-network"},
        {"name": "Material stock analysis", "logo": "chimney"},
        {"name": "Water meters", "logo": "tachometer", "id": 1010649},
    ]
    production = [
        {"name": "Water treatment plants", "logo": "ball-pile"},
        {"name": "Energy analysis", "logo": "bolt"},
        {"name": "Material flow analysis", "logo": "th-list"},
        {"name": "Material stock analysis", "logo": "chimney"},
    ]
    waste = [
        {"name": "Wastewater treatment plants", "logo": "toilet", "id": 1010500},
        {"name": "Energy analysis", "logo": "bolt"},
        {"name": "Material flow analysis", "logo": "th-list"},
        {"name": "Material stock analysis", "logo": "chimney"},
    ]
    test = [
        {"name": "XXX", "logo": "XXXX"},
    ]

    # Temporary function to assign GPS coordinates to reference spaces
    # while we wait for the final GPS coordinates to be provided
    if "random_gps" in request.GET and request.user.id == 1:
        from django.contrib.gis.geos import Point
        import random 
        spaces = ReferenceSpace.objects_include_private.filter(source_id=request.GET["random_gps"])
        for space in spaces:
            lat = random.randrange(4360,4430)/100
            lng = random.randrange(6870,7390)/1000
            space.geometry = Point(lng, lat)
            space.save()

    infrastructure = Tag.objects.filter(parent_tag_id=1716)
    context = {
        "input": input,
        "output": output,
        "consumption": consumption,
        "distribution": distribution,
        "production": production,
        "waste": waste,
        "regions": NICE_REGIONS,
        "infrastructure": infrastructure,
        "documents": available_library_items(request).filter(tags__in=infrastructure),
    }
    return render(request, "water/index.html", context)

def demo(request):
    context = {
        "title": "Home",
    }
    return render(request, "water/demo.html", context)

def water_map(request):
    context = {
        "title": "Eau",
    }
    return render(request, "water/map.html", context)

def infrastructure(request):
    space = ActivatedSpace.objects.get(part_of_project_id=request.project, space_id=request.GET["region"])
    return staf.space_map(request, space.space.slug)

def temp_script(request):

    ###### REMOVE MOC_EXTRAS FUNCTIONS ONCE THIS IS COMPLETED!!
    from django.contrib.gis.geos import Point
    import folium

    x = [123,456]
    y = [660,677]
    names = ["Name1", "Name2"]

    geometry = Point(lng, lat)

    # From https://stackoverflow.com/questions/38961816/geopandas-set-crs-on-points
    import pandas as pd
    from shapely.geometry import Point
    from geopandas import GeoDataFrame

    df = pd.DataFrame({'Names':names,
                   'Lat':y,
                   'Lon':x})

    geometry = [Point(xy) for xy in zip(df.Lon, df.Lat)]
    gdf = {}

    crs_list = [2154]

    maps = {}
    for each in crs_list:
        gdf = GeoDataFrame(df, geometry=geometry)
        gdf.set_crs(epsg=each, inplace=True, allow_override=True)
        # Change to WGS84
        gdf.to_crs(epsg=4326, inplace=True)

        p(gdf)

        for index, row in gdf.iterrows():
            geo = row["geometry"]
            x, y = geo.coords.xy
            x = x[0]
            y = y[0]
            p(x)
            p(y)

        maps[each] = folium.Map(
            location=[y,x],
            zoom_start=20,
            scrollWheelZoom=False,
            tiles=STREET_TILES,
            attr="Mapbox",
        )

    map2 = folium.Map(
        location=[lng,lat],
        zoom_start=10,
        scrollWheelZoom=False,
        tiles=STREET_TILES,
        attr="Mapbox",
    )

    map3 = folium.Map(
        location=[lng,lat],
        zoom_start=15,
        scrollWheelZoom=False,
        tiles=STREET_TILES,
        attr="Mapbox",
    )


    #folium.GeoJson(
    #    geometry,
    #    name="geojson",
    #).add_to(map)

    m = gdf.to_html()

    context = {
        "title": "Eau",
        "maps": maps,
        "map2": map2._repr_html_() if map else None,
        "map3": map3._repr_html_() if map else None,
        "gdf": m,
        "crs_list": crs_list,
    }
    return render(request, "water/infrastructure.html", context)

def dashboard(request):
    context = {
        "title": "Eau",
        "regions": NICE_REGIONS,
    }
    return render(request, "water/dashboard.html", context)
