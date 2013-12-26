function PiatiMap (selector, projects) {
    var geojsonMarkerOptions = {
        radius: 8,
        fillColor: "#ff7800",
        color: "#000",
        weight: 1,
        opacity: 1,
        fillOpacity: 0.8
    };

    var map = new L.Map(selector, {
        center: new L.LatLng(15,-5),
        zoom: 6,
        scrollWheelZoom: false
    });
    var tilelayer = new L.tileLayer('http://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png', {
        maxZoom: 18,
        attribution: 'Data © OpenStreetMap, tiles © HOT'
    }).addTo(map);

    var projectsLayer = L.featureGroup().addTo(map);
    function projectToMarkers (project) {
        var template = "<h3>{name}</h3><a href='{url}'>{projectName}</a>";
        if (project.locations) {
            var location, marker;
            for (var i = 0; i < project.locations.length; i++) {
                location = project.locations[i];
                marker = L.marker([location.lat, location.lng]);
                marker.bindPopup(L.Util.template(template, {name: location.name, url: project.url, projectName: project.name}));
                projectsLayer.addLayer(marker);
            }
        }
    }

    this.update = function (projects) {
        projectsLayer.clearLayers();
        for(var id in projects) {
            projectToMarkers(projects[id]);
        }
    };
    this.update(projects);
    this.map = map;
    // map.fitBounds(projectsLayer.getBounds()); // => Strange behaviour in 0.8-dev
    return this;
}

d3.selection.prototype.checked = function(value) {
  return arguments.length < 1 ? this.property("checked") : this.property("checked", value);
};
Array.prototype.flattenMap = function(func /*, thisArg */)
{
    "use strict";

    if (this === void 0 || this === null) throw new TypeError();

    var t = Object(this);
    var len = t.length >>> 0;
    if (typeof func !== "function") throw new TypeError();

    var res = [], r;
    var thisArg = arguments.length >= 2 ? arguments[1] : void 0;
    for (var i = 0; i < len; i++)
    {
        if (i in t) {
            r = func.call(thisArg, t[i], i, t);
            if (r instanceof Array) {
                res = res.concat(r);
            } else {
                res.push(r);
            }
        }
    }

    return res;
};


var PiatiPie = function (accessor) {

    var cv_w = 300,                        //width
        cv_h = 300,                            //height
        cv_r = 100,                            //radius
        cv_color = d3.scale.category20b();     //builtin range of colors
  
    var cv_svg = d3.select("#tab-charts")
        .append("svg:svg")              //create the SVG element inside the <body>
        .attr("width", cv_w)           //set the width and height of our visualization (these will be attributes of the <svg> tag
        .attr("height", cv_h)
        .append("svg:g")                //make a group to hold our pie chart
        .attr("transform", "translate(" + cv_r + "," + cv_r + ")");    //move the center of the pie chart from 0, 0 to radius, radius

    var cv_arc = d3.svg.arc()              //this will create <path> elements for us using arc data
        .outerRadius(cv_r);

    var cv_pie = d3.layout.pie()           //this will create arc data for us given a list of values
        .value(function(d) { return d.value; });    //we must tell it out to access the value of each element in our data array


    this.updateWith = function () {
        var data = accessor();
        var cv_path = cv_svg.selectAll("path").data(cv_pie(data));
        var cv_text = cv_svg.selectAll("text").data(cv_pie(data));
        cv_path.exit().remove();
        cv_text.exit().remove();
        
        cv_path.enter().append("path");
        cv_path.attr("fill", function(d, i) { return cv_color(i); } )
            .attr("d", cv_arc);
        cv_text.enter()
            .append("text");
        cv_text.attr("transform", function(d) {
                d.innerRadius = 0;
                d.outerRadius = cv_r;
                return "translate(" + cv_arc.centroid(d) + ")";
            })
            .attr("text-anchor", "middle")
            .attr("font-weight", "bold")
            .attr("fill", "#FFFFFF")
            .attr("font-size", "10px")
            .text(function(d) { return "" + d.data.label + " (" + d.value + ")"; });
        
    };
    this.updateWith();
    return this;
};


function Projects(data) {

    var THIS = {

        init: function (data) {
            this.data = data;
            return this;
        },

        getSectorsValues: function (d) {
            return d.sectors.map(function (s) { return s.name; });
        },

        getOrgsValues: function (d) {
            return d.orgs.map(function (s) { return s.name; });
        },

        getTopicsValues: function (d) {
            return d.topics.map(function (s) { return s; });
        },

        getStatusValue: function (d) {
            return d.status;
        }

    };

    return THIS.init(data);

}


function PiatiProjectsBrowser(projects, options) {

    var API = {

        init: function (options) {
            var that = this;
            this.dispatch = d3.dispatch("filter");
            this.filters = ['status', 'sectors', 'orgs', 'topics'];

            this.list = d3.select('#tab-data')
                          .text('')
                          .selectAll('li')
                          .data(projects.data);
            this.list.enter().append("li");
            this.list.html(this.renderProject);
            this.mapHandler = new PiatiMap('tab-map', projects.data);
            this.statusPie = new PiatiPie(HELPERS.bind(this.computeStats, this, 'status'));
            this.sectorsPie = new PiatiPie(HELPERS.bind(this.computeStats, this, 'sectors', 'name'));

            this.dispatch.on('filter', function (selection) {
                that.mapHandler.update(selection);
                that.statusPie.updateWith();
                that.sectorsPie.updateWith();
                that.updateHash();
            });

            d3.selectAll('.tabs a').on('click', function () {
                d3.event.preventDefault();
                that.showTab(this.getAttribute('href'));
                that.updateHash();
            });

            this.buildFilter('status', 'Statut', projects.getStatusValue, 'radio');
            this.buildFilter('sectors', 'Secteurs', projects.getSectorsValues);
            this.buildFilter('orgs', 'Organisations', projects.getOrgsValues);
            this.buildFilter('topics', 'Thèmes', projects.getTopicsValues);
            this.listenHash();
            return this;
        },

        renderProject: function (d) {
            var content = '';
            content += "<h4><a href='" + d.url + "''>" + d.name + "</a> <small>[" + d.id + "]</small></h4>";
            content += "<div>Financement: " + d.budget + " €</div>";
            content += "<div>Statut: " + d.status + "</div>";
            content += "<div>Source: " + d.source.name + "</div>";
            content += "<hr />";
            return content;
        },

        filterProject: function (d) {
            for (var i = 0; i < this.filters.length; i++) {
                if (!HELPERS.projectPassFilter(d, this.filters[i])) {
                    return 'none';
                }
            }
            return null;
        },

        filter: function () {
            this.list.style('display', HELPERS.bind(this.filterProject, this));
            this.dispatch.filter(this.visibleData());
        },

        visible: function () {
            return this.list.filter(HELPERS.isVisible);
        },

        visibleData: function () {
            return this.visible().data();
        },

        computeStats: function (key, prop) {
            var values = d3.map(), sector;
            var increment = function (key) {
                if (prop) {
                    key = key[prop];
                }
                if (!values.has(key)) {
                    values.set(key, {
                        value: 0,
                        label: key
                    });
                }
                values.get(key).value++;
            };
            this.visible().each(function (d) {
                if (d[key] instanceof Array) {
                    for (var i = 0; i < d[key].length; i++) {
                        increment(d[key][i]);
                    }
                } else {
                    increment(d[key]);
                }
            });
            return values.values();
        },

        buildFilter: function (prop, text, accessor, type) {
            var values = d3.set(this.visibleData().flattenMap(accessor)).values(),
                container = d3.select('#piatiFilters').append('fieldset'),
                that = this;
            container.node().id = prop + "Filter";
            container.append('legend').text(text).on('click', function () {
                d3.select(this.parentNode).classed('on', function () { return !d3.select(this).classed('on');});
            });
            var labels = container.selectAll('label').data(values);
            labels.enter().append('label');
            labels.html(function (d) {return "<span> " + d + "</span>";});
            var inputs = labels.insert('input', 'span').attr('type', type || 'checkbox').attr('name', prop).attr('value', function (d) {return d;}).on('change', HELPERS.bind(this.filter, this));
            if (type === "radio") {
                container.append('label').append('small').text('Tout décocher').on('click', function () {
                    inputs.each(function () {
                        this.checked = false;
                        that.filter();
                    });
                });
            }
            this.dispatch.on('filter.' + prop, function (selection) {
                var values = d3.set(selection.flattenMap(accessor));
                labels.classed('inactive', function (d) {return values.has(d) ? false : true;});
            });
        },

        updateHash: function () {
            var tab = d3.select('.tab-content.on').node().id.substr(4);
            var checkedToParam = function (id) {
                return d3.selectAll('#' + id + 'Filter input:checked').data().map(function (d) {
                    return id + '=' + encodeURIComponent(d);
                });
            };
            var params = [];
            for (var i = 0; i < this.filters.length; i++) {
                params = params.concat(checkedToParam(this.filters[i]));
            }
            window.location.hash = tab + (params.length ? '?' + params.join('&') : '');
        },

        listenHash: function () {
            var hash = window.location.hash.substr(1).split('?'),
                tab = hash[0] || 'data';
            this.showTab('#tab-' + tab);
            var checkFromParam = function (param) {
                param = param.split('=');
                var node = d3.select('#' + param[0] + 'Filter input[value="' + decodeURIComponent(param[1]) + '"]').node();
                if (node) {
                    node.checked = true;
                    d3.select(node.parentNode.parentNode).classed('on', true);
                }
            };
            if (hash[1]) {
                var params = hash[1].split('&');
                for (var i = 0; i < params.length; i++) {
                    checkFromParam(params[i]);
                }
                this.filter();
            }
        },

        showTab: function (id) {
            d3.selectAll('.tab-content').classed('on', false);
            d3.selectAll('.tabs a').classed('on', false);
            d3.select(".tabs a[href='" + id + "']").classed('on', true);
            d3.select(id).classed('on', true);
            this.mapHandler.map.invalidateSize();
        }

    };

    var HELPERS = {

        bind: function (fn, obj) {
            var args = arguments.length > 2 ? Array.prototype.slice.call(arguments, 2) : null;
            return function () {
                return fn.apply(obj, args || arguments);
            };
        },

        isVisible: function (d) {
            return this.style.display !== "none";
        },

        idFromProperty: function (prop) {
            return '#' + prop + 'Filter';
        },

        projectPassFilter: function (d, key) {
            var selector = HELPERS.idFromProperty(key),
                values = d3.set(d3.select(selector).selectAll('input').filter(function () {return this.checked;}).data()),
                pass = true, value;
            if (values.values().length) {
                if (d[key] instanceof Array) {
                    pass = false;
                    for (var i = 0; i < d[key].length; i++) {
                        if (d[key][i] === null) { continue; }
                        value = typeof d[key][i] === "object" ? d[key][i].name : d[key][i];
                        if (values.has(value)) {
                            pass = true;
                            break;
                        }
                    }
                } else {
                    pass = values.has(d[key]);
                }
            }
            return pass;
        }

    };

    return API.init(options);
}

