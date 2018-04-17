#!/usr/bin/env python
# encoding: utf-8

'''
Created by Brian Cherinka on 2016-05-02 16:16:27
Licensed under a 3-clause BSD license.

Revision History:
    Initial Version: 2016-05-02 16:16:27 by Brian Cherinka
    Last Modified On: 2016-05-02 16:16:27 by Brian

'''
from __future__ import print_function
from __future__ import division
from flask import session as current_session, request, current_app
from marvin import config
from collections import defaultdict
import flask_featureflags as feature
import re


def configFeatures(app):
    ''' Configure Flask Feature Flags '''

    app.config['FEATURE_FLAGS']['public'] = True if config.access == 'public' else False


def check_access():
    ''' Check the access mode in the session '''

    # check if on public server
    # public_server = request.environ.get('PUBLIC_SERVER', None) == 'True'
    # public_flag = public_server or current_app.config['FEATURE_FLAGS']['public']
    # current_app.config['FEATURE_FLAGS']['public'] = public_server
    public_access = config.access == 'public'
    # print('public_flag', public_flag, public_access)

    # if public_flag:
    #     config.access = 'public'
    #     return
    print('checking access')
    user = current_session['user'] = request.environ.get('REMOTE_USER', None)

    print('auth user', user, public_access)
    if not user and not public_access:
        config.access = 'public'
    elif user and public_access:
        config.access = 'collab'

    #clear_session_versions()
    # check for logged in status
    # logged_in = current_session.get('loginready', None)
    # if not logged_in and not public_access:
    #     config.access = 'public'
    # elif logged_in is True and public_access:
    #     config.access = 'collab'


def update_allowed():
    ''' Update the allowed versions '''
    mpls = list(config._allowed_releases.keys())
    versions = [{'name': mpl, 'subtext': str(config.lookUpVersions(release=mpl))} for mpl in mpls]
    return versions


def set_session_versions(version):
    ''' Set the versions in the session '''
    current_session['release'] = version
    drpver, dapver = config.lookUpVersions(release=version)
    current_session['drpver'] = drpver
    current_session['dapver'] = dapver

def clear_session_versions():
    ''' Clear the versions in a session '''
    print('clearing session')
    keys = ['versions', 'release', 'drpver', 'dapver']
    for key in keys:
        if key in current_session:
            tmp = current_session.pop(key)


def updateGlobalSession():
    ''' updates the Marvin config with the global Flask session '''
    print('updating session')
    # check if mpl versions in session
    if 'versions' not in current_session:
        setGlobalSession()
    elif 'drpver' not in current_session or \
         'dapver' not in current_session:
        set_session_versions(config.release)
    elif 'release' not in current_session:
        current_session['release'] = config.release
    # elif 'user' in current_session:
    #     versions = update_allowed()
    #     if not current_session['user']:
    #         current_session['versions'] = [v for v in versions if 'MPL' not in v]
    #     else:
    #         current_session['versions'] = versions
    # elif feature.is_active('public'):
    #     current_session['versions'] = update_allowed()
    # elif 'access' not in current_session:
    #     current_session['access'] = config.access
    # else:
    #     # update versions based on access
    #     current_session['versions'] = update_allowed()

def setGlobalSession():
    ''' Sets the global session for Flask '''

    # mpls = list(config._allowed_releases.keys())
    # versions = [{'name': mpl, 'subtext': str(config.lookUpVersions(release=mpl))} for mpl in mpls]
    current_session['versions'] = update_allowed()

    if 'release' not in current_session:
        set_session_versions(config.release)


def parseSession():
    ''' parse the current session for MPL versions '''
    drpver = current_session['drpver']
    dapver = current_session['dapver']
    release = current_session['release']
    return drpver, dapver, release


def buildImageDict(imagelist, test=None, num=16):
    ''' Builds a list of dictionaries from a sdss_access return list of images '''

    # get thumbnails and plateifus
    if imagelist:
        thumbs = [imagelist.pop(imagelist.index(t)) if 'thumb' in t else t for t in imagelist]
        plateifu = ['-'.join(re.findall('\d{3,5}', im)) for im in imagelist]

    # build list of dictionaries
    images = []
    if imagelist:
        for i, image in enumerate(imagelist):
            imdict = defaultdict(str)
            imdict['name'] = plateifu[i]
            imdict['image'] = image
            imdict['thumb'] = thumbs[i] if thumbs else None
            images.append(imdict)
    elif test and not imagelist:
        for i in xrange(num):
            imdict = defaultdict(str)
            imdict['name'] = '4444-0000'
            imdict['image'] = 'http://placehold.it/470x480&text={0}'.format(i)
            imdict['thumb'] = 'http://placehold.it/150x150&text={0}'.format(i)
            images.append(imdict)

    return images
