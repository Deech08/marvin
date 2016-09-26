#!/usr/bin/env python
# encoding: utf-8
#
# test_modelcube.py
#
# Created by José Sánchez-Gallego on 25 Sep 2016.


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import os
import unittest

from astropy.io import fits
from astropy.wcs import WCS

import marvin
import marvin.tests

from marvin.core import MarvinError
from marvin.tools.cube import Cube
from marvin.tools.maps import Maps
from marvin.tools.modelcube import ModelCube


class TestModelCubeBase(marvin.tests.MarvinTest):
    """Defines the files and plateifus we will use in the tests."""

    @classmethod
    def setUpClass(cls):

        cls.drpver = 'v2_0_1'
        cls.dapver = '2.0.2'

        cls.plate = 8485
        cls.ifu = 1901
        cls.mangaid = '1-209232'
        cls.plateifu = '8485-1901'

        cls.bintype = 'SPX'
        cls.template_kin = 'GAU-MILESHC'

        cls.filename = os.path.join(
            os.getenv('MANGA_SPECTRO_ANALYSIS'), cls.drpver, cls.dapver,
            cls.bintype + '-' + cls.template_kin, str(cls.plate), str(cls.ifu),
            'manga-{0}-LOGCUBE-{1}-{2}.fits.gz'.format(cls.plateifu,
                                                       cls.bintype,
                                                       cls.template_kin))

        cls.marvindb_session = marvin.marvindb.session

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):

        marvin.marvindb.session = self.marvindb_session
        marvin.config.setMPL('MPL-5')
        self.assertTrue(os.path.exists(self.filename))

    def tearDown(self):
        pass


class TestModelCubeInit(TestModelCubeBase):

    def _test_init(self, model_cube, bintype='SPX', template_kin='GAU-MILESHC'):

        self.assertEqual(model_cube._drpver, self.drpver)
        self.assertEqual(model_cube._dapver, self.dapver)
        self.assertEqual(model_cube.bintype, bintype)
        self.assertEqual(model_cube.template_kin, template_kin)
        self.assertEqual(model_cube.plateifu, self.plateifu)
        self.assertEqual(model_cube.mangaid, self.mangaid)
        self.assertIsInstance(model_cube.header, fits.Header)
        self.assertIsInstance(model_cube.wcs, WCS)
        self.assertIsNotNone(model_cube.wavelength)
        self.assertIsNotNone(model_cube.redcorr)

    def test_init_from_file(self):

        model_cube = ModelCube(filename=self.filename)
        self.assertEqual(model_cube.data_origin, 'file')
        self._test_init(model_cube)

    def test_init_from_db(self):

        model_cube = ModelCube(plateifu=self.plateifu)
        self.assertEqual(model_cube.data_origin, 'db')
        self._test_init(model_cube)

    def test_init_from_api(self):

        model_cube = ModelCube(plateifu=self.plateifu, mode='remote')
        self.assertEqual(model_cube.data_origin, 'api')
        self._test_init(model_cube)

    def test_raises_exception_mpl4(self):

        marvin.config.setMPL('MPL-4')
        with self.assertRaises(MarvinError) as err:
            __ = ModelCube(plateifu=self.plateifu)
        self.assertEqual('ModelCube requires at least dapver=\'2.0.2\'',  str(err.exception))

    def test_init_from_db_not_default(self):

        model_cube = ModelCube(plateifu=self.plateifu, bintype='NRE')
        self.assertEqual(model_cube.data_origin, 'db')
        self._test_init(model_cube, bintype='NRE')

    def test_init_from_api_not_default(self):

        model_cube = ModelCube(plateifu=self.plateifu, bintype='NRE', mode='remote')
        self.assertEqual(model_cube.data_origin, 'api')
        self._test_init(model_cube, bintype='NRE')

    def test_get_flux_db(self):

        model_cube = ModelCube(plateifu=self.plateifu)
        self.assertTupleEqual(model_cube.flux.shape, (4563, 34, 34))

    def test_get_flux_api_raises_exception(self):

        model_cube = ModelCube(plateifu=self.plateifu, mode='remote')
        with self.assertRaises(MarvinError) as err:
            __ = model_cube.flux
        self.assertIn('cannot return a full cube in remote mode.',  str(err.exception))

    def test_get_cube_file(self):

        model_cube = ModelCube(filename=self.filename)
        self.assertIsInstance(model_cube.cube, Cube)

    def test_get_maps_api(self):

        model_cube = ModelCube(plateifu=self.plateifu, mode='remote')
        self.assertIsInstance(model_cube.maps, Maps)


class TestGetSpaxel(TestModelCubeBase):

    def _test_getspaxel(self, spaxel, bintype='SPX', template_kin='GAU-MILESHC'):

        self.assertEqual(spaxel._drpver, self.drpver)
        self.assertEqual(spaxel._dapver, self.dapver)
        self.assertEqual(spaxel.plateifu, self.plateifu)
        self.assertEqual(spaxel.mangaid, self.mangaid)
        self.assertIsNotNone(spaxel.modelcube)
        self.assertEqual(spaxel.modelcube.bintype, bintype)
        self.assertEqual(spaxel.modelcube.template_kin, template_kin)
        self.assertTupleEqual(spaxel._parent_shape, (34, 34))

        self.assertIsNotNone(spaxel.model_flux)
        self.assertIsNotNone(spaxel.model)
        self.assertIsNotNone(spaxel.emline)
        self.assertIsNotNone(spaxel.emline_base)
        self.assertIsNotNone(spaxel.stellar_continuum)
        self.assertIsNotNone(spaxel.redcorr)

    def test_getspaxel_file(self):

        model_cube = ModelCube(filename=self.filename)
        spaxel = model_cube.getSpaxel(x=1, y=2)
        self._test_getspaxel(spaxel)

    def test_getspaxel_db(self):

        model_cube = ModelCube(plateifu=self.plateifu)
        spaxel = model_cube.getSpaxel(x=1, y=2)
        self._test_getspaxel(spaxel)

    def test_getspaxel_api(self):

        model_cube = ModelCube(plateifu=self.plateifu, mode='remote')
        spaxel = model_cube.getSpaxel(x=1, y=2)
        self._test_getspaxel(spaxel)

    def test_getspaxel_db_only_model(self):

        model_cube = ModelCube(plateifu=self.plateifu)
        spaxel = model_cube.getSpaxel(x=1, y=2, properties=False, spectrum=False)
        self._test_getspaxel(spaxel)
        self.assertIsNone(spaxel.cube)
        self.assertIsNone(spaxel.spectrum)
        self.assertIsNone(spaxel.maps)
        self.assertEqual(len(spaxel.properties), 0)


if __name__ == '__main__':
    # set to 1 for the usual '...F..' style output, or 2 for more verbose output.
    verbosity = 2
    unittest.main(verbosity=verbosity)
