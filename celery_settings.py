import os
 
BROKER_URL = os.environ.get('REDIS_URL', 'redis://:p2f6023c375db5e2022b9fbc6f0d372d7f2aaece5f5e4ce32571b96fbb1733b15@ec2-44-195-108-193.compute-1.amazonaws.com:14910')
CELERY_RESULT_BACKEND=os.environ.get('REDIS_URL', 'redis://:p2f6023c375db5e2022b9fbc6f0d372d7f2aaece5f5e4ce32571b96fbb1733b15@ec2-44-195-108-193.compute-1.amazonaws.com:14910')
CELERY_TASK_SERIALIZER='json'