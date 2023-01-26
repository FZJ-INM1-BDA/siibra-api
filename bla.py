
from api.serialization.util import instance_to_model
from api.serialization.util.siibra import StreamlineCounts

feat, *_ = StreamlineCounts.get_instances()

instance_to_model(feat)