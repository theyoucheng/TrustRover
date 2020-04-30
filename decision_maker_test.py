import unittest

from decision_maker import decision_maker
from car import car
import numpy as np

class testDecisionMaker(unittest.TestCase):

    def setUp(self):
      self.test_result = {"label": "car", 
                       "bottomright": {"x" : 150,
                                       "y" : 380 },
                       "topleft": {"x" : 130,
                                       "y" : 300 },
                        "confidence" : 0.56
                      } 
        self.test_results_list = []
        self.test_results_list.append(test_result)

        driving_path = np.array([[190,200],[100,400],[300,400],[210,200]], np.int32)
        warning_left_sector = np.array([[driving_path[1][0],driving_path[0][1]],
                                [driving_path[1][0],driving_path[0][1]+50],
                                [driving_path[1][0]+60,driving_path[0][1]+50],
                                [driving_path[0][0],driving_path[0][1]]], np.int32)
        danger_left_sector = np.array([[warning_left_sector[1][0],warning_left_sector[1][1]],
                                [0,300],
                                [0,400],
                                [driving_path[1][0],driving_path[1][1]],
                                [warning_left_sector[2][0],warning_left_sector[2][1]]], np.int32)
        warning_right_sector = np.array([[driving_path[3][0],driving_path[3][1]],
                                [driving_path[3][0]+30,driving_path[3][1]+50],
                                [driving_path[2][0],driving_path[0][1]+50],
                                [driving_path[2][0],driving_path[3][1]]], np.int32)
        danger_right_sector = np.array([[warning_right_sector[1][0],warning_right_sector[1][1]],
                                [driving_path[2][0],driving_path[2][1]],
                                [driving_path[2][0]+40,driving_path[2][1]],
                                [warning_right_sector[1][0]+40,warning_right_sector[1][1]]], np.int32)
        stopping_zone = np.array([[driving_path[0][0]-30,driving_path[0][1]+100],
                                [driving_path[1][0]+20,driving_path[1][1]],
                                [driving_path[2][0]-20,driving_path[2][1]],
                                [driving_path[3][0]+30,driving_path[3][1]+100]], np.int32)
        slow_zone = np.array([[driving_path[0][0],driving_path[0][1]+50],
                                [stopping_zone[0][0],stopping_zone[0][1]],
                                [stopping_zone[3][0],stopping_zone[3][1]],
                                [driving_path[3][0],driving_path[3][1]+50]], np.int32)
        self.test_car = car(driving_path, warning_left_sector, danger_left_sector, 
             warning_right_sector, danger_right_sector, 
             stopping_zone, slow_zone)


    def test_stop_zone_for_object_in_zone(self):
        #  assume
        
        # action
        test_decision_maker = decision_maker(self.test_car)
        results = test_decision_maker.check_if_object_in_path(test_results_list)
        test_decision_maker.car.status = test_decision_maker.check_status_of_car()

        #  assert
        self.assertEqual(test_decision_maker.check_status_of_car(), "stopped")
