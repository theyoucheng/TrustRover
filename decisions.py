
def check_if_object_in_path(results):
    for result in results:
        inside = False
        point1 = Point(result['topleft']['x'], result['topleft']['y'])
        point2 = Point(result['bottomright']['x'], result['bottomright']['y'])
        point3 = Point(result['topleft']['x'], result['bottomright']['y'])
        point4 = Point(result['bottomright']['x'], result['topleft']['y'])
        warning_poly = Polygon(warning_path)
        danger_poly = Polygon(danger_path)
        if warning_poly.contains(point1):
            result['label'] = 'warning {0}'.format(result['label'])
        elif warning_poly.contains(point2):
            result['label'] = 'warning {0}'.format(result['label'])
        elif warning_poly.contains(point3):
            result['label'] = 'warning {0}'.format(result['label'])
        elif warning_poly.contains(point4):
            result['label'] = 'warning {0}'.format(result['label'])

        if danger_poly.contains(point1):
            result['label'] = 'danger {0}'.format(result['label'])
        elif danger_poly.contains(point2):
            result['label'] = 'danger {0}'.format(result['label'])
        elif danger_poly.contains(point3):
            result['label'] = 'danger {0}'.format(result['label'])
        elif danger_poly.contains(point4):
            result['label'] = 'danger {0}'.format(result['label'])
    return results

def is_object_in_range(points, poly):
        if poly.contains(point1):
            return True
        elif poly.contais(point2):
            return True
        elif poly.contains(point3):
            return True
        elif poly.contains(point4):
            return True
        else : 
            return False