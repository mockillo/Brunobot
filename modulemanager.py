__author__  = 'Vegard Veiset'
__email__   = 'veiset@gmail.com'
__license__ = 'GPL'

import inspect
import thread
from module.core.output import out

class ModuleManager():
    '''
    The ModuleManager manages the core modules
    such as communication and connection, as well
    as the user defined modules located in module/extra.
    
    It contains information about which modules that
    are loaded.
    '''

    def __init__(self):
        '''
        Load the core modules, as well as the user defined
        extra modules defined in the config file (config.conf).
        '''

        self.enabled = True

        self.mcore = {}
        self.mextra = []
        self.mplugin = []
        self.cmdlist = {}
        self.cfg = ''

        import module.core.configmanager as cfg

        self.cfg = cfg.BrunobotConfig()
        self.cfg.printConfig()
        self.mcore['cfg'] = self.cfg

        # setting configuration for the output object
        out.setcfg(self.mcore['cfg'])

        self.loadCore()

        out.info('Core modules loaded ')
        for module in self.mcore:
            out.info('%s' % module)
        out.newline()

        import module.core.loadmodule as loadmodule
        self.moduleLoader = loadmodule.DynamicLoad(self)

        for module in self.cfg.list('modules'):
            thread.start_new_thread(self.loadModule, (module, ) )

        

    def quit(self, message=None):
        '''
        quit(string)

        Closes the IRC socket, and stops all the threads that are 
        running making the program come to a natural stop.  
        '''
        out.newline()
        self.mcore['connection'].quit()
        self.mcore['parser'].breader.running = False
        self.mcore['threadmanager'].stop()
        self.enabled = False

    def loadModule(self,name):
        '''
        Load a module using the module loader. 
        '''
        module, result = self.moduleLoader.load(name)

    def loadCore(self):
        '''
        Load the core modules required for the bot,
        and passing references to the core modules
        required for initializing them. 
        '''
        import module.core.communication as communication
        import module.core.cparser as parser
        import module.core.connection as connection
        import module.core.recentdata as recentdata
        import module.core.corecmd as corecmd
        import module.core.presist as presist
        import module.core.auth as auth
        import threadedmanager 
        

        self.mcore['connection'] = connection.Connection(
                self.cfg.get('connection','nick'),
                self.cfg.get('connection','ident'),
                self.cfg.get('connection','name'),
                self.cfg.get('connection','server'),
                int(self.cfg.get('connection','port')),
                self.cfg.list('channels'),
                self.cfg.get('connection','host'))
        
        self.mcore['auth'] = auth.Auth(
                self.cfg.list('owners'),
                self.cfg.list('admins'))

        self.mcore['communication'] = communication.Communication(self.mcore['connection'])
        self.mcore['recentdata'] = recentdata.Data()

        threadedmanager = threadedmanager.ThreadedManager()
        threadedmanager.setCommunication(self.mcore['communication'])
        threadedmanager.setConfig(self.mcore['cfg'])
        self.mcore['threadmanager'] = threadedmanager

        self.mcore['parser'] = parser.Parser(self)
        self.mcore['corecmd'] = corecmd.CoreCMD(self)
        self.mcore['presist'] = {}




    def isCmd(self, module, keyword='cmd'):
        '''
        isCmd(object, string) -> bool

        Checking if a modules listens to a keyword, when no
        keyword is defined it checks if it listens to 'cmd'.

        Keyword arguments:
        module   -- brunobot extra module
        keyword  -- keyword the module listens to 
        '''

        if not (inspect.ismodule(module)):
            try: module = self.extra(module)
            except: ''' ++ Warning: isCmd() - no such module '''

        try: 
            for listen in module.listen:
                if listen == keyword:
                    return True
        except: ''' ++ isCmd() - no such module '''

        return False

    def requires(self, module, keyword):
        '''
        requires(object, string) -> bool

        Checking if a module requires a given keyword. The require
        is defined in the extra module with the given variable:
          require = [coremodule, ...]

        Keyword arguments:
        module   -- brunobot extra module
        keyword  -- keyword to check if the module requires
        '''

        if inspect.ismodule(module):
            for req in module.require:
                if (req == keyword):
                    return True

        return False

    def listening(self, keyword):
        '''
        Return: a list of modules that listens to
        a given keyword.
        '''

        modules = []
        for module in self.mextra:
            for k in module.listen:
                if (k == keyword):
                    modules.append(module)

        return modules


    def core(self,name):
        ''' 
        Checking for name in core, i.e:
        that a core module with the name 
        'name' is loaded.
        '''

        try: return self.mcore[str(name)]
        except: return None
    
    def extra(self,name):
        ''' 
        Checking for name in extra, i.e:
        that an extra module with the name 
        'name' is loaded.
        '''

        for mod in self.mextra:
            if mod.filename == name:
                return mod
        return None

