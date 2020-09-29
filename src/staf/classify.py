# This is an archived script
# It was used to check for duplicates and existing reference spaces
# We did away with that in the processing phase
# But we may want to use this later
# If this file still exists on Jan 1, 2021, then it's time to remove it

    if classify:
        page = "processing.gis.classify.html"
        try:

            names = layer.get_fields(document.meta_data["columns"]["name"])
            rename_list = {}
            matches = None

            # If the user reclassified any names, then we need to ALSO search for these names
            # This seems banana code and I'd like to change it, but I'm not sure how
            # TODO
            # It works fine though

            if "matches" in request.POST and request.POST["matches"]:
                if "," in request.POST["matches"]:
                    m = request.POST["matches"]
                    matches = m.split(",")
                else:
                    matches = request.POST.getlist("matches")
                p(matches)
                for each in matches:
                    if each:
                        check = each.split("_")
                        p(each)
                        p(check[1])
                        rename_id = int(check[1])
                        new = request.POST.get(each)
                        rename_list[rename_id] = new
                        count = 0
                        temp = names
                        names = []
                        for name in temp:
                            count += 1
                            if count == rename_id:
                                names.append(new)
                            else:
                                names.append(name)

            context["matches"] = matches
            hits = ReferenceSpace.objects.filter(name__in=names)
            hit = {}
            hitlist = {}
            for each in hits:
                hit[each.name] = each.id
                hitlist[each.name] = each

            # Let's check to see if there are duplicates
            seen = {}
            duplicates = []
            empty_name = False

            for name in names:
                if not name:
                    empty_name = True
                else:
                    if name not in seen:
                        seen[name] = 1
                    else:
                        if seen[name] == 1:
                            duplicates.append(name)
                        seen[name] += 1

            if duplicates:
                error = True
                duplicates_li = ""
                for each in duplicates:
                    duplicates_li += "<li>" + str(each) + "</li>"
                messages.error(request, "You have duplicates in your list -- please review the source data or the name column selection. Duplicates:<ul>" + duplicates_li + "</ul>")

            if empty_name:
                error = True
                messages.error(request, "You have items in the list that do not have a name -- please review the source data or the name column selection.")

            if request.method == "POST" and not error and "save" in request.POST:
                from django.contrib.gis.geos import GEOSGeometry

                name_field = document.meta_data["columns"]["name"]
                count = 0
                for each in layer:
                    count += 1
                    if count in rename_list:
                        name = rename_list[count]
                    else:
                        name = each.get(name_field)
                    name = str(name)
                    geo = each.geom.wkt
                    if name in hitlist:
                        space = hitlist[name]
                    else:
                        space = ReferenceSpace.objects.create(
                            name = name,
                        )
                    location = ReferenceSpaceLocation.objects.create(
                        space = space,
                        geometry = geo,
                    )
                    space.location = location
                    space.save()
                    RecordRelationship.objects.create(
                        record_parent = document,
                        record_child = space,
                        relationship_id = 30,
                    )
                messages.success(request, "Your shapefile has been imported!")

HTML FILE:


      <h3 class="mt-4">Identify columns</h3>
      <div class="alert alert-danger alert-identify">
        <i class="fas fa-exclamation-triangle mr-2"></i>
        You must tell the system which column contains the <em>names</em> of the reference spaces.
      </div>

      <form id="identify-columns" method="post" action="?classify=true">
        <div class="form-row">
          <div class="col-md-4 col-lg-3 mb-4">
            <label class="category mb-0">Name</label>
            <select class="custom-select{% if not document.meta_data.columns.name %} unidentified{% endif %}" name="classify_name">
              <option value="none" selected disabled>Name</option>
              {% for field in layer.fields %}
                <option value="{{ field }}" {% if document.meta_data.columns.name == field %}selected{% endif %}>{{ field }}</option>
              {% endfor %}
            </select>
          </div>
          <div class="col-md-4 col-lg-3">
            <label class="category mb-0">Identifier</label>
            <select class="custom-select{% if not document.meta_data.columns.identifier %} unidentified{% endif %}" name="identifier">
              <option value="none" selected disabled>Identifier</option>
              {% for field in layer.fields %}
                <option value="{{ field }}" {% if document.meta_data.columns.identifier == field %}selected{% endif %}>{{ field }}</option>
              {% endfor %}
            </select>
          </div>
        </div>

        <div class="form-group">
          <label>Reference space classification(s)</label>
          <select class="form-control select2" multiple required name="geocodes">
            <option></option>
            {% for each in geocodes %}
              <option value="{{ each.id }}" {% if each in active_geocodes %}selected{% endif %}>{{ each.name }} - {{ each.scheme }}</option>
            {% endfor %}
          </select>
        </div>

        {% csrf_token %}
      </form>

      <button class="btn disabled save btn-success" disabled form="identify-columns">
        <i class="fas fa-save"></i>
        Save and next
      </button>

<script>
    // toggle visibility of raw data
    $("#viewraw").click(function(){
      $("i", this).toggleClass("fa-angle-down, fa-angle-up")
      $("#raw").toggle();
    });

    // checking how many columns need a type
    function checkColumns() {
      $("#identify-columns select").each(function() {
        if ($(this).val()) {
          $(this).removeClass("unidentified").addClass("is-valid");
        }
      });

      let unidentifiedCount = $("#identify-columns select.unidentified").length;
      console.log(unidentifiedCount);

      $("#unidentified-columns-count").text(unidentifiedCount)

      if (unidentifiedCount != 0 && $("select[name='classify_name']").hasClass("is-valid")) {
        let alert = $(".alert-identify");

        alert
          .addClass("alert-primary")
          .removeClass("alert-danger")
          .html("<i class='fal fa-info-circle mr-1'></i> You have selected a name and can continue to the next step. However, there are still unselected identifiers")

        $(".btn.save").removeClass("disabled");
        $(".btn.save").removeAttr("disabled");
      } else if (unidentifiedCount == 0) {
        let alert = $(".alert-identify");

        alert
          .addClass("alert-success")
          .removeClass("alert-danger alert-primary")
          .html("<i class='fal fa-check-circle mr-1'></i> You have identified all columns. Please continue to the next step")

        $(".btn.save").removeClass("disabled");
        $(".btn.save").removeAttr("disabled");
      }
    }

    // what happens when a column is identified
    $("#identify-columns select").change(function() {
      $(this).removeClass("is-invalid unidentified");
      $(this).addClass("is-valid");

      checkColumns()

      // check all select values to prevent duplicates
      $("#identify-columns select option").removeAttr("hidden")
      $("#identify-columns select option[value='none']").attr("hidden", "hidden")

      $("#identify-columns select").each(function() {
        let columnValue = $(this).val();

        if (columnValue) {
          $("#identify-columns select option[value='" + columnValue + "']").attr("hidden", "hidden")
        }
      })
    })

    // check unidentified columns on page load
    checkColumns();
  </script>
