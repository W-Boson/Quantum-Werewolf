\# Quantum Werewolf



Quantum Werewolf is a game based on the party game "The Werewolves of Millers Hollow" (known as "Die Werwölfe von Düsterwald" to german audiences) with a quantum mechanical twist: Players play in a superposition of possible games of werewolves!



This Version is a heavily modified and updated Version of one published by Jesse Straat (https://github.com/JesseStraat/Quantum-Werewolf)



Currently there is no installation or update option implemented, though this Git-Version will stay updated with Information About Version changes.





\## About



\### What is "The Werewolves of Millers Hollow"?



The Werewolves of Millers Hollow is a classic party game where each player (save the game master) gets a secret role card assigned to them.

There are two teams: the werewolves and the village (consisting of all roles except the werewolves).

At night, each player secretly takes an action corresponding to their role: The seer gets to see another player's card; Cupid can make two players fall in love; and the werewolves choose who they will eat that night.

During the day, all players vote on another player to be lynched.

The village's goal is to kill all werewolves, and the werewolves' goal is to kill all non-werewolves.

When only one faction is left, they win.



\### What is the quantum twist?



The quantum twist introduced in Quantum Werewolf is a superposition of roles.

This means that every player is every role at once, and gets to take actions corresponding to all roles at night.

Of course, the superposition can be collapsed by measurements.

Currently, there are three ways of measuring the superposition:



1\. A player uses his Seer action to look at someone else's role, partially collapsing the superposition (and introducing entanglement) by removing all possibilities in which the player is the Seer and the viewed person is a different role to the one opserved;

2\. There is an option to enable 'werewolfs can't eat other werewolfs', in this case choosing a victim as a werewolf removes all possibilities of both persons beeing werewolfs simultaneously;

3\. A player dies, which reveals his role to all players, collapsing the superposition quite a bit.



Since there is no way of knowing the final gamestate (in fact, your actions influence what the final measurement will be), it is important to players to "crack" the permutations and try to make the superposition collapse in their favour.



\## What are the rules?



\### Game setup



When you start a game of quantum werewolf, you are first prompted to enter the names of all participating players.

After entering and confirming the list of players, you are presented with the standard role selection of a number of werewolves and the seer.

You may refuse this role selection and choose the amount of werewolves as well as the additional roles.



A game of quantum werewolf needs at least 1 werewolf, optional roles are:



&#x20;\* Seer: Inspects the identity of a player each night, revealing their role to the seer.

&#x20;\* Cupid: Chooses two players to fall in love during the first night. Whenever one of the lovers dies, the other dies as well. The lovers win if they are the only 2 players left, regardless of role.

&#x20;\* Hunter: Whenever the hunter dies, they may choose to kill another player.



\### Night phase



During the night all special roles get to take their specific actions.

In quantum werewolf all players will take all their actions in turns.

During your turn you must specify how you would act as each role.

You are only promted for actions corresponding to roles for which you have a non-zero probability to be.

At the start of your turn you will be shown all the players that are still alive and the current distribution of your own role.

During your action as a werewolf you will be shown what the probability is that the other players are a werewolf together with you.

Furthermore after the first round and if cupid is in the game, you will also be shown the likelihood that each other player is your lover.



\### Day phase



At the start of the day phase all players that have died during the night will be revealed, as will their roles (this is a measurement and partially collapses the game).

After the reveal, the players are presented with the current state of the game in which all players and their chances of being each role is tabulated.

All players in the table are anomymous except for dead players.

The order of the players is random, but fixed throughout the game.



All players that are still alive must now discuss whoever they will lynch.

This discussion is separate from the interface of the game.

You should decide beforehand on the format of this discussion and how the lynch target will be decided.



\## References



Original "Schrödinger's Wolves" puzzle by Steven Irrgang in the 2008 CISRA puzzle competition:

https://web.archive.org/web/20080719133809/http://puzzle.cisra.com.au/D-5-Schroedingers-Wolves.pdf



Original solution and explanation:

https://web.archive.org/web/20181116123708/https://puzzle.cisra.com.au/2008/quantumwerewolf.html



Earlier Code-implementation:
https://github.com/JesseStraat/Quantum-Werewolf

