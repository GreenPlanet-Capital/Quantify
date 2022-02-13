import copy
import os, sys
sys.path.append(os.getcwd())
from constants.quant_cmd import Cmd
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
    SET_ADDL_FLAGS = ['all', 'end']
    SET_COMPLETES =  list(SET_DATA.keys()) + SET_ADDL_FLAGS
    STRAT_IDS = [str(x) for x in list(app.strat_id_to_name.keys())]
    STRAT_NAMES = list(app.strat_name_to_id.keys())
    STRAT_IDS_AND_NAMES = STRAT_IDS + STRAT_NAMES
    TIMESTAMP_COMPLETIONS = ['start_timestamp', 'end_timestamp']

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

        sid = -1
        if args.isdigit():
            sid = int(args)
        else:
            sid = app.strat_name_to_id(args)
        self.run_subcommand('set')
        # run the strat

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
        TIMESTAMPS = False
        EXCHANGE_NAME_FLAG = False
        LIMIT_FLAG = False
        UPDATE_BEFORE = False

        args_flag = args.split()

        if 'end' in args_flag:
            return
        if 'all' in args_flag:
            TIMESTAMPS = True
            EXCHANGE_NAME_FLAG = True
            LIMIT_FLAG = True
            UPDATE_BEFORE = True
        if 'timestamps' in args_flag:
            TIMESTAMPS = True
        if 'exchangeName' in args_flag:
            EXCHANGE_NAME_FLAG = True
        if 'limit' in args_flag:
            LIMIT_FLAG = True
        if 'update_before' in args_flag:
            UPDATE_BEFORE = True

        if TIMESTAMPS:
            self.run_subcommand('timestamps')
        if EXCHANGE_NAME_FLAG:
            self.run_subcommand('exchangeName')
        if LIMIT_FLAG:
            self.run_subcommand('limit')
        if UPDATE_BEFORE:
            self.run_subcommand('update_before')

        print('FLAGS CHOSEN:')
        x = PrettyTable()
        x.set_style(SINGLE_BORDER)
        x.field_names = ['flags', 'value']
        flags_dict = copy.deepcopy(self.SET_DATA)
        td = flags_dict['timestamps']
        flags_dict.pop('timestamps')
        rows = [
            ('start_timestamp', TimeHandler.get_alpaca_string_from_datetime(td['CURRENT_START_TIMESTAMP'])),
            ('end_timestamp', TimeHandler.get_alpaca_string_from_datetime(td['CURRENT_END_TIMESTAMP']))
        ]
        rows.extend(list(flags_dict.items()))
        x.add_rows(rows)
        print(x.get_string())

    def complete_set(self, text, line, begidx, endidx):
        if not text:
            completions = self.SET_COMPLETES[:]
        else:
            completions = [ f
                            for f in self.SET_COMPLETES
                            if f.startswith(text)
                            ]
        return completions

    def do_timestamps(self, args):
        args_flags = args.split()
        START_FLAG = False
        END_FLAG = False
        if not args:
            START_FLAG = True
            END_FLAG = True

        if self.TIMESTAMP_COMPLETIONS[0] in args_flags:
            START_FLAG = True
        
        if self.TIMESTAMP_COMPLETIONS[1] in args_flags:
            END_FLAG = True

        timestamps_dict = self.SET_DATA['timestamps']
        start_datetime = timestamps_dict['CURRENT_START_TIMESTAMP']
        end_datetime = timestamps_dict['CURRENT_END_TIMESTAMP']
        if START_FLAG:
            while(1):
                print('start_timestamp', TimeHandler.get_alpaca_string_from_datetime(start_datetime), end=' ')
                user_inp = str(input())
                if user_inp == '':
                    break
                try:
                    start_datetime = datetime.strptime(user_inp, "%Y-%m-%d")
                    break
                except:
                    print('INVALID FORMAT: Enter date(yyyy-mm-dd)')

        if END_FLAG:
            while(1):
                print('end_timestamp', TimeHandler.get_alpaca_string_from_datetime(end_datetime), end=' ')
                user_inp = str(input())
                if user_inp == '':
                    break
                try:
                    end_datetime = datetime.strptime(user_inp, "%Y-%m-%d")
                    break
                except:
                    print('INVALID FORMAT: Enter date(yyyy-mm-dd)')

        timestamps_dict['CURRENT_START_TIMESTAMP'] = start_datetime
        timestamps_dict['CURRENT_END_TIMESTAMP'] = end_datetime
        




    def complete_timestamps(self, text, line, begidx, endidx):
        return self.completions_list(text, self.TIMESTAMP_COMPLETIONS)

    def completions_list(self, text, list_of_completions):
        if not text:
                    completions = list_of_completions
        else:
            completions = [ f
                            for f in list_of_completions
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

    def run_subcommand(self, cmd_name: str):
        self.CUSTOM_PROMPT_NEEDED = True
        self.CUSTOM_PROMPT_MSG = f'{cmd_name} '
        self.postcmd(False, None)
        self.hax()

if __name__ == '__main__':
    prompt = MyPrompt()
    prompt.prompt = '(q)> '
    prompt.cmdloop('Quantify 0.0.0\n')