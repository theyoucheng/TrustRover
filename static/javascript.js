function main(){
    print("calling main()")
    $SCRIPT_ROOT = '{{ request.script_root|tojson|safe }}';

    var route = document.getElementById("route").value;
    var yolo = document.getElementById("yolo_version").value;

    console.log(route)
    console.log(yolo)

    $.get($SCRIPT_ROOT, '/get_route', {
        route: route,
        yolo: yolo
     }
     , function(data) {
       journey = document.getElementById("journey"); 
       journey.src = data.gif;
       return false;
     })

}
