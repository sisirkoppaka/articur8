import os
import yaml
import articurate

config = yaml.load(file(os.path.join(os.path.dirname(articurate.__file__),'config.yaml'),'r'))
