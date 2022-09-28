##Layer_with_POI=table
##Interval_in_minutes=number 5
##Way_to_travel=selection foot; car
##Directory_for_your_json=output file json

import json
import urllib2
import re
from qgis.core import *
from PyQt4.QtCore import *
from processing.core.GeoAlgorithmExecutionException import  GeoAlgorithmExecutionException

output_directory = Directory_for_your_json
foot_or_car = Way_to_travel
dissolve_field = Layer_with_POI
tim = Interval_in_minutes
i = foot_or_car
if i == 0:
        foc='foot'
        rad = (4000. / 60. * tim / 1000)
else:
        foc='car'
        rad = (60000. / 60. * tim / 1000)

inlayer = processing.getObject(dissolve_field)
iter = inlayer.getFeatures()
output_info = None

def get_request(foc, points, rad, tim):
    try:
        request =  'https://galton.urbica.co/moscow/%s/?lng=%0.12f&lat=%0.12f&intervals=%f&radius=%f&cellWidth=0.2'%(foc, points[0], points[1], tim, rad)
    except:
        raise  GeoAlgorithmExecutionException('Invalid GET request! (%s)'%request)
    return json.load(urllib2.urlopen(request))

i = 1
n = len(inlayer.allFeatureIds())
for feature in iter:
    progress.setText('%d out of %d'%(feature.id(), n))
    progress.setPercentage(i*100/n)
    # retrieve every feature with its geometry and attributes
    # fetch geometry
    geom = feature.geometry()

    # show some information about the feature
    if geom.type() == QGis.Point:
        x = geom.asPoint()
        get_result = get_request(foc, x, rad, tim)      
	if output_info is None:
            output_info = get_result
        else:
            output_info['features'].append(get_result['features'][0])
    i +=1
   # if i>5:
      #  break
if output_info is None:
    raise  GeoAlgorithmExecutionException("We haven't found any isochrones. Probably, there are no points in your input layer.")

output_directory = output_directory.split('.json')[0] + '_' + str(tim) + '_min_' + foc + '_isochrones' + '.json' if len(output_directory.split('.json')) > 1 else output_directory + '_' + str(tim) + '_min_' + foc + '_isochrones' + '.json'
with open(output_directory, 'w') as outfile:
    json.dump(output_info, outfile)
print('Your data is saved at %s'% output_directory)
progress.setInfo('Your data is saved at %s'% output_directory)
out_layer = QgsVectorLayer(output_directory,re.split(r'/|\\', output_directory)[-1].split('.json')[0],"ogr")
QgsMapLayerRegistry.instance().addMapLayer(out_layer)