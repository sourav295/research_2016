from Book import *
from springpython.config import XMLConfig
from springpython.context import ApplicationContext


configuration = XMLConfig("../res/conf.xml")
context = ApplicationContext(configuration)


testService = context.get_object("book-001");

print testService.name + " " + testService.author