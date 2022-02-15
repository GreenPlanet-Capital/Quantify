import copy
from itertools import zip_longest
import os, sys
sys.path.append(os.getcwd())
from typing import List
from positions.opportunity import Opportunity
from positions.position import Position
from strats.base_strategy import BaseStrategy
from constants.datamanager_settings import setup_datamgr_settings
setup_datamgr_settings()
from DataManager.datamgr.data_manager import DataManager
from constants.quant_cmd import Cmd
from app_f import app
import datetime as dt
from datetime import datetime
from DataManager.utils.timehandler import TimeHandler
from prettytable import PrettyTable, SINGLE_BORDER

TODAY = datetime.now()
TODAY = datetime(TODAY.year, TODAY.month, TODAY.day)

class MyPrompt(Cmd):
    __hiden_methods = ('do_EOF', 'do_exchangeName', 'do_timestamps',
                        'do_limit', 'do_update_before', 'do_forward_test',
                        'do_live_test', 'do_strat')
    SHOW_COMMANDS = ['strats', 'set_data', 'results', 'tracked']
    RUN_COMPLETES = ['live_test', 'forward_test']
    SET_DATA = {
        'timestamps': {
            'CURRENT_START_TIMESTAMP': TODAY,
            'CURRENT_END_TIMESTAMP': TODAY,
        },
        'limit': None,
        'update_before': False,
        'exchangeName': 'NYSE',
        'strat': None
    }
    SET_ADDL_FLAGS = ['all', 'end', ]
    SET_COMPLETES =  list(SET_DATA.keys()) + SET_ADDL_FLAGS
    STRAT_IDS = [str(x) for x in list(app.strat_id_to_name.keys())]
    STRAT_NAMES = list(app.strat_name_to_id.keys())
    STRAT_IDS_AND_NAMES = STRAT_IDS + STRAT_NAMES
    TIMESTAMP_COMPLETIONS = ['start_timestamp', 'end_timestamp']
    EXCHANGE_NAMES = ['NYSE', 'NASDAQ', 'OTC', 'ARCA', 'AMEX', 'BATS']
    RESULTS: List[Opportunity] = []
    TRACKED: List[Position] = [] # TODO populate this from disk
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
            x.field_names = ['SID', 'Name', 'Min Data Needed', 'Unit']
            x.add_rows(
                (id, name, app.strat_id_to_class[id].length_of_data_needed, app.strat_id_to_class[id].timeframe.datatype)
                for id, name in app.strat_id_to_name.items()
            )
            print(x.get_string(sortby='SID'))
        
        elif args == self.SHOW_COMMANDS[1]: #set_data
            self.print_set_data()

        elif args == self.SHOW_COMMANDS[2]: #results
            self.show_results()

        elif args == self.SHOW_COMMANDS[3]: #tracked
            self.show_tracked()

    def complete_show(self, text, line, begidx, endidx):
        return self.completions_list(text, self.SHOW_COMMANDS)

    def do_run(self, args):
        if not args:
            print (f'run needs an argument')
            return
        if not args in self.RUN_COMPLETES:
            print (f'{args} is not a valid argument to run')
            return

        if args=='live_test':
            self.run_subcommand('live_test')
        elif args=='forward_test':
            self.run_subcommand('forward_test')

    def complete_run(self, text, line, begidx, endidx):
        return self.completions_list(text, self.RUN_COMPLETES)

    def do_forward_test(self, args):
        pass

    def complete_forward_test(self, text, line, begidx, endidx):
        return self.completions_list(text, ['default'])

    def do_live_test(self, args):
        DEFAULT_FLAG = False
        if args=='default':
            DEFAULT_FLAG = True

        if not DEFAULT_FLAG:
            self.run_subcommand('set')
        
        STATUS, msg = self.check_set_integrity()
        if not STATUS:
            if DEFAULT_FLAG:
                print()
                print(msg)
            print('Cancelling forward_test\n')
            return
        
        # TODO Do the forward test here

    def complete_live_test(self, text, line, begidx, endidx):
        return self.completions_list(text, ['default'])

    def do_track(self, args):
        uid = -1
        if not args and not args.isdigit() and not args.isdigit() < len(self.RESULTS):
            print('track needs a uid of an opportunity\nuse "show results" to find the uid')
            return
        elif args.isdigit():
            uid = int(args)

        opp: Opportunity = self.RESULTS[uid]
        position = Position(opp)

        #TODO pickle the position


    def do_strat(self, args):
        if not args:
            if not self.SET_DATA['strat']:
                print (f'Needs a strategy argument')
                return self.run_subcommand('strat')
            else:
                return
        if not args in self.STRAT_IDS_AND_NAMES:
            print (f'{args} is not a valid argument to strat')
            return

        sid = -1
        if args.isdigit():
            sid = int(args)
        else:
            sid = app.strat_name_to_id[args]
        
        self.SET_DATA['strat'] = app.strat_id_to_class[sid]

    def complete_strat(self, text, line, begidx, endidx):
        return self.completions_list(text, self.STRAT_NAMES)

    def do_set(self, args):
        TIMESTAMPS = False
        EXCHANGE_NAME_FLAG = False
        LIMIT_FLAG = False
        UPDATE_BEFORE = False
        STRATEGY = False

        args_flag = args.split()

        if 'end' in args_flag:
            return
        if 'all' in args_flag:
            TIMESTAMPS = True
            EXCHANGE_NAME_FLAG = True
            LIMIT_FLAG = True
            UPDATE_BEFORE = True
            STRATEGY = True
        if 'timestamps' in args_flag:
            TIMESTAMPS = True
        if 'exchangeName' in args_flag:
            EXCHANGE_NAME_FLAG = True
        if 'limit' in args_flag:
            LIMIT_FLAG = True
        if 'update_before' in args_flag:
            UPDATE_BEFORE = True
        if 'strat' in args_flag:
            STRATEGY = True

        if TIMESTAMPS:
            self.run_subcommand('timestamps')
        if EXCHANGE_NAME_FLAG:
            print('exchangeName', self.SET_DATA['exchangeName'])
            self.run_subcommand('exchangeName')
        if LIMIT_FLAG:
            print('limit', self.SET_DATA['limit'])
            self.run_subcommand('limit')
        if UPDATE_BEFORE:
            print('update_before', self.SET_DATA['update_before'])
            self.run_subcommand('update_before')
        if STRATEGY:
            print('strategy', self.SET_DATA['strat'])
            self.run_subcommand('strat')
        
        STATUS, msg = self.check_set_integrity()
        if not STATUS:
            print(msg)

        self.print_set_data()

    def print_set_data(self):
        print('\nFLAGS CHOSEN:')
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

    def check_set_integrity(self):
        INTEGRITY = True
        msg = ""
        if self.SET_DATA['strat']:
            strat:BaseStrategy = self.SET_DATA['strat']
            dmgr = DataManager()
            start_timestamp_string = TimeHandler.get_string_from_datetime(self.SET_DATA['timestamps']['CURRENT_START_TIMESTAMP'])
            end_timestamp_string = TimeHandler.get_string_from_datetime(self.SET_DATA['timestamps']['CURRENT_END_TIMESTAMP'])
            new_start, new_end, date_range = dmgr.validate_timestamps(start_timestamp_string, end_timestamp_string)
            self.SET_DATA['timestamps']['CURRENT_START_TIMESTAMP'], self.SET_DATA['timestamps']['CURRENT_END_TIMESTAMP'] = TimeHandler.get_datetime_from_string(new_start), TimeHandler.get_datetime_from_string(new_end)
            if(not (len(date_range) >= strat.length_of_data_needed)):
                print(f'TIMESTAMPS: start_timestamp was not suffiencient for strategy "{strat.name}"\nNeeds at least {strat.length_of_data_needed} {strat.timeframe.datatype} units')
                assumed_start = (self.SET_DATA['timestamps']['CURRENT_END_TIMESTAMP'] - dt.timedelta(int(strat.length_of_data_needed*2))).date()
                assumed_start_string = TimeHandler.get_string_from_datetime(assumed_start)
                _, _, date_range = dmgr.validate_timestamps(assumed_start_string, new_end)
                new_start_timestamp = date_range[-strat.length_of_data_needed]
                new_start_datetime = TimeHandler.get_datetime_from_timestamp(new_start_timestamp)
                self.SET_DATA['timestamps']['CURRENT_START_TIMESTAMP'] = new_start_datetime
                print(f'WARNING: start_timestamp was changed to {TimeHandler.get_string_from_datetime(new_start_datetime)} to accomodate for strategy')
        
        if (self.SET_DATA['timestamps']['CURRENT_START_TIMESTAMP']\
            == self.SET_DATA['timestamps']['CURRENT_END_TIMESTAMP']):
            msg += 'TIMESTAMPS: start_timestamp and end_timestamp is equal\n'
            INTEGRITY = False
        
        if (self.SET_DATA['timestamps']['CURRENT_START_TIMESTAMP']\
            > self.SET_DATA['timestamps']['CURRENT_END_TIMESTAMP']):
            msg += 'TIMESTAMPS: end_timestamp is before start_timestamp\n'
            INTEGRITY = False

        if (self.SET_DATA['timestamps']['CURRENT_START_TIMESTAMP'] > TODAY):
            msg += 'TIMESTAMPS: start_timestamp is in the future\n'
            INTEGRITY = False
        if (self.SET_DATA['timestamps']['CURRENT_END_TIMESTAMP'] > TODAY):
            msg += 'TIMESTAMPS: end_timestamp is in the future\n'
            INTEGRITY = False

        if (self.SET_DATA['limit'] is not None and self.SET_DATA['limit'] < 8):
            msg += 'LIMIT: limit !> 8. limit needs to be None or >=8\n'
            INTEGRITY = False

        if not self.SET_DATA['strat']:
            msg += 'STRATEGY: Strategy Not Set\n'
            INTEGRITY = False

        if not INTEGRITY:
            msg = 'SET ERROR(s): Run the set command again to resolve integrity issues\n' + msg

        return INTEGRITY, msg

    def complete_set(self, text, line, begidx, endidx):
        return self.completions_list(text, self.SET_COMPLETES)

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
        print()
        timestamps_dict['CURRENT_START_TIMESTAMP'] = start_datetime
        timestamps_dict['CURRENT_END_TIMESTAMP'] = end_datetime

    def complete_timestamps(self, text, line, begidx, endidx):
        return self.completions_list(text, self.TIMESTAMP_COMPLETIONS)

    def do_exchangeName(self, args):
        if args == '':
            return
        if args in self.EXCHANGE_NAMES:
            self.SET_DATA['exchangeName'] = args
        else:
            print('Invalid exchange name')
            return self.run_subcommand('exchangeName')

    def complete_exchangeName(self, text, line, begidx, endidx):
        return self.completions_list(text, self.EXCHANGE_NAMES)

    def do_limit(self, args):
        if args == '':
            return
        if args == 'None':
            self.SET_DATA['limit'] = None
        elif args.isdigit():
            self.SET_DATA['limit'] = int(args)
        else:
            print(args)
            print('Argument must be a digit or "None"')
            return self.run_subcommand('limit')

    def do_update_before(self, args):
        if args == '':
            return
        if args == 'True':
            self.SET_DATA['update_before'] = True
        elif args == 'False':
            self.SET_DATA['update_before'] = False
        else:
            print('Argument must be a digit')
            return self.run_subcommand('update_before')

    def complete_update_before(self,text, line, begidx, endidx):
        return self.completions_list(text, ['True', 'False'])

    def show_results(self):
        if not self.RESULTS:
            print('No results to show. Run a test.\n')
        else:
            out_string_list = []
            out_string = ''
            opp: Opportunity
            for i, opp in enumerate(self.RESULTS):
                out_string_list.append(opp.get_string(pre_entries=[('uid', i)]))
            
            def combine(*strings):
                str_list = [s for s in strings if s]
                lines = zip(*(s.splitlines() for s in str_list))
                return '\n'.join('  '.join(line) for line in lines)

            def n_wise(iterable, n=2):
                "s -> (s0, s1), (s2, s3), (s4, s5), ..."
                a = iter(iterable)
                return zip_longest(*[iter(a)]*n, fillvalue='')

            pairs = n_wise(out_string_list)

            for i, j in pairs:
                out_string += combine(i, j) + '\n'

            print(out_string)

    def show_tracked(self):
        #TODO
        pass

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

    def cmdloop(self, intro=None):
        print(self.intro)
        while True:
            try:
                super().cmdloop(intro="")
                break
            except KeyboardInterrupt:
                print("^C")
                self.CUSTOM_PROMPT_NEEDED = False
                self.lastcmd = None
                self.postcmd(False, None)


if __name__ == '__main__':
    prompt = MyPrompt()
    prompt.prompt = '(q)> '
    prompt.intro = 'Quantify 0.0.0\n'
    prompt.cmdloop(intro=None)