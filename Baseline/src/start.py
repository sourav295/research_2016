from springpython.config import XMLConfig
from configure import GlobalConfiguration

GlobalConfiguration.configure()

GlobalConfiguration.simpyEnv.run(until=int(300))


#packet logging
import SimComponents
SimComponents.Packet.log_to_file()
