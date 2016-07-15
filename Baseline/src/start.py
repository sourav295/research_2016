from springpython.config import XMLConfig
from configure import GlobalConfiguration

configs = [XMLConfig("resource/current/Topology.xml"), XMLConfig("resource/current/Router.xml")]


g = GlobalConfiguration()
g.configure(configs)


