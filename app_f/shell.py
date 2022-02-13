import os, sys
sys.path.append(os.getcwd())
from cmd import Cmd
from app_f import app
from datetime import datetime
from DataManager.utils.timehandler import TimeHandler
from prettytable import PrettyTable, SINGLE_BORDER

TODAY = datetime.now()
TODAY = datetime(TODAY.year, TODAY.month, TODAY.day)

class MyPrompt(Cmd):
    __hiden_methods = ('do_EOF', 'do_set', )
    SHOW_COMMANDS = ['strats', ]
    SET_DATA = {
        'timestamps': {
            'CURRENT_START_TIMESTAMP': TODAY,
            'CURRENT_END_TIMESTAMP': TODAY,
        },
        'limit': None,
        'update_before': False,
        'exchangeName': 'NYSE',
    }
    SET_ADDL_FLAGS = ['all', 'end_set']
    SET_COMPLETES =  list(SET_DATA.keys()) + SET_ADDL_FLAGS
    STRAT_IDS = [str(x) for x in list(app.strat_id_to_name.keys())]
    STRAT_NAMES = list(app.strat_name_to_id.keys())
    STRAT_IDS_AND_NAMES = STRAT_IDS + STRAT_NAMES

    CUSTOM_PROMPT_NEEDED = False
    CUSTOM_PROMPT_MSG = ''

    def do_show(self, args):
        if not args:
            print (f'show needs an argument')
            return
        if not args in self.SHOW_COMMANDS:
            print (f'{args} is not a valid argument to show')
            return

        if args == self.SHOW_COMMANDS[0]: #strats
            x = PrettyTable()
            x.set_style(SINGLE_BORDER)
            x.field_names = ['SID', 'Name']
            x.add_rows(list(app.strat_id_to_name.items()))
            print(x.get_string(sortby='SID'))
            return
        

    def complete_show(self, text, line, begidx, endidx):
        if not text:
            completions = self.SHOW_COMMANDS[:]
        else:
            completions = [ f
                            for f in self.SHOW_COMMANDS
                            if f.startswith(text)
                            ]
        return completions

    def do_run(self, args):
        if not args:
            print (f'run needs an argument')
            return
        if not args in self.STRAT_IDS_AND_NAMES:
            print (f'{args} is not a valid argument to run')
            return
        if args.isdigit():
            sid = int(args)
            self.CUSTOM_PROMPT_NEEDED = True
            self.CUSTOM_PROMPT_MSG = 'set '
        else:
            s_name = args
        

    def complete_run(self, text, line, begidx, endidx):
        if not text:
            completions = self.STRAT_IDS[:]
        else:
            completions = [ f
                            for f in self.STRAT_NAMES
                            if f.startswith(text)
                            ]
        return completions

    def do_set(self, args):
        if args == 'all':
            pass

    def complete_set(self, text, line, begidx, endidx):
        if not text:
            completions = self.SET_COMPLETES[:]
        else:
            completions = [ f
                            for f in self.SET_COMPLETES
                            if f.startswith(text)
                            ]
        return completions

    def do_quit(self, args):
        """Quits Quantify"""
        print ("Quantify closed.")
        raise SystemExit

    def do_EOF(self, line):
        self.do_quit(line)
    
    def postloop(self):
        print

    def postcmd(self, stop: bool, line: str) -> bool:
        if self.CUSTOM_PROMPT_NEEDED:
            self.prompt = '(q)> ' + self.CUSTOM_PROMPT_MSG
        else:
            self.prompt = '(q)> '
        return super().postcmd(stop, line)

    def precmd(self, line: str) -> str:
        if self.CUSTOM_PROMPT_NEEDED:
            line = self.CUSTOM_PROMPT_MSG + line
            self.CUSTOM_PROMPT_NEEDED = False
            self.CUSTOM_PROMPT_MSG = ''
        
        return super().precmd(line)

    def get_names(self):
        return [n for n in dir(self.__class__) if n not in self.__hiden_methods]

    def complete(self, text: str, state: int):
        if self.CUSTOM_PROMPT_NEEDED and state < 2:
            import readline
            origline = readline.get_line_buffer()
            line = origline.lstrip()
            stripped = len(origline) - len(line)
            begidx = readline.get_begidx() - stripped
            endidx = readline.get_endidx() - stripped
            try:
                compfunc = getattr(self, 'complete_' + self.CUSTOM_PROMPT_MSG.strip())
            except AttributeError:
                compfunc = self.completedefault
            self.completion_matches = ['XXX'] + compfunc(text, line, begidx, endidx)
            return super().complete(text, 1)
        return super().complete(text, state)


if __name__ == '__main__':
    prompt = MyPrompt()
    prompt.prompt = '(q)> '
    prompt.cmdloop('Quantify 0.0.0\n')