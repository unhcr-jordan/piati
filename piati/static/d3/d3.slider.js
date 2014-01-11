d3.slider = function module(el, options) {
    "use strict";

    function stop() {
        d3.event.stopPropagation();
    }
    var formatPercent = d3.format(".2%"),
        tickFormat = d3.format(".0");

    var API = {

        init: function (el, options) {
            var that = this;
            this.min = options.min || 0;
            this.max = options.max || 100;
            this.step = options.step || 0.01;
            this.from = options.from || this.min;
            this.to = options.to || this.max;
            this.dispatch = d3.dispatch("slide", "slideend");
            this.container = d3.select(el).classed("d3-slider d3-slider-horizontal", true);
            this.scale = d3.scale.linear().domain([this.min, this.max]);
            this.drag = d3.behavior.drag();
            this.build();
            this.set();
            this.drag.on('dragend', function () {that.dispatch.slideend(d3.event, that.from, that.to);});
            this.drag.on("drag", function () { that.onDrag();});
            // this.container.on("click", function () {that.onClick();});
            d3.rebind(this, this.dispatch, "on");
            return this;
        },

        build: function () {
            this.handleFrom = this.container.append("a")
                .classed("d3-slider-handle", true)
                .attr("xlink:href", "#")
                .attr('id', "handle-from")
                .on("click", stop)
                .call(this.drag);
            this.handleTo = this.container.append("a")
                .classed("d3-slider-handle", true)
                .attr('id', "handle-to")
                .attr("xlink:href", "#")
                .on("click", stop)
                .call(this.drag);
            this.divRange = this.container.append('div').classed("d3-slider-range", true);
        },

        set: function (from, to) {
            if (!isNaN(from)) {
                this.from = from;
            }
            if (!isNaN(to)) {
                this.to = to;
            }
            this.handleFrom.style("left", formatPercent(this.scale(this.from)));
            this.divRange.style("left", formatPercent(this.scale(this.from)));
            this.handleTo.style("left", formatPercent(this.scale(this.to)));
            this.divRange.style("right", 100 - parseFloat(formatPercent(this.scale(this.to))) + "%");
        },

        stepValue: function (val) {
            // Calculate nearest step value
            if (val === this.scale.domain()[0] || val === this.scale.domain()[1]) {
                return val;
            }
            var valModStep = (val - this.scale.domain()[0]) % this.step,
                alignValue = val - valModStep;
            if (Math.abs(valModStep) * 2 >= this.step) {
                alignValue += (valModStep > 0) ? this.step : -this.step;
            }
            return alignValue;
        },

        size: function () {
            return parseInt(this.container.style("width"), 10);
        },

        onClick: function () {
            // if (!values.length) {
            //     this.onMove(d3.event.offsetX || d3.event.layerX);
            // }
        },

        onDrag: function () {
            var active = d3.event.sourceEvent.target.id.substr(7);
            if (active === "from" || active === "to") {
                this.active = active;
            }
            this.onMove(Math.max(0, Math.min(this.size(), d3.event.x)));
        },

        onMove: function (pos) {
            if ( this.from >= this.to ) return;
            var newValue = this.stepValue(this.scale.invert(pos / this.size()));

            if (this[this.active] !== newValue) {
                var newPos = formatPercent(this.scale(this.stepValue(newValue)));
                this[this.active] = newValue;
                this.dispatch.slide(d3.event, this.from, this.to);

                if ( this.active === 'from' ) {
                    this.divRange.style("left", newPos);
                    this.handleFrom.style('left', newPos);
                } else {
                    this.divRange.style('right', (100 - parseFloat(newPos)) + "%");
                    this.handleTo.style('left', newPos);
                }
            }
        }


    };

    return API.init(el, options);

};