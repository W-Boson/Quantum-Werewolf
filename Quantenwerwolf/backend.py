from itertools import permutations
from random import shuffle, choice
from functools import wraps
from typing import Callable, List, Tuple, Union
from math import factorial
import logging

logger = logging.getLogger(__name__)


class Player:

    def __init__(self, index, name):
        self.index = index
        self.name = name
        self.killed = False
        self.witch_used = [False] * self.player_count
        self.logger = logging.getLogger(__name__)
        # can put lover list here


class Game:
    """Object keeping track of game state."""

    default_deck = {
            'werewolf': 2,
            'seer': 1,
            'witch': 0,
            'hunter': 0,
            'cupid': 0,
            }

    def __init__(self):
        self.players = []
        self.deck = Game.default_deck.copy()
        self.started = False
        self.logger = logging.getLogger(__name__)
        # optional rules
        self.werewolf_cannot_eat_werewolf = True
        self.start_with_subset = False
        self.witch_used = []
        self.witch_kills = []
        self.death_causes = {}

    @property
    def player_count(self):
        return len(self.players)

    # HELPER FUNCTIONS

    def started(value: bool = True) -> Callable:
        """Return decorator that return decorated function that only runs when the game has started (or not).

        Arguments:
            value: bool -- required value of Game.started for the decorated function to run (default: True)
        """
        def decorator(function: Callable) -> Callable:
            @wraps(function)
            def wrapper(self, *args: object, **kwargs: object) -> object:
                if self.started == value:
                    return function(self, *args, **kwargs)
                else:
                    raise ValueError(f'Game.started equal {self.started} when it should be {value}')
            return wrapper
        return decorator

    def _id(self, player_name: str) -> int:
        """Return index of a player name.

        Arguments:
            player_name: str -- name of a player in Game.players
        """
        return self.player_ids[player_name]

    def _name(self, player_id: int) -> str:
        """Return the name of a player index.
        """
        return self.players[player_id]

    # PLAYERS

    @started(False)
    def add_player(self, name: str) -> None:
        self.logger.debug(f"running add_players({name})")
        # Add names from input and input lists
        assert isinstance(name, str)
        if name in self.players:
            self.logger.debug(f"Player {name} already in self.players. Returning 'False'.")
            return False
        else:
            self.players.append(name)
            self.logger.debug(f"Added player {name} to self.players. Returning 'True'.")
            return True


    # DECK

    @started(False)
    def set_deck(self, deck: dict) -> bool:
        self.logger.debug(f"running set_deck({deck})")
        if self._valid_deck(deck):
            self.deck = deck
            self.logger.debug("Deck set. Returning True")
            return True
        self.logger.debug("Deck invalid and not set. Returning False.")
        return False

    @started(False)
    def _valid_deck(self, deck: dict) -> bool:
        self.logger.debug(f"running _valid_deck({deck})")
        thief_extra_cards = 2 if 'thief' in deck else 0
        deck_size = self.player_count + thief_extra_cards
        if 'villager' in deck:
            role_count = sum([count for role, count in deck.items()])
            if role_count != deck_size:
                self.logger.debug(f"{role_count=} does not equal {deck_size=}. Returning False.")
                return False
        else:
            nonvillager_count = sum([count for role, count in deck.items() if role != 'villager'])
            if nonvillager_count > deck_size:
                self.logger.debug(f"{nonvillager_count=} is larger than {deck_size=}. Returning False.")
                return False
            deck['villager'] = deck_size - nonvillager_count
        self.logger.debug("Deck is valid. Returning True.")
        return True

    @started(False)
    def set_suggested_deck(self) -> None:
        self.logger.debug("running set_suggested_deck()")
        if self.player_count < 8:
            self.logger.warning("It is recommended to play with at least 8 players.")
        werewolf_count = max(round(self.player_count / 5), 1)
        self.logger.debug(f"Suggested werewolf count is {werewolf_count}")

        suggested_deck = self.default_deck.copy()
        suggested_deck['werewolf'] = werewolf_count
        suggested_deck['seer'] = 1

        self.set_deck(suggested_deck)
        
    @started(False)
    def set_rules(self, werewolf_cannot_eat_werewolf: bool = False) -> None:
        """Set optional game rules before the game starts.
        
        Arguments:
        werewolf_cannot_eat_werewolf: bool -- if True, werewolves cannot attack other werewolves (default: False)
        """
        self.logger.debug(f"running set_rules(werewolf_cannot_eat_werewolf={werewolf_cannot_eat_werewolf})")
        self.werewolf_cannot_eat_werewolf = werewolf_cannot_eat_werewolf
        self.logger.info(f"Rule 'werewolf_cannot_eat_werewolf' set to {werewolf_cannot_eat_werewolf}")

    # GAMESTATE

    def generate_all_permutations(self):
        self.logger.info('Generating all role permutations')
        roles = [role for role, count in self.deck.items() for _ in range(count)]
        self.logger.debug(f'role frequencies: {roles}')
        self.permutations = {p: True for p in permutations(roles)}

    def _max_permutations(self):
        number = factorial(self.player_count)
        for n in self.deck.values():
            number /= factorial(n)
        return number

    def _subset_size(self):
        max_subset_size = self._max_permutations()
        return min(self.player_count + 2, max_subset_size)

    def generate_subset_permutations(self):
        self.logger.info('Generating subset of role permutations')
        roles = [role for role, count in self.deck.items() for _ in range(count)]
        self.logger.debug(f'role frequencies: {roles}')
        n_permutations = self._subset_size()
        self.permutations = {}
        while len(self.permutations) < n_permutations:
            shuffle(roles)
            self.permutations[tuple(roles)] = True

    @started(False)
    def start(self) -> bool:
        """Start the game and return succes boolean."""
        self.logger.debug("running start()")

        # Determine playercount
        self.logger.info(f"number of players is {self.player_count}")
        if self.player_count == 0:
            self.logger.error('No players in current game. Failed to start game.')
            return False

        # create lookup dictionary of player ids
        self.logger.info('Creating Lookup dictionary for player indices')
        self.player_ids = {player: player_id for player_id, player in enumerate(self.players)}

        # Generate permutation list for anomymous printing in print_probabilities()
        self.print_permutation = list(range(self.player_count))
        shuffle(self.print_permutation)
        self.logger.info(f'Random player order in tables is {self.print_permutation}')

        # Determine (valid) amount of villager in the game
        assert self._valid_deck(self.deck)

        # Sets the list of roles
        self.used_roles = [role for role, count in self.deck.items() if count > 0]
        self.logger.info(f'Roles used in game are {self.used_roles}')

        self.werewolf_count = self.deck['werewolf']
        self.logger.info(f'Number of live werewolves is {self.werewolf_count}')

        # Generates the list of role permutations
        #if self.start_with_subset:
        #    self.generate_subset_permutations()
        #else:
        self.generate_all_permutations()

        self.logger.debug(f'number of permutations: {len(self.permutations)}')

        # Set all players to be fully alive
        self.logger.info('Initializing attacked and killed list')
        self.deaths = []
        for i in range(self.player_count):
            self.deaths += [[0] * self.player_count]
        self.witch_kills = []
        for i in range(self.player_count):
            self.witch_kills += [[0] * self.player_count]
        self.killed = [False] * self.player_count
        self.witch_used = [False] * self.player_count     
        self.death_causes = {}

        # create list of cupid lovers
        self.logger.info('Initializing cupids lovers list')
        self.lovers_list = {}

        # start game
        self.logger.info('Set Game.started to True and turn to 0')
        self.started = True
        self.turn_counter = 0

        return True

    @started()
    def stop(self) -> None:
        """Stop the game."""
        self.logger.debug("running stop()")
        self.started = False
        
        # Free game state objects created in start()
        self.permutations = {}
        self.deaths = []
        self.witch_kills = []
        self.killed = []
        self.player_ids = {}
        self.lovers_list = {}
        self.print_permutation = []
        self.used_roles = []
        self.witch_used = []
        self.death_causes = {}
        self.werewolf_count = 0
        self.turn_counter = 0
        
        self.logger.info("Game stopped.")
        return True

    def reset(self) -> None:
        """Set all values to default and stop the game if started."""
        self.logger.debug("running reset()")
        self.players = []
        self.deck = Game.default_deck.copy()
        if self.started:
            self.stop()
        self.logger.info("Game reset.")

    # GAME INFO METHODS

    @started()
    def valid_permutations(self) -> List[List[str]]:
        """Return all possible game states."""
        return [p for p in self.permutations if self.permutations[p]]

    def living_players(self) -> List[str]:
        """Return all players that are still alive."""
        return [player for player_id, player in enumerate(self.players) if self.killed[player_id] == 0]


    @started()
    def check_deaths(self) -> List[str]:
        """Return names of players that have died but are not marked as such."""
        self.logger.debug("running check_deaths()")
        p_dead_list = self.death_probabilities()
        return [
            player
            for player_id, player in enumerate(self.players)
            if (
                not self.killed[player_id]
                and (
                    p_dead_list[player_id] >= 1
                    or player_id in self.death_causes
                ))]
        


    @started()
    def role_probabilities(self) -> Tuple[dict, ...]:
        """Return table of probability per role per player."""
        self.logger.debug("running role_probabilities()")
        p_list = self.valid_permutations()
        transpose = list(zip(*p_list))
        p_dead_list = self.death_probabilities()

        probs = []
        for i, p in enumerate(self.players):
            player_probs = {'name': p}
            for role in self.used_roles:
                player_probs[role] = transpose[i].count(role) / len(p_list)
            player_probs['dead'] = p_dead_list[i]
            probs.append(player_probs)
        return tuple(probs)

    

    @started()
    def death_probabilities(self) -> List[float]:
        """Return the probability of death for all players in a single pass.
        """
        self.logger.debug("running death_probabilities()")
        p_list = self.valid_permutations()
        n = len(p_list)
        
        # Start: bereits tote Spieler haben P=1, lebende P=0
        total_attacks = [1.0 if self.killed[i] else 0.0 for i in range(self.player_count)]
        
        # Vorberechnung: welche Spieler sind schon tot und haben einen Liebhaber?
        # (wird pro Permutation geprüft, aber killed[] ist global)
        has_cupid = self.deck.get('cupid', 0) > 0 and self.lovers_list
        
        for p in p_list:
            # Lover-Lookup für diese Permutation (None wenn kein Cupid)
            if has_cupid:
                cupid_id = p.index('cupid')
                lovers = self.lovers_list.get(cupid_id)
            else:
                lovers = None

            # Werewolf-Angriffssumme pro Spieler in dieser Permutation
            werewolf_attack = [0.0] * self.player_count
            if self.werewolf_count > 0:
                for i in range(self.player_count):
                    if p[i] == 'werewolf':
                        continue  # Werwölfe greifen sich selbst nicht an
                    for j in range(self.player_count):
                        if p[j] == 'werewolf':
                            werewolf_attack[i] += self.deaths[i][j]/ self.werewolf_count

            # Akkumuliere für jeden lebenden Spieler
            for i in range(self.player_count):
                if self.killed[i]:
                    continue  # bereits tot, bleibt 1.0

                witch_attack = 0.0

                for witch_id in range(self.player_count):
                    if p[witch_id] == 'witch':
                        witch_attack += self.witch_kills[i][witch_id]

                witch_attack = min(witch_attack, 1.0)   

                attack = max(werewolf_attack[i],witch_attack)

                # Liebhaber-Logik: stirbt, wenn Liebhaber stirbt
                lover_id = None
                if lovers is not None and i in lovers:
                    lover_id = lovers[1] if i == lovers[0] else lovers[0]

                if lover_id is not None:
                    if self.killed[lover_id]:
                        lover_attack = 1.0
                    else:
                        lover_attack = werewolf_attack[lover_id]
                    attack = max(attack, lover_attack)
                
                total_attacks[i] += attack
            
        return [t / n if not self.killed[i] else 1.0 for i, t in enumerate(total_attacks)]


    @started()
    def other_werewolves(self, werewolf: str) -> List[dict]:
        """Returns a table of players and their probabilities to be a werewolf simultaneously as a given werewolf.

        Arguments:
            werewolf: str -- name of player assumed to be a werewolf.
        """
        self.logger.debug(f"running other_werewolves({werewolf})")
        # Gives the probabilities of all other players being a werewolf
        werewolf_id = self._id(werewolf)
        p_list = self.valid_permutations()
        projection = [p for p in p_list if p[werewolf_id] == 'werewolf']

        if not projection:
            return []

        n_projection = len(projection)
        transpose = list(zip(*projection))

        probs = []
        for i, p in enumerate(self.players):
            P_werewolf = transpose[i].count("werewolf") / n_projection
            probs.append({'name': p, 'werewolf': P_werewolf})

        return probs

    @started()
    def other_lover(self, player: str) -> List[dict]:
        """Return table of players and their probabilities to be the lover of a given player.

        Arguments:
            player: str -- name of player
        """
        self.logger.debug(f"running other_lover({player})")
        player_id = self._id(player)

        lover_count_list = [0] * self.player_count
        p_list = self.valid_permutations()
        if self.lovers_list:
            if self.deck['cupid'] > 0:
                for p in p_list:
                    cupid_id = p.index('cupid')
                    lover1, lover2 = self.lovers_list[cupid_id]
                    if player_id == lover1:
                        lover_count_list[lover2] += 1
                    elif player_id == lover2:
                        lover_count_list[lover1] += 1

        probs = []
        for i, p in enumerate(self.players):
            P_lover = lover_count_list[i] / len(p_list)
            probs.append({'name': p, 'lover': P_lover})

        return probs

    @started()
    def check_win(self) -> Tuple[bool, str]:
        """Return wether any win condition is met and if so the faction that won."""
        all_dead = True
        villager_win = True
        werewolf_win = True
        lover_win = True

        p_list = self.valid_permutations()
        for p in p_list:
            lovers = ()
            if 'cupid' in p:
                cupid_id = p.index('cupid')
                lovers = self.lovers_list[cupid_id]
            for ID, role in enumerate(p):
                if self.killed[ID] == 0:
                    all_dead = False
                    if role == 'werewolf':
                        villager_win = False
                    else:
                        werewolf_win = False
                    if ID not in lovers:
                        lover_win = False

        if all_dead:
            self.logger.info('the game is a tie')
            return True, None
        if villager_win:
            self.logger.info('The villagers win')
            return True, 'villagers'
        if werewolf_win:
            self.logger.info('The werewolves win')
            return True, 'werewolves'
        if lover_win:
            self.logger.info('The lovers win')
            return True, 'lovers'
        return False, None

    @started()
    def process_night(self, actions):
        self.logger.debug(f"running process_night({actions})")
        for player, player_actions in actions.items():
            for role, args in player_actions.items():
                if role == 'cupid':
                    self.cupid(player, *args)
                    
                elif role == 'seer':
                    self.seer(player, *args)

                elif role == 'werewolf':
                    self.werewolf(player, args)

                elif role == 'witch':
                    continue

    # ROLE ACTIONS

    @started()
    def cupid(self, cupid: str, lover1: str, lover2: str) -> None:
        """Perform cupid action for a player. Records the lover pair in Game.lovers_list."""
        self.logger.debug(f"running cupid({cupid}, {lover1}, {lover2})")
        cupid_id = self._id(cupid)
        lovers = (self._id(lover1), self._id(lover2))
        self.lovers_list[cupid_id] = lovers

    @started()
    def seer(self, seer: str, target: str, target_role: str = None, project: bool = True) -> str:
        """Perform the seer action for a players. Return target's role and collapse game state..

        Arguments:
            seer: str -- name of playerperforming the seer action.
            target: str -- name of target of the seer action
        """
        self.logger.debug(f"running seer({seer}, {target}, target_role={target_role}, project={project})")
        seer_id = self._id(seer)
        target_id = self._id(target)

        # Check if player and target are alive and player can be the seer
        assert self.killed[seer_id] != 1, "ERROR: in seer() seer {} is dead.".format(seer)
        assert self.killed[target_id] != 1, "ERROR: in seer() target {} is dead.".format(target)
        # assert self.probs[seer_id]['seer'] != 0, "ERROR: in seer() {}'s seer probability is 0.".format(seer)

        # Player is allowed to take the action
        self.logger.info("{} is investigating {} ...".format(seer, target))
        p_list = self.valid_permutations()
        projection = [p for p in p_list if p[seer_id] == 'seer']

        if projection:
            # Choose an outcome
            if target_role is None:
                target_role = choice(projection)[target_id]

            # Collapse the wave function
            if project:
                for p in projection:
                    if p[target_id] != target_role:
                        self.permutations[p] = False

        # Report on results
        self.logger.info(f"{seer} sees that {target} is a {target_role}!")

        return target_role

    @started()
    def werewolf(self, werewolf, target):
        """Perform werewolf action for a player. Mark the attack in Game.deaths.
        Optionally collapses the game to exclude werewolves targeting werewolves. [CAUSES PROBLEMS]

        Arguments:
            werewolf: str -- name of the player performing the werewolf action
            target: str -- name of target of the werewolf action

        kill chance is 1 over number of werewolves still alive.
        If werewolves may not eat other werewolves then all permutations in which acting player and target are both werewolves are no longer possible.
        """
        self.logger.debug(f"running werewolf({werewolf}, {target})")
        assert werewolf != target, "ERRROR: in werwwolf() werewolf == target."
        werewolf_id = self._id(werewolf)
        target_id = self._id(target)
        assert self.killed[werewolf_id] != 1, "ERROR: in werewolf() werewolf {} is dead".format(werewolf)
        assert self.killed[target_id] != 1, "ERROR: in werewolf() target {} is dead".format(target)
        # assert self.probs[werewolf_id]['werewolf'] != 0, "ERROR: in werewolf() {}'s werewolf probability is 0".format(target)

        self.deaths[target_id][werewolf_id] = 1

        if not self.werewolf_cannot_eat_werewolf:
            return True

        previous_permutations = self.permutations.copy()

        for world in self.valid_permutations():
            if world[werewolf_id] == 'werewolf' and world[target_id] == 'werewolf':
                self.permutations[world] = False

        if self.valid_permutations():
            return True

        self.permutations = previous_permutations

        possible_werewolf_ids = set()
        for world in self.valid_permutations():
            for player_id, role in enumerate(world):
                if role == 'werewolf':
                    possible_werewolf_ids.add(player_id)

        for player_id in possible_werewolf_ids:
            if not self.killed[player_id]:
                self.death_causes[player_id] = ('because the werewolves ate themselves')
        self.logger.warning("The werewolves have eaten themselves.")

        return False
    
    
    @started()
    def choose_witch_world(self, witch):
        """
        Randomly choose a possible werewolf combination from worlds
        in which the player is the witch.
        
        Worlds in which the player is not the witch remain valid.
        Within witch-worlds, worlds are removed if one of the
        measured players is not a werewolf.
        """
        witch_id = self._id(witch)
        valid_worlds = self.valid_permutations()
        
        possible_combinations = set()
        
        for world in valid_worlds:
            if world[witch_id] != 'witch':
                continue

            werewolves = tuple(
                self.players[player_id]
                for player_id, role in enumerate(world)
                if role == 'werewolf'
                )

            possible_combinations.add(werewolves)

        if not possible_combinations:
            return None

        measured_werewolves = choice(
            list(possible_combinations)
            )

        measured_werewolf_ids = {
            self._id(player)
            for player in measured_werewolves
            }
        
        witch_worlds = []

        for world in valid_worlds:
            # Welten, in denen die Person nicht Hexe ist,
            # bleiben immer erhalten.
            if world[witch_id] != 'witch':
                continue

            # Nur Hexen-Welten entfernen, in denen mindestens
            # ein gemessener Werwolf kein Werwolf ist.
            if any(
                    world[player_id] != 'werewolf'
                    for player_id in measured_werewolf_ids
                    ):
                self.permutations[world] = False
                continue
            
            witch_worlds.append(world)

        remaining_worlds = tuple(
            world
            for world in valid_worlds
            if self.permutations[world]
            )

        self.witch_used[witch_id] = True

        self.logger.info(
            f"Witch measured werewolves: "
            f"{measured_werewolves}"
            )

        self.logger.info(
            f"{len(remaining_worlds)} possible worlds remain."
            )

        return tuple(witch_worlds), measured_werewolves
    
    
    
    @started()
    def witch_world_information(self, worlds):
        """
        Return role information shared by all selected worlds.
        
        A role is only shown as certain if it is identical
        in every remaining selected world.
        """
        if not worlds:
            return []

        # Backward compatibility:
        # Accept one world as well as multiple worlds.
        if isinstance(worlds[0], str):
            worlds = (worlds,)

        information = []

        for player_id, player in enumerate(self.players):
            roles = {world[player_id] for world in worlds}

            if len(roles) == 1:
                role = next(iter(roles))
            else:
                role = 'good'

            information.append({'name': player,'role': role,})

        return information
    
    @started()
    def possible_werewolf_combinations(self, witch):
        """
        Return all possible werewolf combinations in worlds
        where the given player is the witch.
        """
        witch_id = self._id(witch)
        combinations = set()

        for world in self.valid_permutations():
            if world[witch_id] != 'witch':
                continue

            werewolves = tuple(self.players[player_id] for player_id, role in enumerate(world) if role == 'werewolf')
            combinations.add(werewolves)

        return sorted(combinations)
    
    
    @started()
    def wolf_targets_in_world(self, world):
        """
        Return players attacked by at least one werewolf
        in the selected world.
        """
        attack_counts = self.attack_counts_in_world(world)

        return [player for player, count in attack_counts.items()
        if count > 0]
    
    @started()
    def witch_save(self, target, measured_werewolves):
        """
        Remove all recorded attacks by the measured werewolves
        against the selected target.
        """
        target_id = self._id(target)
        removed_attacks = 0

        for werewolf in measured_werewolves:
            werewolf_id = self._id(werewolf)

            if self.deaths[target_id][werewolf_id]:
                self.deaths[target_id][werewolf_id] = 0
                removed_attacks += 1

        self.logger.info(f"Witch saved {target} by removing " f"{removed_attacks} werewolf attacks.")

        return removed_attacks
            
    @started()
    def witch_kill(self, witch, target):
        """
        Store a possible witch kill.
        
        The kill only applies in worlds where the given player
        is actually the witch.
        """
        witch_id = self._id(witch)
        target_id = self._id(target)

        if self.witch_used[witch_id] is False:
            raise ValueError(f"{witch} must use the witch ability first.")

        if self.killed[target_id]:  
            raise ValueError(f"{target} is already dead.")

        self.witch_kills[target_id][witch_id] = 1

        self.logger.info(f"{witch} stored a possible witch kill against {target}.")

        return target
    
    
    def attack_counts_in_world(self, measured_werewolves):
        counts = []
        
        measured_werewolf_ids = [
        self._id(player)
        for player in measured_werewolves
    ]

        for target_id in range(self.player_count):
            count = 0
            for werewolf_id in measured_werewolf_ids:
                count += self.deaths[target_id][werewolf_id]
            counts.append(count)

        return counts
        
    
    @started()
    def kill(self, target: str) -> str:
        """Kill and identify a player. Return the player's role and collapses the game state.

        Arguments:
            target: str -- name of player to kill.
        """
        self.logger.debug(f"running kill({target})")
        target_id = self._id(target)
        assert self.killed[target_id] != 1, "ERROR:in kill() target {} is already dead.".format(target)

        self.logger.info("{} was killed!".format(target))

        # Chooses an outcome
        p_list = self.valid_permutations()
        result = choice(p_list)
        target_role = result[target_id]

        # Collapse the wave function
        for p in p_list:
            if p[target_id] != target_role:
                self.permutations[p] = False

        # Report on results
        self.logger.info(f"{target} was a {target_role}!")

        # Deal with the case that the dead person is a werewolf
        if target_role == "werewolf":
            self.werewolf_count -= 1
            for i in range(self.player_count):
                self.deaths[i][target_id] = 0

        self.killed[target_id] = 1

        return target_role

    def _lover(self, permutation: List[str], player_id: int) -> int:
        """Return the index of the lover of a player in a given permutation if they exits, otherwise returns None.

        Arguments:
            permutation: List[str] -- permutation in which to check for lover.
            player_id: int -- index of player for which to check lover.
        """
        if self.deck['cupid'] == 0 or not self.lovers_list:
            return None
        lover_id = None
        cupid_id = permutation.index('cupid')
        lover1, lover2 = self.lovers_list[cupid_id]
        if player_id == lover1:
            lover_id = lover2
        elif player_id == lover2:
            lover_id = lover1
        return lover_id

    def _werewolf_attack(self, permutation: List[str], player_id: int) -> int:
        """Return the total sum of werewolf attacks of a player in a given permutation.

        Arguments:
            permutation: List[str] -- permutation in which to sum the werewolf attacks.
            player_id: int -- index of player for which to check werewolf attacks.
        """
        werewolf_attacks = 0
        for i in range(self.player_count):
            if permutation[i] == "werewolf" and permutation[player_id] != "werewolf":
                werewolf_attacks += self.deaths[player_id][i]/ self.werewolf_count
        return werewolf_attacks

    
    @started()
    def process_deaths(self, killed_players, cause=''):
        death_log = []
        pending_hunter = None
        
        for player in killed_players:
            player_id = self._id(player)
            player_cause = self.death_causes.pop(player_id, cause)
            role = self.kill(player)
            death_log.append((player, role, player_cause))
            if role == 'hunter':
                pending_hunter = player

        if killed_players:
            chained_players = self.check_deaths()
            chained_log, chained_hunter = self.process_deaths(chained_players)
            death_log.extend(chained_log)
            if pending_hunter is None:
                pending_hunter = chained_hunter

        return death_log, pending_hunter


    @started()
    def start_day(self):
        killed_players = self.check_deaths()
        return self.process_deaths(killed_players,cause='by the werewolves')


    @started()
    def end_day(self, lynch_target, cause=''):
        return self.process_deaths([lynch_target], cause='by the villagers')