import os
import yaml
import articulate

config = yaml.load(file(os.path.join(os.path.dirname(articulate.__file__),'config.yaml'),'r'))
