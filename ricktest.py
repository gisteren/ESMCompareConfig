__author__ = 'Vosteen'
from datetime import datetime

epoch = datetime(1970,1,1)
i = datetime.now()

delta_time = (i - epoch).total_seconds()
print delta_time