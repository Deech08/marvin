#!/usr/bin/env python
# encoding: utf-8

'''
Created by Brian Cherinka on 2016-04-08 14:31:34
Licensed under a 3-clause BSD license.

Revision History:
    Initial Version: 2016-04-08 14:31:34 by Brian Cherinka
    Last Modified On: 2016-04-08 14:31:34 by Brian

'''
from __future__ import print_function
from __future__ import division
from flask import Blueprint, render_template, session as current_session, request, jsonify
from flask_classy import FlaskView, route
from brain.api.base import processRequest
from marvin.utils.general.general import convertImgCoords, parseIdentifier, getDefaultMapPath, getDapRedux
from brain.utils.general.general import convertIvarToErr
from marvin.core.exceptions import MarvinError
from marvin.tools.cube import Cube
from marvin.tools.maps import _get_bintemps, _get_bintype, _get_template_kin
from marvin.utils.dap.datamodel import get_dap_maplist, get_default_mapset
from marvin.web.web_utils import parseSession
import os

try:
    from sdss_access.path import Path
except ImportError as e:
    Path = None

galaxy = Blueprint("galaxy_page", __name__)


def getWebSpectrum(cube, x, y, xyorig=None, byradec=False):
    ''' Get and format a spectrum for the web '''
    webspec = None
    try:
        if byradec:
            spaxel = cube.getSpaxel(ra=x, dec=y, xyorig=xyorig, modelcube=True, properties=False)
        else:
            spaxel = cube.getSpaxel(x=x, y=y, xyorig=xyorig, modelcube=True, properties=False)
    except Exception as e:
        specmsg = 'Could not get spaxel: {0}'.format(e)
    else:
        # get error and wavelength
        error = convertIvarToErr(spaxel.spectrum.ivar)
        wave = spaxel.spectrum.wavelength

        # try to get the model flux
        try:
            modelfit = spaxel.model.flux
        except Exception as e:
            modelfit = None

        # make input array for Dygraph
        if not isinstance(modelfit, type(None)):
            webspec = [[wave[i], [s, error[i]], [modelfit[i], 0.0]] for i, s in enumerate(spaxel.spectrum.flux)]
        else:
            webspec = [[wave[i], [s, error[i]]] for i, s in enumerate(spaxel.spectrum.flux)]

        specmsg = "Spectrum in Spaxel ({2},{3}) at RA, Dec = ({0}, {1})".format(x, y, spaxel.x, spaxel.y)

    return webspec, specmsg


def getWebMap(cube, parameter='emline_gflux', channel='ha_6564',
              bintype=None, template_kin=None, template_pop=None):
    ''' Get and format a map for the web '''
    name = '{0}_{1}'.format(parameter.lower(), channel)
    webmap = None
    try:
        maps = cube.getMaps(plateifu=cube.plateifu, mode='local',
                            bintype=bintype, template_kin=template_kin)
        data = maps.getMap(parameter, channel=channel)
    except Exception as e:
        mapmsg = 'Could not get map: {0}'.format(e)
    else:
        vals = data.value
        ivar = data.ivar  # TODO
        mask = data.mask  # TODO
        # TODO How does highcharts read in values? Pass ivar and mask with webmap.
        webmap = {'values': [list(it) for it in data.value],
                  'ivar': [list(it) for it in data.ivar] if data.ivar is not None else None,
                  'mask': [list(it) for it in data.mask] if data.mask is not None else None}
        # webmap = [[ii, jj, vals[ii][jj]] for ii in range(len(vals)) for jj in range(len(vals[0]))]
        mapmsg = "{0}: {1}-{2}".format(name, maps.bintype, maps.template_kin)
    return webmap, mapmsg


def buildMapDict(cube, params, bintemp=None):
    ''' Build a list of dictionaries of maps

    params - list of string parameter names in form of category_channel

        NOT GENERALIZED
    '''
    # split the bintemp
    if bintemp:
        bintype, temp = bintemp.split('-', 1)
    else:
        bintype, temp = (None, None)

    mapdict = []
    params = params if type(params) == list else [params]
    for param in params:
        param = str(param)
        try:
            parameter, channel = param.split(':')
        except ValueError as e:
            parameter, channel = (param, None)
        webmap, mapmsg = getWebMap(cube, parameter=parameter, channel=channel,
                                   bintype=bintype, template_kin=temp)
        mapdict.append({'data': webmap, 'msg': mapmsg})

    anybad = [m['data'] is None for m in mapdict]
    if any(anybad):
        raise MarvinError('Could not get map for one of supplied parameters')

    return mapdict


class Galaxy(FlaskView):
    route_base = '/galaxy'

    def __init__(self):
        ''' Initialize the route '''
        self.galaxy = {}
        self.galaxy['title'] = 'Marvin | Galaxy'
        self.galaxy['page'] = 'marvin-galaxy'
        self.galaxy['error'] = None
        self.galaxy['specmsg'] = None
        self.galaxy['mapmsg'] = None

    def before_request(self, *args, **kwargs):
        ''' Do these things before a request to any route '''
        self.galaxy['error'] = None
        self.galaxy['cube'] = None
        self.galaxy['image'] = ''
        self.galaxy['spectra'] = 'null'
        self.galaxy['maps'] = None
        self._drpver, self._dapver, self._release = parseSession()

    def index(self):
        ''' Main galaxy page '''
        self.galaxy['error'] = 'Not all there are you...  Try adding a plate-IFU or manga-ID to the end of the address.'
        return render_template("galaxy.html", **self.galaxy)

    def get(self, galid):
        ''' Retrieve info for a given cube '''

        # determine type of galid
        self.galaxy['id'] = galid
        idtype = parseIdentifier(galid)
        if idtype in ['plateifu', 'mangaid']:
            # set plateifu or mangaid
            self.galaxy['idtype'] = idtype
            galaxyid = {self.galaxy['idtype']: galid, 'release': self._release}

            # Get cube
            try:
                print('marvin config', self._release, self._dapver, self._dapver)
                cube = Cube(**galaxyid)
            except MarvinError as e:
                self.galaxy['cube'] = None
                self.galaxy['error'] = 'MarvinError: {0}'.format(e)
                return render_template("galaxy.html", **self.galaxy)
            else:
                self.galaxy['cube'] = cube
                self.galaxy['daplink'] = getDapRedux(release=self._release)
                # get SAS url links to cube, rss, maps, image
                if Path:
                    sdss_path = Path()
                    self.galaxy['image'] = sdss_path.url('mangaimage', drpver=cube._drpver, plate=cube.plate, ifu=cube.ifu, dir3d=cube.dir3d)
                    cubelink = sdss_path.url('mangacube', drpver=cube._drpver, plate=cube.plate, ifu=cube.ifu)
                    rsslink = sdss_path.url('mangarss', drpver=cube._drpver, plate=cube.plate, ifu=cube.ifu)
                    maplink = getDefaultMapPath(release=self._release, plate=cube.plate, ifu=cube.ifu, daptype='SPX-GAU-MILESHC', mode='MAPS')
                    self.galaxy['links'] = {'cube': cubelink, 'rss': rsslink, 'map': maplink}
                else:
                    self.galaxy['image'] = cube.data.image

            # Get the initial spectrum
            if cube:
                webspec, specmsg = getWebSpectrum(cube, cube.ra, cube.dec, byradec=True)
                # temporarily do version stuff
                #
                daplist = get_dap_maplist(self._dapver, web=True)
                dapdefaults = get_default_mapset(self._dapver)

                # build the uber map dictionary
                try:
                    mapdict = buildMapDict(cube, dapdefaults)
                    mapmsg = None
                except Exception as e:
                    mapdict = [{'data': None, 'msg': 'Error'} for m in dapdefaults]
                    mapmsg = 'Error getting maps: {0}'.format(e)

                if not webspec:
                    self.galaxy['error'] = 'Error: {0}'.format(specmsg)
                self.galaxy['cube'] = cube
                self.galaxy['spectra'] = webspec
                self.galaxy['specmsg'] = specmsg
                self.galaxy['cubehdr'] = cube.header
                self.galaxy['quality'] = cube.qualitybit
                self.galaxy['mngtarget'] = cube.targetbit
                self.galaxy['maps'] = mapdict
                self.galaxy['mapmsg'] = mapmsg
                self.galaxy['dapmaps'] = daplist
                self.galaxy['dapbintemps'] = _get_bintemps(self._dapver)
                current_session['bintemp'] = '{0}-{1}'.format(_get_bintype(self._dapver), _get_template_kin(self._dapver))
                # TODO - make this general - see also search.py for querystr
                self.galaxy['cubestr'] = ("<html><samp>from marvin.tools.cube import Cube<br>cube = \
                    Cube(plateifu='{0}')<br># get a spaxel<br>spaxel=cube[16,16]<br></samp></html>".format(cube.plateifu))
                self.galaxy['mapstr'] = ("<html><samp>from marvin.tools.cube import Cube<br>cube = \
                    Cube(plateifu='{0}')<br># get maps<br>maps=cube.getMaps()<br># or another way <br>\
                    from marvin.tools.maps import Maps<br>maps = Maps(plateifu='{0}')<br># get an emission \
                    line map<br>haflux = maps.getMap('emline_gflux', channel='ha_6564')<br></samp></html>".format(cube.plateifu))
        else:
            self.galaxy['error'] = 'Error: Galaxy ID {0} must either be a Plate-IFU, or MaNGA-Id designation.'.format(galid)
            return render_template("galaxy.html", **self.galaxy)

        return render_template("galaxy.html", **self.galaxy)

    @route('getspaxel', methods=['POST'], endpoint='getspaxel')
    def getSpaxel(self):
        f = processRequest(request=request)
        print('spaxelform', f)
        self._drpver, self._dapver, self._release = parseSession()
        cubeinputs = {'plateifu': f['plateifu'], 'release': self._release}
        maptype = f.get('type', None)

        if maptype == 'optical':
            # for now, do this, but TODO - general processRequest to handle lists and not lists
            try:
                mousecoords = [float(v) for v in f.get('mousecoords[]', None)]
            except:
                mousecoords = None

            if mousecoords:
                pixshape = (int(f['imwidth']), int(f['imheight']))
                if (mousecoords[0] < 0 or mousecoords[0] > pixshape[0]) or (mousecoords[1] < 0 or mousecoords[1] > pixshape[1]):
                    output = {'specmsg': 'Error: requested pixel coords are outside the image range.', 'status': -1}
                    self.galaxy['error'] = output['specmsg']
                else:
                    # TODO - generalize image file sas_url to filesystem switch, maybe in sdss_access
                    infile = os.path.join(os.getenv('MANGA_SPECTRO_REDUX'), f['image'].split('redux/')[1])
                    arrcoords = convertImgCoords(mousecoords, infile, to_radec=True)

                    cube = Cube(**cubeinputs)
                    webspec, specmsg = getWebSpectrum(cube, arrcoords[0], arrcoords[1], byradec=True)
                    if not webspec:
                        self.galaxy['error'] = 'Error: {0}'.format(specmsg)
                        status = -1
                    else:
                        status = 1
                    msg = 'gettin some spaxel at RA/Dec {0}'.format(arrcoords)
                    output = {'message': msg, 'specmsg': specmsg, 'spectra': webspec, 'status': status}
            else:
                output = {'specmsg': 'Error getting mouse coords', 'status': -1}
                self.galaxy['error'] = output['specmsg']
        elif maptype == 'heatmap':
            # grab spectrum based on (x, y) coordinates
            x = int(f.get('x')) if 'x' in f.keys() else None
            y = int(f.get('y')) if 'y' in f.keys() else None
            if all([x, y]):
                cube = Cube(**cubeinputs)
                webspec, specmsg = getWebSpectrum(cube, x, y, xyorig='lower')
                msg = 'gettin some spaxel with (x={0}, y={1})'.format(x, y)
                if not webspec:
                    self.galaxy['error'] = 'Error: {0}'.format(specmsg)
                    status = -1
                else:
                    status = 1
                output = {'message': msg, 'specmsg': specmsg, 'spectra': webspec, 'status': status}
            else:
                output = {'specmsg': 'Error: X or Y not specified for map', 'status': -1}
                self.galaxy['error'] = output['specmsg']
        else:
            output = {'specmsg': 'Error: No maptype specified in request', 'status': -1}
            self.galaxy['error'] = output['specmsg']

        return jsonify(result=output)

    @route('updatemaps', methods=['POST'], endpoint='updatemaps')
    def updateMaps(self):
        self._drpver, self._dapver, self._release = parseSession()
        f = processRequest(request=request)
        cubeinputs = {'plateifu': f['plateifu'], 'release': self._release}
        params = f.get('params[]', None)
        bintemp = f.get('bintemp', None)
        current_session['bintemp'] = bintemp
        # get cube (self.galaxy['cube'] does not work)
        try:
            cube = Cube(**cubeinputs)
        except Exception as e:
            cube = None
        # Try to make the web maps
        if not cube:
            output = {'mapmsg': 'No cube found', 'maps': None, 'status': -1}
        elif not params:
            output = {'mapmsg': 'No parameters selected', 'maps': None, 'status': -1}
        else:
            try:
                mapdict = buildMapDict(cube, params, bintemp=bintemp)
            except Exception as e:
                output = {'mapmsg': e.message, 'status': -1, 'maps': None}
            else:
                output = {'mapmsg': None, 'status': 1, 'maps': mapdict}
        return jsonify(result=output)

Galaxy.register(galaxy)