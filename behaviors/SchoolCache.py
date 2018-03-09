#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '4/3/15'


from tornado import gen
from Behavior import Behavior
import settings
import logging
import pickle


class SchoolCache(Behavior):
    def __init__(self):
        super(SchoolCache, self).__init__()
        self._rpcs = None
        self._id_to_rpcs = None
        self._regions = None

    @staticmethod
    def Instance():
        if not hasattr(SchoolCache, '_instance'):
            SchoolCache._instance = SchoolCache()
        return SchoolCache._instance

    @gen.coroutine
    def GetSchools(self, region, province, city):
        if not self._rpcs:
            yield self._BuildRPCS()
        schools = self._rpcs[region][province][city]
        raise gen.Return(schools)

    @gen.coroutine
    def GetRegions(self):
        if not self._regions:
            self._regions = yield self.region_model.AllRegions()
        raise gen.Return(self._regions)

    @gen.coroutine
    def AddSchool(self, school):
        if not self._rpcs:
            yield self._BuildRPCS()
        else:
            self._AddSchoolToRPCS(
                school['region'],
                school['province'],
                school['city'],
                school
            )

    @gen.coroutine
    def DeleteSchool(self, school_id):
        if not self._rpcs:
            yield self._BuildRPCS()
        else:
            schools = self._id_to_rpcs.get(school_id)
            if schools:
                index, old_school = self._FindSchoolInList(schools, school_id)
                if old_school:
                    del schools[index]
                    del self._id_to_rpcs[school_id]

    @gen.coroutine
    def UpdateSchool(self, school):
        if not self._rpcs:
            yield self._BuildRPCS()
        schools = self._id_to_rpcs.get(school['_id'])
        if schools:
            index, old_school = self._FindSchoolInList(schools, school['_id'])
            if old_school:
                if old_school['region'] == school['region'] and \
                   old_school['province'] == school['province'] and \
                   old_school['city'] == school['city']:
                    schools[index] = school
                else:
                    del schools[index]
                    self._AddSchoolToRPCS(school['region'], school['province'], school['city'], school)
            else:
                logging.info('[SchoolCache]: can not find school: ' + str(school['_id']))
        else:
            self._AddSchoolToRPCS(school['region'], school['province'], school['city'], school)


    @gen.coroutine
    def _BuildRPCS(self):
        regions = yield self.region_model.AllRegions()
        rpcs = {
            region['name']: {
                 province['name']: {
                    city['name']: [] for city in province['city']
                 } for province in region['province']
            } for region in regions
        }
        self._rpcs = rpcs
        self._id_to_rpcs = {}
        schools = yield self.school_model.find({}).to_list(None)
        for school in schools:
            r = school.get('region', '')
            p = school.get('province', '')
            c = school.get('city', '')
            self._AddSchoolToRPCS(r, p, c, school)


    def _AddSchoolToRPCS(self, r, p, c, s):
        pcs = self._rpcs.get(r, None)
        if not pcs:
            logging.info('RPCS error: %s! %s %s %s' % (r,p,c,s))
            return
        cs = pcs.get(p, None)
        if not cs:
            logging.info('RPCS error: %s %s! %s %s' % (r,p,c,s))
            return
        schools = cs.get(c, None)
        if not s:
            logging.info('RPCS error: %s %s %s! %s' % (r,p,c,s))
            return
        schools.append(s)
        self._id_to_rpcs[s['_id']] = schools


    def _FindSchoolInList(self, schools, school_id):
        for i,s in enumerate(schools):
            if s['_id'] == school_id:
                return (i, s)
        return (-1, None)
