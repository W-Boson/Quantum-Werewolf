import logging
from os import system, get_terminal_size
from backend import Game

logger = logging.getLogger(__name__)
logging.basicConfig(filename='debug.log', level=logging.DEBUG)


class CliGame:

    # Define colors
    normal = '\033[0;37m'
    bold = '\033[1;37m'
    italic = '\033[3;37m'
    underline = '\033[4;37m'
    red = '\033[0;31m'
    boldred = '\033[1;31m'
    pink = '\033[0;35m'
    boldpink = '\033[1;35m'
    yellow = '\033[0;33m'
    boldyellow = '\033[1;33m'
    green = '\033[0;32m'
    boldgreen = '\033[1;32m'
    blue = '\033[0;34m'
    boldblue = '\033[1;34m'

    role_style = {
        'villager': yellow,
        'werewolf': red,
        'seer': pink,
        'hunter': green,
        'cupid': blue,
        }

    role_style_bold = {
        'villager': boldyellow,
        'werewolf': boldred,
        'seer': boldpink,
        'hunter': boldgreen,
        'cupid': boldblue,
        }

    role_preposition = {
        'villager': 'a ',
        'werewolf': 'a ',
        'seer': 'the ',
        'hunter': 'the ',
        'cupid': '',
        }

    name_length = 12
    def __init__(self):
        self.game = Game()
        self.logger = self.game.logger
        columns = get_terminal_size().columns
        if columns < 100:
            if columns < 69:
                if columns < 45:
                    print(f"{self.boldred}WARNING: screen is too narrow for the game{self.normal}")
                    self.bar_length = 12
                else:
                    self.bar_length = columns - 27
            else:
                self.bar_length = 36
        else:
            self.bar_length = 72

    def ask_yesno(self, query, yes, no):
        self.logger.debug(f'running ask_yesno({query}, {yes}, {no})')
        answer = input(query + ' (yes/no) ')
        if answer == 'yes' or answer == 'y':
            if callable(yes):
                return yes()
            else:
                return yes
        elif answer == 'no' or answer == 'n':
            if callable(no):
                return no()
            else:
                return no
        else:
            print('invalid answer')
            return self.ask_yesno(query, yes, no)

    def ask_player(self, query, invalid_players=[]):
        answer = input(query + 'Name: ')

        if answer.isdecimal():
            i = int(answer) - 1
            if i in range(self.game.player_count):
                answer = self.game.players[i]

        valid_players = self.game.living_players()
        for player in invalid_players:
            if player in valid_players:
                valid_players.remove(player)

        if not valid_players:
            return None

        if answer in valid_players:
            return answer
        else:
            print(f'    {self.red}"{answer}" is not a valid choice{self.normal}')
            print('    Valid players are:')
            for i, p in enumerate(valid_players):
                print("      {}".format(p))

            return self.ask_player(query, invalid_players=invalid_players)

    def ask_number(self, query, valid_numbers=None):
        answer = input(query)
        if answer.isdigit():
            return int(answer)
        else:
            print('  "{}" is not a valid choice'.format(answer))
            return self.ask_number(query)
        
    def table_label(self, player_id):
        index = self.game.print_permutation.index(player_id)
        return chr(ord('A') + index)

    def print_probability_bars(self, game_over=False):
        probabilities = self.game.role_probabilities()

        # print header
        print(f"{self.bold}{'ID':>3} {'Name':>{self.name_length}} {'Role Distribution':<{self.bar_length}}{'Deadness':>11}{self.normal}")

        # print bars
        for i in self.game.print_permutation:
            p = probabilities[i]
            name = '???'
            if p['dead'] == 1 or game_over:
                name = p['name']
            table_index = self.game.print_permutation.index(i)
            table_label = chr(ord('A') + table_index)
            line = f"{table_label:>3} {str(name):>{self.name_length}} "
            total_chance = 0.0
            total_length = 0
            for role in self.game.used_roles:
                letter = role[0].capitalize()
                chance = p[role]
                total_chance += chance
                total_length_new = round(total_chance * self.bar_length)
                length = total_length_new - total_length
                
                if length <= 0:
                    length = 0
                    if chance > 0:
                        length = 1
                        total_length_new = total_length_new + 1
                    
                total_length = total_length_new
                line += f"{self.role_style_bold[role]}{letter * length}"
            line += f"{self.normal}{100*p['dead']:5.0f}% dead"
            print(line)

        # print legend
        legend = ""
        for role in self.game.used_roles:
            legend += f"{self.role_style_bold[role]}{role.title()}, "
        print(f'\n        {self.bold}Legend: {legend[:-2]}.{self.normal}')

    def print_kill(self, player, cause=''):
        player_role = self.game.kill(player)
        print(f'\n  {player} was killed {cause}')
        print(f'    {player} was {self.role_preposition[player_role]}{player_role}\n')
        return player_role

    
    def print_death_log(self, death_log):
        for player, role, cause in death_log:
            print(f'\n  {player} was killed {cause}')
            print(f'    {player} was {self.role_preposition[role]}{role}\n')


    def resolve_hunter(self, pending_hunter):
        while pending_hunter and self.game.living_players():
            print(f'    {pending_hunter} must now kill another player')
            hunter_target = self.ask_player(
                f'\n  {self.boldgreen}[HUNTER]{self.normal} {pending_hunter}, who do you shoot?\n    '
                )
            
            death_log, pending_hunter = self.game.end_day(hunter_target, cause='by the hunter')
            self.print_death_log(death_log)
            
    def print_win(self):
        win, winners = self.game.check_win()
        if win:
            if winners is None:
                print("THE GAME IS A TIE!")
            else:
                print(f"\n\n{self.bold}THE {winners.upper()} WIN!{self.normal}\n")
            self.print_probability_bars(game_over=True)
            self.game.stop()
        return win

    def get_players(self):
        # Get player names
        print("Enter player names")
        print("Enter no name to continue.")
        new_player = True
        while new_player:
            name = input(f"  Name player {self.game.player_count + 1}: ")
            if name == '':
                if self.game.player_count < 3:
                    print(f'\033[F{self.red}  This game needs at least 3 players to play! Add more players.{self.normal}\033[K')
                else:
                    new_player = False
            elif not name.isalpha():
                print(f"\033[F{self.red}  Name may only contain letters!{self.normal}\033[K")
            elif len(name) > self.name_length:
                print(f"\033[F{self.red}  Name cannot be longer than 12 characters!{self.normal}\033[K")
            else:
                if not self.game.add_player(name):
                    print(f"\033[F{self.red}  Name {name} already in use!{self.normal}\033[K")

    def print_players(self):
        # display players
        print("Current Players:")
        for i, p in enumerate(self.game.players):
            print(f"{i+1:3d}: {p}")

    def print_live_players(self):
        # display live players
        print(f"  {self.underline}Live Players:{self.normal}")
        live_players = self.game.living_players()
        for i, p in enumerate(self.game.players):
            if p in live_players:
                print(f"  {i+1:3d}: {p}")

        if self.game.turn_counter == 1:
            print(f'\n  {self.italic}Hint: you can also use player numbers instead of names{self.normal}')

    def print_deck(self, hide_unused=False):
        for (role, count) in self.game.deck.items():
            if count == 0:
                if hide_unused:
                    continue
                else:
                    name = role
                    count = 'no'
            elif count == 1:
                name = role
            elif count > 1:
                if role == 'werewolf':
                    name = 'werewolves'
                else:
                    name = role + 's'
            print(f"{count:>4} {name}")

    def get_deck(self):
        self.logger.debug('running get_deck()')

        def ask_deck():
            self.logger.debug('running ask_deck()')
            # ask for new roles
            print('')
            deck = {}
            for role in self.game.default_deck.keys():
                if role == 'werewolf':
                    deck['werewolf'] = self.ask_number('Number of werewolves: ')
                elif role == 'villager':
                    continue
                else:
                    deck[role] = self.ask_yesno(f'Include {role}?', 1, 0)

            # check for valid deck
            if self.game.set_deck(deck):
                self.logger.debug('Received asked deck. Returning False.')
                return False
            else:
                print(f"{self.red}Too many roles for numer of players. Try again.{self.normal}")
                self.logger.debug('Deck not valid. Asking again.')
                return ask_deck()

        self.game.set_suggested_deck()

        deck_confirmed = False
        while deck_confirmed is False:
            print("\nPlay with following roles?")
            self.print_deck()
            deck_confirmed = self.ask_yesno('', True, ask_deck)
        
        self.get_rules()

    def get_rules(self):
        """Ask for optional game rules and apply them."""
        print('\nOptional rules:')
        werewolf_cannot_eat_werewolf = self.ask_yesno(
            f'  {self.boldred}Werewolves cannot eat other werewolves?{self.normal}',
            yes=True,
            no=False
            )
        self.game.set_rules(werewolf_cannot_eat_werewolf=werewolf_cannot_eat_werewolf)

    def get_player_actions(self, player, player_role_probabilities, player_other_werewolves, player_other_lover):
        self.logger.debug(f"running get_player_actions({player}, {player_role_probabilities}, {player_other_werewolves}, {player_other_lover})")
        player_actions = {}
        # cupid
        if 'cupid' in self.game.used_roles:
            if self.game.turn_counter == 1 and player_role_probabilities['cupid'] != 0:
                # query cupid action
                first_lover = self.ask_player(f'\n  {self.boldblue}[CUPID]{self.normal} Who do you choose as first lover?\n    ')
                second_lover = self.ask_player(f'  {self.boldblue}[CUPID]{self.normal} Who do you choose as second lover?\n    ', invalid_players=[first_lover])
                player_actions['cupid'] = (first_lover, second_lover)
                print(f'  {self.boldblue}[CUPID]{self.normal} {first_lover} and {second_lover} are now lovers.')
            elif self.game.turn_counter > 1:
                # print lover probabilities
                print(f'\n  {self.boldblue}[CUPID]{self.normal} Your lover is:')
                for p in player_other_lover:
                    name = p['name']
                    chance = p['lover']
                    if name != player:
                        length = round(chance * self.bar_length)
                        print(f'    {name:>{self.name_length}}: {100*chance:3.0f}% {self.boldblue}{"L" * length}{self.normal}')

        # seer
        if 'seer' in self.game.used_roles and player_role_probabilities['seer'] != 0:
            target = self.ask_player(f'\n  {self.boldpink}[SEER]{self.normal} Whose role do you inspect?\n    ')
            target_role = self.game.seer(player, target, project=False)
            player_actions['seer'] = (target, target_role)
            print(f'  {self.boldpink}[SEER]{self.normal} You see that {target} is {self.role_preposition[target_role]}{self.role_style_bold[target_role]}{target_role}.')

        # werewolf
        if 'werewolf' in self.game.used_roles and player_role_probabilities['werewolf'] != 0:
            invalid_players = [player]
            # print other werewolves
            print(f'\n  {self.boldred}[WEREWOLF]{self.normal} Your fellow werewolves are:')
            for p in player_other_werewolves:
                name = p['name']
                chance = p['werewolf']
                if name != player:
                    length = round(chance * self.bar_length)
                    print(f'    {name:>{self.name_length}}: {100*chance:3.0f}% {self.boldred}{"W"*length}{self.normal}')
                if chance == 1 and name != player and name in self.game.living_players():
                    invalid_players.append(name)

            if self.game.living_players() != invalid_players:
                # do werewolf action
                target = self.ask_player(f'\n  {self.boldred}[WEREWOLF]{self.normal} Who do you attack?\n    ', invalid_players=invalid_players)
                player_actions['werewolf'] = (target)

        return player_actions

    def print_player_role(self, player_probabilities):
        # display game and player info (role superposition)
        print(f'\n  {self.underline}Your role:{self.normal}')
        for role in self.game.used_roles:
            style = self.role_style[role]
            letter = role[0].capitalize()
            chance = player_probabilities[role]
            length = round(chance * self.bar_length)
            print(f"    {style}{role:>8s}: {100*chance:3.0f}% |{letter * length:<{self.bar_length}}|{self.normal}")


def cli():

    system('clear')

    g = CliGame()
    g.get_players()

    system('clear')

    g.print_players()
    g.get_deck()

    system('clear')

    g.game.start()

    # loop turns for every player
    while g.game.started:
        g.game.turn_counter += 1

        # night
        system('clear')
        print('Night falls and all players take their actions in turns privately\n')

        start_probabilities = g.game.role_probabilities()

        # collect all player actions
        actions = {}
        for player_id, player in enumerate(g.game.players):
            player_role_probabilities = start_probabilities[player_id]
            player_other_lover = g.game.other_lover(player)
            player_other_werewolves = g.game.other_werewolves(player)

            # if player is dead skip turn
            if g.game.killed[player_id] == 1:
                continue
            
            table_label = g.table_label(player_id)
            input(f"{player}'s turn (press ENTER to continue)")
            system('clear')
            
            print(f"{player}'s turn\n")
            
            g.print_live_players()
            
            print(f"\n {g.red}!!! You are {table_label} in the list !!!\n")

            g.print_player_role(player_role_probabilities)

            player_actions = g.get_player_actions(player, player_role_probabilities, player_other_werewolves, player_other_lover)

            # pass the actions for the player
            actions[player] = player_actions

            input("\n(press ENTER to continue)")

            system('clear')

        # process actions
        g.logger.debug(g.game.valid_permutations())
        g.game.process_night(actions)
        g.logger.debug(g.game.valid_permutations())

        # day
        input('All player have had their turn (press ENTER to continue)')
        system('clear')

        print('The day begins and the villagers awaken.\n')
        death_log, pending_hunter = g.game.start_day()
        g.print_death_log(death_log)
        g.resolve_hunter(pending_hunter)
        

        # check win before the vote
        if g.print_win():
            break

        # show live players
        g.print_live_players()

        # Show current game state
        print('\n  These are the current roles of the players:')
        g.print_probability_bars()

        # vote
        print('\n  All players that are still alive must now choose one player to lynch.')
        lynch_target = g.ask_player(f'\n  {g.boldyellow}[ALL VILLAGERS]{g.normal} Who do you lynch?\n    ')

        death_log, pending_hunter = g.game.end_day(lynch_target)
        g.print_death_log(death_log)
        g.resolve_hunter(pending_hunter)

        # check win after the vote
        if g.print_win():
            break

        input('(press ENTER to continue)')


if __name__ == '__main__':
    cli()
