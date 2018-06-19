
def gen_traindata(tot, di):
  for i in range(0, tot):
    print './{0}/{1}.jpg'.format(di, i)

def check_result(fname):
  c=-1
  labels_0=[]
  labels=[]
  with open(fname) as f:
    lines = f.readlines()
    for l in lines:
      if not (l.find(':') >= 0): continue

      if l.find('Enter')>=0:
        c+=1

        if c==1:
          labels_0.sort()

        if c>1:
          labels.sort()
          if not labels_0==labels: return c-1
          labels=[]

        continue

      label=l.split(':')[0]
      print c, label
      if c==0: labels_0.append(label)
      else: labels.append(label)

  return 0
