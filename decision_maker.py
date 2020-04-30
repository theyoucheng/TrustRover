
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import numpy as np
class decision_maker:

    def __init__(self, car):
        self.car = car
        self.objs_in_slow_range = []
        self.objs_in_stop_range = []
        self.prev_objs_in_slow_range = []
        self.prev_objs_in_stop_range = []
    
    def print_car_driving_path(self):
        print(self.car.driving_path)

    def print_car_warning_left_sector(self):
        print(self.car.warning_left_sector)
    
    # checks if an object bounding box is within a sector
    def objectInSector(self,result, poly, message):
        corners = np.array([[result['topleft']['x'], result['topleft']['y']],
                       [result['bottomright']['x'], result['bottomright']['y']],
                       [result['topleft']['x'], result['bottomright']['y']],
                       [result['bottomright']['x'], result['topleft']['y']]], np.int32)  
        for corner in corners:
            corner = Point(corner)
            if poly.contains(corner):
                return True
        
        return False
    
    # checks if any objcts exist in any sectors and labels them if they are.
    def check_if_object_in_path(self, results):
        self.clearObjLists()
        for result in results:
            result['status'] = ''
            if self.objectInSector(result, Polygon(self.car.warning_left_sector), "warning" ) or self.objectInSector(result, Polygon(self.car.warning_right_sector), "warning" ):
                result['status'] = "warning"
            if self.objectInSector(result, Polygon(self.car.danger_left_sector), "danger" ) or self.objectInSector(result, Polygon(self.car.danger_right_sector), "danger" ):
                result['status'] = "danger"
            if self.objectInSector(result, Polygon(self.car.slow_zone), "slow" ):
                result['status'] = "slow"
                self.add_obj_to_warning_list(result['bottomright']['y'])
            if self.objectInSector(result, Polygon(self.car.stopping_zone), "stop" ):
                result['status'] = "stop"
                self.add_obj_to_danger_list(result['bottomright']['y'])

        return results

# clears the arrays holding the current objects detected in the slow and stop zones
    def clearObjLists(self):
        self.objs_in_slow_range.clear()
        self.objs_in_stop_range.clear()
    
    # clears the previous slow and stop arrays and adds the current arrays into the previous arrays
    def set_prev_obj(self):

        self.prev_objs_in_slow_range.clear()
        self.prev_objs_in_stop_range.clear()
        self.prev_objs_in_slow_range = self.objs_in_slow_range.copy()
        self.prev_objs_in_stop_range = self.objs_in_stop_range.copy() 

    def add_obj_to_warning_list(self,y):
        self.objs_in_slow_range.append(y)

    def add_obj_to_danger_list(self, y):
        self.objs_in_stop_range.append(y)

# checks the stop zone sector
    def check_stop_zone(self):
        if len(self.objs_in_stop_range) > 0:
            return "stopped"
        elif len(self.prev_objs_in_stop_range) > 0 and len(self.objs_in_stop_range) == 0:
            return "accelerating"
        else:
            return "driving"

# checks slow zone sector
    def check_slow_zone(self):
        if len(self.prev_objs_in_slow_range) == 0 and len(self.objs_in_slow_range) > 0 :
            return "decelerating"
        elif len(self.objs_in_slow_range) > 0:
            self.objs_in_slow_range.sort()
            if len(self.prev_objs_in_slow_range) > 0:
                self.prev_objs_in_slow_range.sort()
                if self.objs_in_slow_range[-1] > self.prev_objs_in_slow_range[-1] + 10:
                    return "decelerating"
                elif self.objs_in_slow_range[-1] < self.prev_objs_in_slow_range[-1] + 10:
                    return "accelerating"
                else:
                    return "slow"
            else:
                return "slow"
        else:
            return "driving"

# gets the status of the car based on the contents of the slow and stop zones
    def check_status_of_car(self):
        self.car.status =''
        self.car.status = self.check_stop_zone()
        if self.car.status != "driving":
            return self.car.status
        self.car.status = self.check_slow_zone()
        return self.car.status






    