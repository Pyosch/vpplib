# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 15:34:00 2019

@author: Sascha Birk
"""

from Model.VPPBEV import VPPBEV

bev = VPPBEV(1,2,3,2017)

def test_prepareTimeSeries(bev):
    
    bev.prepareTimeSeries()
    bev.prepareBEV()
    print("prepareTimeSeries:")
    print(bev.timeseries.head())    
    
def test_valueForTimestamp(bev):
    
    timestepvalue = bev.valueForTimestamp(300)
    print("\nvalueForTimestamp:\n", timestepvalue)
    
test_prepareTimeSeries(bev)
test_valueForTimestamp(bev)