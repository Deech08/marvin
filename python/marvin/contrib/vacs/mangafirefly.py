# !usr/bin/env python
# -*- coding: utf-8 -*-
#
# Licensed under a 3-clause BSD license.
#
# @Author: Brian Cherinka
# @Date:   2018-10-11 17:51:43
# @Last modified by:   Brian Cherinka
# @Last Modified time: 2018-11-29 17:23:15

from __future__ import print_function, division, absolute_import

import numpy as np
import astropy
import astropy.units as u
import marvin.tools
from marvin.tools.quantities.spectrum import Spectrum
from marvin.utils.general.general import get_drpall_table
from marvin.utils.plot.scatter import plot as scatplot

from .base import VACMixIn


class FIREFLYVAC(VACMixIn):
    """Provides access to the MaNGA-FIREFLY VAC.

    VAC name: FIREFLY

    URL: 

    Description: Returns integrated and resolved stellar population parameters fitted by FIREFLY

    Authors: Jianhui Lian, Daniel Thomas, Claudia Maraston, and Lewis Hill

    """

    # Required parameters
    name = 'mangaffly'
    description = 'Returns stellar population parameters fitted by FIREFLY'
    version = 'v1_1_2'
               
    drpver = 'v2_4_3'

    # optional Marvin Tools to attach your vac to
    include = (marvin.tools.cube.Cube,
               marvin.tools.maps.Maps,
               marvin.tools.modelcube.ModelCube)

    # Required method
    def get_data(self):

        # define the variables to build a unique path to your VAC file
        path_params = {'ver': self.version,'drpver': self.drpver 
                       }

        # get_path returns False if the files do not exist locally
        allfile = self.get_path('mangaffly', path_params=path_params)

        # download the vac from the SAS if it does not already exist locally
        if not allfile:
            allfile = self.download_vac('mangaffly', path_params=path_params)

        #Returns the FITS data from the mangafirefly summary file 
        ffly = astropy.io.fits.getdata(allfile)

        return ffly


