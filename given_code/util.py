
def read_yolo_labels(fname):
  labels=[]
  with open(fname) as f:
    lines=f.readlines()
    lines=lines[1:]
    for l in lines:
      labels.append(l.split(':')[0])
  labels.sort()
  return labels
