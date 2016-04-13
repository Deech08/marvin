/*
* @Author: Brian Cherinka
* @Date:   2016-04-13 16:49:00
* @Last Modified by:   Brian
* @Last Modified time: 2016-04-13 17:45:08
*/

//
// Javascript Galaxy object handling JS things for a single galaxy
//

'use strict';

class Galaxy {

    // Constructor
    constructor(plateifu) {
        this.setPlateIfu(plateifu);
        this.maindiv = $('#'+this.plateifu);
        this.mapdiv = this.maindiv.find('#map');
        this.specdiv = this.maindiv.find('#graphdiv');
        this.specmsg = this.maindiv.find('#specmsg');
        this.webspec = null;
        this.staticdiv = this.maindiv.find('#staticdiv');
        this.dynamicdiv = this.maindiv.find('#dynamicdiv');
        this.togglediv = $('#toggleinteract');
    }

    // Test print
    print() {
        console.log('We are now printing galaxy', this.plateifu, this.plate, this.ifu);
    }

    // Set the plateifu
    setPlateIfu(plateifu) {
        if (plateifu === undefined) {
            this.plateifu = $('.galinfo').attr('id');
        } else {
            this.plateifu = plateifu;
        }
        [this.plate, this.ifu] = this.plateifu.split('-');
    }

    // Initialize and Load a DyGraph spectrum
    loadSpaxel(spaxel) {
        this.webspec = new Dygraph(this.specdiv[0],
                  spaxel,
                  {
                    labels: ['x','Flux'],
                    errorBars: true
                  });
    };

    // Update a DyGraph spectrum
    updateSpaxel(spaxel, specmsg) {
        var newmsg = "Here's a spectrum: "+specmsg;
        this.specmsg.empty();
        this.specmsg.html(newmsg);
        this.webspec.updateOptions({'file': spaxel});
    };

    // Initialize OpenLayers Map
    initOpenLayers(image) {
        this.image = image;
        this.olmap = new OLMap(image);
        // add click event handler on map to get spaxel
        this.olmap.map.on('singleclick', this.getSpaxel, this);
    };

    // Retrieves a new Spaxel from the server based on a given mouse position
    getSpaxel(event) {
        var map = event.map;
        var mousecoords = event.coordinate;
        var keys = ['plateifu', 'image', 'imwidth', 'imheight', 'mousecoords'];
        var form = m.utils.buildForm(keys, this.plateifu, this.image, this.olmap.imwidth, this.olmap.imheight, mousecoords);
        var _this = this;

        // send the form data
        $.post(Flask.url_for('galaxy_page.getspaxel'), form,'json')
            .done(function(data) {
                $('#mouse-output').empty()
                var myhtml = "<h5>My mouse coords "+mousecoords+", message: "+data.result.message+"</h5>"
                $('#mouse-output').html(myhtml);
                _this.updateSpaxel(data.result.spectra, data.result.specmsg);
            })
            .fail(function(data) {
                $('#mouse-output').empty()
                var myhtml = "<h5>Error message: "+data.result.message+"</h5>"
                $('#mouse-output').html(myhtml);
            });
    };

    // Toggle the interactive OpenLayers map and Dygraph spectra
    toggleInteract(spaxel, image) {
        if (this.togglediv.hasClass('active')){
            this.togglediv.button('reset');
            this.dynamicdiv.hide();
            this.staticdiv.show();
        } else {
            this.togglediv.button('complete');
            this.staticdiv.hide();
            this.dynamicdiv.show();

            // check for empty divs
            var specempty = this.specdiv.is(':empty');
            var mapempty = this.mapdiv.is(':empty');
            // load the spaxel if the div is initially empty;
            if (this.specdiv !== undefined && specempty) {
                this.loadSpaxel(spaxel);
            }

            // load the map if div is empty
            if (mapempty) {
                this.initOpenLayers(image);
            }

        }
    };
}

