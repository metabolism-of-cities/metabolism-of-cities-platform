from django.shortcuts import render
from core.mocfunctions import *
from staf import views as staf
from django.shortcuts import redirect
from django.http import Http404

def index(request):

    return redirect(reverse("water:diagram") + "?region=1012156")

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

    infrastructure = Tag.objects.filter(parent_tag_id=1766)
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
    return redirect(reverse("water:diagram") + "?region=1012156")
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

    lat = 10
    lng = 10

    x = [123,456]
    y = [660,677]

    x = [1045918.297,1013578.8084,1032350.974,1033894.0333,1043455.8766,1039647.8672,1040462.2315,1038254.985,1038262.4848,1030805.7427,1031465.056,1032927.0042,1035733.0693,1033280.8131,1033294.6171,1013816.6669,1013816.9384,1028267.7031,1045936.7533,1045939.3844,1045939.3844,1031371.15,1044878.3663,1035860.3984,1039515.217,1043330.8911,1034387.2589,1045421.5174,1046562.0988,1044407.4532,1038541.0546,1038052.3617,1046059.6214,1044602.1168,1038623.9767,1042944.3461,1024180.2758,1024176.4775,1033998.357,1033996.2633,1008389.1296,1016443.7476,1048300.0135,1048302.7388,1031811.3001,1013579.4538,1016934.6525,1034048.9412,1032958.4144,1033376.0822,1033146.6383,1031478.5591,1031464.5519,1030990.8982,1030980.845,1030979.8343,1017996.3566,1027067.7663,1040367.5374,1030795.9723,1030795.9296,1030795.8826,1053248.3795,1055395.4366,1055145.7801,1053453.8292,1053477.3501,1044410.0572,1035496.0161,1035129.9937,1029696.7585,1031170.5499,1029757.0663,1029299.4089,1036082.4462,1029008.0994,1048235.3605,1035936.7753,1007869.547,1007870.5829,1042317.4068,1042365.8783,1044429.807,1035277.4422,1031453.0931,1029616.2914,1035486.6602,1035471.9926,1034901.8367,1035737.3991,1036044.6706,1042934.6555,1055453.5649,1055456.5039,1053123.3051,1053481.2705,1033785.5453,1033984.8217,1034214.2252,1034268.7985,1042325.9111,1044791.1305,1030023.6655,1033793.978,1030756.16,1031683.6642,1020339.9306,1044793.8804,1044795.9415,1044972.3291,1046591.2923,1046669.8229,1034833.3045,1032977.537,1030804.522,1027324.9779,1037046.0655,1046553.7019,1024131.6201,1024139.3816,1024128.8505,1024131.9406,1018174.7961,1044604.6709,1039037.1164,1028622.0631,1029329.5111,1036820.3186,1032150.6382,1033898.9154,1035620.7965,1008389.0484,1017401.3269,1017396.1863,1017404.0583,1038747.33,1038751.2217,1038752.8178,1040403.6548,1036184.9354,1032902.8612,1014363.6069,1013815.2511,1013816.1241,1027061.5365,1028646.5144,1032499.9639,1030239.4194,1038636.661,1028629.4957,1046812.8926,1038673.4106,1035025.1664,1035025.1664,1045668.2533,1044465.5968,1034242.4293,1036020.6668,1038655.3432,1038654.1183,1052195.9375,1052195.0178,1033479.6524,1035380.4373,1033291.9338,1042832.8127,1042136.0437,1044396.8287,1048311.1658,1037917.2514,1038211.1544,1035916.492,1035074.2024,1036017.5167,1028631.6971,1033482.92,1035469.672,1037967.7238,1037969.1861,1036161.3112,1036163.3478,1036144.1415,1035990.447,1035739.8672,1046565.5501,1046572.349,1036157.4356,1043973.2672,1044646.8887,1039486.5717,1028627.4526,1042952.1737,1042773.5191,1052965.739,1009539.0958,1032521.5766,1032516.3287,1036237.9441,1035343.5089,1037244.2369,1033862.303,1039247.8865,1016445.7044,1013813.0288,1013812.7133,1047552.3683,1047439.1825,1042476.6116,1030750.0749,1046805.7378,1020348.6138,1025858.4461,1030805.415,1013579.976,1038282.808,1053477.6318,1012389.8717,1038554.3634,1030992.3339,1038255.7955,1038261.6677,1038057.3821,1033739.1406,1050631.9352,1048238.1314,1042776.5293,1044970.7641,1042551.9732,1032602.7639,1034268.4414,1033049.3019,1041857.968,1031838.4711,1045601.6321,1041856.0147,1041857.1521,1036855.2531,1036854.9163,1036858.7816,1037965.6997,1045908.5435,1050632.7627,1047469.1418,1027361.3774,1041732.083,1041732.3047,1040425.2061,1039465.9368,1047017.9935,1045994.5955,1046523.0278,1045490.1947,1052567.0957,1042280.1054,1042385.7796,1033444.8732,1045225.1132,1045993.3082,1045276.948,1044599.8916,1044583.8752,1045279.014,1045274.9003,1045432.4971,1048194.6093,1048195.9223,1048191.418,1045010.6003,1045398.517,1042365.9294,1042775.9622,1043311.7486,1039503.6962,1042405.6395,1042058.4143,1042587.6146,1042380.7362,1034219.3254,1045852.8917,1032927.4081,1032928.0987,1042059.7589,1040666.3172,1042655.6863,1032012.9118,1032013.2491,1032183.5121,1032927.7026,1032928.3872,1028546.12,1029870.4376,1048367.4854,1046882.869,1052558.439,1047458.7553,1033294.329,1036855.1052,1044671.6281,1045140.3653,1045142.204,1045142.204,1044674.054,1044660.3866,1044641.8411,1037348.4572,1039837.9831,1040507.4255,1040507.4255,1037280.9661,1041719.8232,1041723.4268,1037515.4317,1040095.8282,1040006.1352,1033468.9438,1032518.1039,1035508.4955,1033470.4516,1013807.8054,1035364.4674,1035357.2739,1035935.9198,1030979.1544,1045930.3482]
    y = [6304140.0232,6351401.4864,6331172.0545,6302056.4225,6305474.5547,6316596.447,6317885.8083,6339510.1977,6339505.1042,6335696.023,6334781.9829,6330777.1829,6322897.3476,6351217.2176,6351221.514,6355795.5298,6355793.2533,6300496.5378,6334372.7294,6334371.3758,6334371.3758,6298960.3229,6302364.1973,6299586.4525,6303736.6394,6303115.527,6303585.5459,6309621.4337,6299576.6895,6309430.3367,6308767.8145,6295897.7622,6303998.1755,6302187.8826,6308744.878,6304084.3643,6341010.0812,6341010.472,6339278.8093,6339278.0743,6361593.5718,6355716.7341,6299280.6199,6299277.9332,6301707.2855,6351402.0468,6353333.5172,6301750.3573,6297802.7826,6296078.6017,6326761.5008,6334815.5402,6334781.8648,6338447.5012,6338425.6207,6338425.8559,6353556.7661,6340828.3474,6337556.9765,6329313.2906,6329312.5721,6329311.9531,6301461.4596,6302457.8004,6302542.5955,6303107.0573,6303081.9373,6333581.1162,6300367.3076,6301109.2788,6301202.8607,6299531.5063,6301211.1094,6301070.5043,6322605.655,6300990.0448,6335462.0021,6305557.8157,6365737.5321,6365737.133,6327820.5305,6327468.4701,6333590.125,6324915.1531,6334762.6807,6298622.6235,6297079.5968,6300379.9631,6299846.7317,6322900.8567,6322584.2012,6326660.9434,6302243.3931,6302241.4537,6304290.4923,6303087.9886,6339379.1841,6339219.6615,6339156.6486,6339048.9168,6324165.4006,6302301.3862,6301147.5097,6303273.1022,6329466.1862,6330887.781,6352411.3612,6302426.1138,6302427.4456,6297927.2806,6299537.534,6299533.827,6301422.9445,6298445.9459,6335696.9147,6341117.4386,6317163.3002,6299471.6053,6351786.8817,6351781.7806,6351780.311,6351778.3412,6353353.6593,6302175.7539,6294571.8721,6300820.8393,6297843.8616,6295028.9588,6301989.9496,6302051.3069,6299910.0456,6361595.4715,6354829.0935,6354831.5641,6354833.8343,6294227.9682,6294226.2872,6294223.2148,6296365.0573,6298158.7544,6302617.9985,6356747.069,6355795.0683,6355796.6712,6340836.0659,6340232.6617,6302366.5221,6301128.1366,6307578.4287,6334438.436,6336957.6597,6307527.1089,6309547.7875,6309547.7875,6301661.6188,6333204.0679,6310264.1752,6313691.0994,6307574.478,6307696.5188,6329792.529,6329792.1577,6292314.6612,6325018.0995,6351217.4379,6301097.5551,6321739.2705,6302808.5318,6335526.0124,6312101.7694,6311497.5869,6305591.8278,6315248.7465,6313694.6187,6334431.3635,6292413.78,6307397.1389,6330332.0387,6330330.8735,6325527.8683,6325525.512,6324992.5314,6303486.5205,6322900.0005,6299579.3391,6299564.6073,6298138.4384,6303183.0813,6302724.4928,6303805.528,6341318.4671,6326969.6897,6326840.6718,6332580.6582,6365855.0916,6326051.4328,6326054.9071,6309115.7168,6305646.9758,6297896.6064,6297796.7588,6305998.8358,6355714.0606,6355789.3709,6355789.6676,6301057.051,6300351.4922,6327135.4343,6329521.5584,6336951.329,6352442.8929,6353069.2984,6335698.6718,6351403.961,6339526.8242,6303089.175,6360556.6356,6308770.7855,6338444.143,6339512.8433,6339516.0046,6295894.7381,6326701.5625,6337806.34,6335460.8314,6326839.3773,6329704.2735,6327052.0407,6303192.9905,6299692.482,6302968.2171,6319964.8062,6303916.037,6319468.0423,6319961.2824,6319963.3581,6326828.3665,6326828.0662,6326833.5354,6330327.4476,6336109.3977,6337811.3115,6330908.4396,6344735.9521,6345127.8854,6345129.4115,6337461.2426,6303807.4895,6303034.2462,6304014.8576,6299075.4729,6319577.4824,6303766.3606,6322945.0479,6322238.5391,6303240.278,6328811.6005,6304041.173,6328808.9487,6328782.08,6328772.866,6326306.7554,6326307.3723,6326494.3044,6326771.1617,6326773.4707,6326768.1895,6329843.2725,6329027.4511,6327465.8808,6326838.7735,6326866.5656,6317717.0066,6324668.7241,6326315.4538,6322739.2579,6322226.8132,6301093.0617,6332940.1846,6330776.685,6330775.6919,6326103.7973,6322585.731,6319511.2587,6328693.1045,6328692.4149,6328661.5174,6330776.2205,6330775.3311,6334759.2369,6335114.2049,6331842.6544,6332111.2053,6330568.6503,6330904.5403,6351199.2269,6326828.2058,6336889.4437,6334697.1289,6334696.9265,6334696.9265,6336881.2444,6336888.8414,6336891.0299,6315221.3988,6340643.9087,6339845.4777,6339845.4777,6297707.4992,6345127.3349,6345153.1078,6315751.0642,6318812.1175,6335560.5892,6292351.9625,6302303.1979,6293075.4966,6292351.6958,6355803.2895,6305637.0406,6305643.7834,6305561.5102,6338426.3284,6298553.8389]

    names = ["Name1", "Name2"]
    names = ["Cpt _735","Cpt_1","Cpt_1008","Cpt_1013","Cpt_1016","Cpt_1017","Cpt_1018","Cpt_1021","Cpt_1023","Cpt_1035","Cpt_1036","Cpt_1037","Cpt_1038","Cpt_1039","Cpt_1040","Cpt_1041","Cpt_1042","Cpt_1043","Cpt_1044","Cpt_1045","Cpt_1062","Cpt_1067","Cpt_107","Cpt_1071","Cpt_112","Cpt_115","Cpt_1151","Cpt_1156","Cpt_116","Cpt_118","Cpt_119","Cpt_135","Cpt_142","Cpt_144","Cpt_160","Cpt_164","Cpt_174","Cpt_175","Cpt_179","Cpt_181","Cpt_182","Cpt_19","Cpt_190","Cpt_191","Cpt_198","Cpt_2","Cpt_20","Cpt_205","Cpt_206","Cpt_207","Cpt_213","Cpt_214","Cpt_215","Cpt_216","Cpt_217","Cpt_218","Cpt_22","Cpt_220","Cpt_222","Cpt_223","Cpt_224","Cpt_225","Cpt_232","Cpt_233","Cpt_234","Cpt_235","Cpt_236","Cpt_237","Cpt_238","Cpt_239","Cpt_245","Cpt_246","Cpt_248","Cpt_249","Cpt_25","Cpt_252","Cpt_254","Cpt_259","Cpt_260","Cpt_261","Cpt_265","Cpt_266","Cpt_268","Cpt_269","Cpt_270","Cpt_280","Cpt_292","Cpt_293","Cpt_294","Cpt_297","Cpt_298","Cpt_3","Cpt_306","Cpt_307","Cpt_308","Cpt_309","Cpt_310","Cpt_312","Cpt_313","Cpt_314","Cpt_319","Cpt_320","Cpt_324","Cpt_325","Cpt_342","Cpt_343","Cpt_350","Cpt_359","Cpt_360","Cpt_361","Cpt_363","Cpt_365","Cpt_366","Cpt_371","Cpt_383","Cpt_384","Cpt_386","Cpt_39","Cpt_391","Cpt_392","Cpt_393","Cpt_394","Cpt_40","Cpt_402","Cpt_403","Cpt_408","Cpt_409","Cpt_411","Cpt_417","Cpt_419","Cpt_422","Cpt_423","Cpt_427","Cpt_428","Cpt_429","Cpt_438","Cpt_439","Cpt_440","Cpt_443","Cpt_460","Cpt_464","Cpt_472","Cpt_473","Cpt_474","Cpt_475","Cpt_478","Cpt_492","Cpt_495","Cpt_504","Cpt_5","Cpt_50","Cpt_505","Cpt_507","Cpt_511","Cpt_518","Cpt_520","Cpt_538","Cpt_541","Cpt_547","Cpt_549","Cpt_558","Cpt_559","Cpt_56","Cpt_563","Cpt_566","Cpt_574","Cpt_581","Cpt_582","Cpt_585","Cpt_587","Cpt_588","Cpt_590","Cpt_598","Cpt_599","Cpt_6","Cpt_60","Cpt_607","Cpt_608","Cpt_609","Cpt_610","Cpt_611","Cpt_612","Cpt_62","Cpt_621","Cpt_626","Cpt_627","Cpt_63","Cpt_630","Cpt_632","Cpt_633","Cpt_636","Cpt_638","Cpt_639","Cpt_642","Cpt_643","Cpt_644","Cpt_645","Cpt_646","Cpt_647","Cpt_65","Cpt_653","Cpt_656","Cpt_663","Cpt_666","Cpt_667","Cpt_675","Cpt_677","Cpt_687","Cpt_688","Cpt_693","Cpt_696","Cpt_697","Cpt_698","Cpt_699","Cpt_7","Cpt_700","Cpt_702","Cpt_703","Cpt_706","Cpt_707","Cpt_708","Cpt_709","Cpt_710","Cpt_711","Cpt_717","Cpt_718","Cpt_719","Cpt_720","Cpt_725","Cpt_729","Cpt_732","Cpt_739","Cpt_740","Cpt_741","Cpt_744","Cpt_746","Cpt_747","Cpt_748","Cpt_749","Cpt_750","Cpt_751","Cpt_752","Cpt_755","Cpt_759","Cpt_760","Cpt_761","Cpt_762","Cpt_763","Cpt_764","Cpt_765","Cpt_769","Cpt_773","Cpt_777","Cpt_778","Cpt_780","Cpt_782","Cpt_789","Cpt_79","Cpt_790","Cpt_791","Cpt_792","Cpt_793","Cpt_794","Cpt_795","Cpt_796","Cpt_797","Cpt_798","Cpt_800","Cpt_804","Cpt_806","Cpt_807","Cpt_808","Cpt_820","Cpt_823","Cpt_825","Cpt_826","Cpt_832","Cpt_834","Cpt_837","Cpt_848","Cpt_849","Cpt_857","Cpt_858","Cpt_859","Cpt_862","Cpt_863","Cpt_864","Cpt_865","Cpt_866","Cpt_867","Cpt_868","Cpt_872","Cpt_874","Cpt_879","Cpt_882","Cpt_887","Cpt_889","Cpt_891","Cpt_892","Cpt_893","Cpt_894","Cpt_900","Cpt_905","Cpt_906","Cpt_91","Cpt_910","Cpt_911","Cpt_912","Cpt_92","Cpt_927","Cpt_928","Cpt_93","Cpt_931","Cpt_939","Cpt_94","Cpt_940","Cpt_948","Cpt_95","Cpt_954","Cpt_960","Cpt_961","Cpt_962","Cpt_990","Cpt_993"]

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
    region = None
    flows = Tag.objects.filter(parent_tag_id=1752)
    if "region" in request.GET:
        region = ReferenceSpace.objects.get(pk=request.GET["region"])
    context = {
        "title": "Eau",
        "regions": NICE_REGIONS,
        "documents": available_library_items(request).filter(tags__in=flows).order_by("id"),
        "region": region,
    }
    return render(request, "water/dashboard.html", context)

def diagram(request):

    try:
        doc = available_library_items(request).get(pk=1013292)
    except:
        raise Http404("Data object was not found (or you lack access).") 

    file = doc.attachments.all()[0]

    from openpyxl import load_workbook
    import pandas as pd
    import numpy as np
    df = pd.read_excel(file.file)

    if "region" in request.GET and request.GET.get("region") != "1012156":
        region = request.GET["region"]
        this_region = None
        for key,value in NICE_REGIONS.items():
            if value == int(region):
                this_region = key
        if this_region:
            columns_to_keep = [this_region]
            df = df[columns_to_keep]
            totals = df.sum(axis=1, numeric_only=True)
            # Getting totals just so that the syntax below is the same, but in reality
            # we only have a single column anyways
        else:
            messages.error(request, f"The region {region} was not found.")
    else:
        totals = df.set_index("Type").sum(axis=1, numeric_only=True)

    demo_figures = {
        "extract_surface": totals[0],
        "extract_subterrain": totals[1],
        "extract_mountains": totals[2],
        "imports": totals[4]-totals[0]-totals[1]-totals[2]+totals[5]+totals[8],
        "exports": totals[6],
        "losses1": totals[7],
        "losses2": totals[4]*0.02,
        "energy": totals[8],
        "treatment_internal": totals[9]+totals[10],
        "treatment_external": totals[11],
        "treatment_imports": totals[12],
    }
    if demo_figures["imports"] < 0:
        demo_figures["exports"] = demo_figures["imports"]*-1 + demo_figures["exports"]
        demo_figures["imports"] = 0

    demo_figures["imports_without_buy"] = demo_figures["imports"]*0.6
    demo_figures["buy"] = demo_figures["imports"]*0.4

    # k m3 -> km3
    for key,value in demo_figures.items():
        demo_figures[key] = int(value/(1000))

    data = demo_figures
    data["extract"] = data["extract_surface"] + data["extract_subterrain"] + data["extract_mountains"]
    data["treatment"] = data["treatment_internal"] + data["treatment_external"]

    if demo_figures["extract"] == 0:
        demo_figures["losses2"] += demo_figures["losses1"]
        demo_figures["losses1"] = 0

    total_size = data["extract"] + data["imports"]
    pixels = 100
    per_unit = pixels/total_size

    pixel_data = {}
    for key,value in data.items():
        if value:
            pixel_data[key] = int(value*per_unit) if int(value*per_unit) > 1 else 1
        else:
            pixel_data[key] = 0

    pixel_data["seg1"] = pixel_data["imports"] + pixel_data["extract"]
    pixel_data["seg2"] = pixel_data["seg1"] - pixel_data["losses1"]
    pixel_data["seg3"] = pixel_data["seg2"] - pixel_data["losses2"]
    pixel_data["seg4"] = pixel_data["seg3"] - pixel_data["energy"] - pixel_data["exports"]
    pixel_data["seg5"] = pixel_data["seg4"] + pixel_data["treatment_imports"]
    pixel_data["seg6"] = pixel_data["seg5"] - pixel_data["treatment_external"]

    infrastructure = Tag.objects.filter(parent_tag_id=1766)
    flows = Tag.objects.filter(parent_tag_id=1752)

    context = {
        "title": "Eau",
        "regions": NICE_REGIONS,
        "data": data,
        "pixel_data": pixel_data,
        "pixels": range(1,100),
        "rows": range(1,40),
        "link": reverse("water:diagram"),
        "infrastructure": infrastructure, 
        "documents": available_library_items(request).filter(tags__in=infrastructure),
        "documents_flows": available_library_items(request).filter(tags__in=flows),
    }
    return render(request, "water/diagram.html", context)
