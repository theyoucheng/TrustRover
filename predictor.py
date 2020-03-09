class predictor:
    
   
   def get_prediction(image, predicted_path):
            results = tfnet.return_predict(image)
            results = check_if_object_in_path(results)
            car_status = check_status_of_car()
            set_prev_obj()
            if os.path.exists('./{0}/'.format(predicted_path)):
                write_boundingboxes(results, image, './{0}/{1}'.format(predicted_path, image), car_status)
            else:
                try:
                    os.mkdir('./{0}/'.format(predicted_path))
                    write_boundingboxes(results, imgcv, './{0}/{1}/{2}'.format(predicted_path,route, step), car_status)
                except OSError:
                    print ("Creation of the directory ./{0}/{1} failed".format(predicted_path, route))
                else:
                    print ("Successfully created the directory ./{0}/{1}".format(predicted_path, route))
        predicted_route = os.listdir("./{0}/{1}/".format(predicted_path, route))
        predicted_route = sorted(predicted_route)
        convertToGif(predicted_route, predicted_path, route) 
    
    def check_if_object_in_path(results):
        clearObjLists()
        for result in results:
            result['status'] = ''
            if objectInSector(result, Polygon(warning_left_sector), "warning" ) or objectInSector(result, Polygon(warning_right_sector), "warning" ):
                result['status'] = "warning"
            if objectInSector(result, Polygon(danger_left_sector), "danger" ) or objectInSector(result, Polygon(danger_right_sector), "danger" ):
                result['status'] = "danger"
            if objectInSector(result, Polygon(slow_zone), "slow" ):
                result['status'] = "slow"
                add_obj_to_warning_list(result['bottomright']['y'])
            if objectInSector(result, Polygon(stopping_zone), "stop" ):
                result['status'] = "stop"
                add_obj_to_danger_list(result['bottomright']['y'])

        return results

    def objectInSector(result, poly, message):
        corners = np.array([[result['topleft']['x'], result['topleft']['y']],
                       [result['bottomright']['x'], result['bottomright']['y']],
                       [result['topleft']['x'], result['bottomright']['y']],
                       [result['bottomright']['x'], result['topleft']['y']]], np.int32)  
        for corner in corners:
            corner = Point(corner)
            if poly.contains(corner):
                return True
    
        return False