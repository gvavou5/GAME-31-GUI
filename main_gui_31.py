############################################################################
################################## GUI-31 ##################################
############################################################################

############################################################################
################################## How it works? ######################
############################################################################
'''
This is a simple version of game 31.
Two players are playing, the PC(Big-Blue) and a player that we choose.
First Big-Blue is playing first and after the player.
Every player is taking cards and the goal is to reach the highest possible score. If the score is more than 31
then automatically is lost and the winner is the other player without playing.
If both players have score less or equal of 31, the winner is the player with the highest score.
If they have the same score there is no winner in the specific round.
'''

import PlayingCards as pc
from thirtyone import Player, Game # classes Player, Game are imported from the first version of the game
import tkinter as tk
import os
from tkinter import simpledialog
import pickle
import random

class GUICard():
    # this class is responsible for the graphical interface of the Card
    theCards = {}
    def __init__(self, card, canvas):
        self.canvas = canvas
        self.value = card.value
        self.symbol = card.symbol
        self.position = None
        self.image = None
        GUICard.theCards[card] = self
    def _fetch_image(self):
        if self.face:
            return CardImages.images[self.symbol][pc.Deck.values.index(self.value)]
        else: return CardImages.images['b']
    def _animate_image(self):
        self.canvas.move(self.image, self.img_vx, self.img_vy)
        x1,y1,x2,y2 = self.canvas.bbox(self.image)
        if abs(x1 - self.position[0]) < 5 and abs(y1 - self.position[1]) < 5:
            return
        else:
            self.canvas.update_idletasks()
            self.canvas.after(20, self._animate_image)
    def set_face(self, face):
        if self.position and face != self.face:
            self.face = face
            self.canvas.itemconfig(self.image, image= self._fetch_image())
        else:
            self.face = face
    def move_to(self, new_position):
        if not self.position: self.position = new_position
        if not self.image:
            self.image = self.canvas.create_image(*self.position, image =  self._fetch_image())
        self.canvas.itemconfig(self.image, anchor='nw')
        if new_position != self.position:
            self.img_vx = (new_position[0] - self.position[0]) / 20
            self.img_vy = (new_position[1] - self.position[1]) / 20
            self._animate_image()
            self.position = new_position
    def __str__(self):
        out = self.value + self.symbol
        if self.position:
            out += '['+str(self.position[0])+','+str(self.position[1])+']'
        return out

class CardImages():
    # this class is responsible for the image creation of the cards by srpitesheet
    image_file = 'cards.gif'
    path = '.'
    imagefile = os.path.join(path, image_file)
    images = {}
    @staticmethod
    def generate_card_images():
        # Create the image of the cards (79x123 px) from the spritesheet cards2.gif
        num_sprites = 13
        place = 0
        spritesheet = tk.PhotoImage(file= CardImages.imagefile)
        for x in 'sdhc':
            CardImages.images[x] = [CardImages._subimage(79 * i, 0 + place, \
                                            79 * (i + 1), 123 + place, spritesheet) for i in range(num_sprites)]
            place += 123
        CardImages.images['b'] = CardImages._subimage(0, place, 79, 123 + place, spritesheet) #back image
    @staticmethod
    def _subimage(l, t, r, b, spritesheet):
        dst = tk.PhotoImage()
        dst.tk.call(dst, 'copy', spritesheet, '-from', l, t, r, b, '-to', 0, 0)
        return dst

class ComputerPlayer(Player):
    # Player corresponding behavior
    def __init__(self, canvas, deck):
        self.canvas = canvas
        self.name = 'Big Blue'
        self.deck = deck
        self.score = 0
        self.hand = []  # player's cards
        self.start = GUI.padx, GUI.pady  # NW corner for player's cards
        self.next_card_position = self.place_of_next_card()
        self.message_place = self.start[0], round(self.start[1] + GUI.card_height * 1.1)
        self.infomessage = ""
        self.my_message = self.canvas.create_text(*self.message_place,
                                                  fill="white", text=self.infomessage, font="Arial 30", anchor='nw')
        self.active = False

    def place_of_next_card(self):
        return self.start[0] + (GUI.card_width // 2) * len(self.hand), self.start[1]

    def receive(self, card):  # gives a new card to player
        self.hand.append(card)
        self.next_card_position = self.place_of_next_card()
        return len(self.hand) - 1

    def plays(self, face=False):
        if self.active:
            card = GUICard.theCards[self.deck.draw()]
            card.set_face(face)
            card.move_to(self.place_of_next_card())
            self.receive(card)
            card_value = self._calculate_value(card)
            self.score += card_value
            self._check_if_exceeded()
            if self._computer_strategy():
                root.after(1000, self.plays)
            else:
                self.show_cards()
                self.active= False
                if self.score == -1:
                    self.update_message()

    def show_cards(self, all=False):
        if self.score == -1 or all:
            for card in self.hand:
                card.set_face(True)
        else:
            card_to_hide = random.randint(0, len(self.hand)-1)
            for i, card in enumerate(self.hand):
                if i != card_to_hide:
                    card.set_face(True)

    def _computer_strategy(self):
        return False if self.score >= 25 or self.score == -1 else True  #

    def update_message(self):
        self.canvas.delete(self.my_message) # Delete current message
        if self.score == -1:
            self.infomessage = "{}: You are out of score limits. Try again!".format(self.name)
        else:
            self.infomessage = "{} score is: {}".format(self.name, self.score)
        self.my_message = self.canvas.create_text(*self.message_place,fill="white", text=self.infomessage,
                                                  font="Arial 30", anchor='nw')


class HumanPlayer(ComputerPlayer):
    # this class is responsible only the human player

    counter = 0 # ask for username if it is the first game
    all_time_name = "" # hold username for the next games
    def __init__(self, *args, **kwds):
        ComputerPlayer.__init__(self, *args, **kwds)
        self.start = GUI.padx, GUI.board_height - GUI.pady - GUI.card_height
        self.message_place = self.start[0], round(self.start[1] - 0.6 * GUI.card_height)
        if HumanPlayer.counter == 0:
            HumanPlayer.all_time_name = simpledialog.askstring("Title", "Give a username")
            # the username should not be EMPTY or Big Blue. In these cases I force the username to be Uplayer
            if HumanPlayer.all_time_name != None and HumanPlayer.all_time_name != "" and HumanPlayer.all_time_name != "Big Blue":
                self.name = HumanPlayer.all_time_name
            else:
                HumanPlayer.all_time_name = "Uplayer"
                self.name = "Uplayer"
            HumanPlayer.counter += 1
        else:
            # this is not the first game, thus you already have the username
            self.name = HumanPlayer.all_time_name

    def plays(self, face=True):
        if self.active:
            card = GUICard.theCards[self.deck.draw()]
            card.set_face(face)
            card.move_to(self.place_of_next_card())
            self.receive(card)
            card_value = self._calculate_value(card)
            self.score += card_value
            self._check_if_exceeded()
            self.update_message()
            root.update_idletasks()
            if self.score == -1:
                self.active = False
                app.find_winner()

class GUI():
    # this class is responsible for the parameters of the graphical interface
    board_width, board_height = 900, 600  # canvas size
    card_width, card_height = 79, 123  # card size
    padx, pady = 50, 50
    deck = (800, 230)
    # cards region
    deck_of_cards_area = (deck[0], deck[1], deck[0] + card_width, deck[1] + card_height)
    @staticmethod
    def in_area(point, rect):
        if point[0]>= rect[0] and point[0] <= rect[2] \
            and point[1] >= rect[1] and point[1] <= rect[3]:
            return True
        else:
            return False

class GUIGame(Game, GUI)  :
    # Game Controller - Interface and Players Creator
    def __init__(self, root):
        ##### Game parameters
        self.root = root
        root.title("Game 31 -- GUI")
        root.resizable(width='false', height='false')
        ##### GUI parameters
        self.infomessage_position = GUI.padx, GUI.board_height // 2 - 22
        self.top_font = 'Arial 20'
        self.f = tk.Frame(root)
        self.f.pack(expand=True, fill='both')
        self.create_widgets()
        self.run = False
        self.winner = None
        self.username = None
        self.number_of_plays = 0 # games counter
        self.database_name = 'pickle_database.db' # database for holding the best scores observed
        self.font_message = "Menlo 15"


    def create_widgets(self):
        self.f1 = tk.Frame(self.f)
        self.f1.pack(fill='both')

        # New Game Button
        self.button_new_game = tk.Button(self.f1, text='New Game', font=self.top_font, command=self.play_game, width=9)
        self.button_new_game.pack(side='left', fill='x')

        # Stop Button
        self.button_enough = tk.Button(self.f1, text='Stop', font=self.top_font, command=self.stop, width=5, fg='red')
        self.button_enough.pack(side='left', fill='x')
        self.button_enough.configure(state='disabled') # Πρεπει να ειναι και στην αρχη disabled

        # Textvariable for refreshing the score
        self.thescore = tk.StringVar()
        tk.Label(self.f1, textvariable=self.thescore, font=self.top_font, width=35).pack(side='left', fill='x')

        # Save Score Button
        self.button_save_score = tk.Button(self.f1, text='Save Score', font=self.top_font, command=self.save_score, width=12)
        self.button_save_score.pack(side='right', fill='x')
        self.button_save_score.configure(state='disabled')

        # Hall of Fame Button
        self.button_hall_of_fame = tk.Button(self.f1, text="Best Scores", font=self.top_font, command=self.info, width=12)
        self.button_hall_of_fame.pack(side='right', fill='x')

        self.f2 = tk.Frame(self.f)
        self.f2.pack( fill='both')

        self.canvas = tk.Canvas(self.f2, width=self.board_width, height=self.board_height, bg='darkgreen')
        self.canvas.pack(side='left', fill =  'x', expand=1)
        self.canvas.bind("<Button-1>", self.board_event_handler)
        self.thescore.set('Score: Big Blue:0, Player:0')
        self.message =""
        self.score =[0,0]
        self.canvas_info_message = ''


    def save_score(self):
        # you can save the score only if you have a valid username and you have already played more than 3 games
        if self.username != "Player" and self.username != "Uplayer" and self.number_of_plays >=3:
            if os.path.isfile(self.database_name):
                with open(self.database_name, 'rb') as fin:
                    reader = pickle.load(fin)
            else:
                reader = []

            with open(self.database_name,'wb') as fin:
                to_save = "BigBlue-{}: {}-{}".format(self.username, self.score[0], self.score[1])
                reader.append(to_save)
                pickle.dump(reader, fin)
            self.button_save_score.configure(state='disabled')

    def info(self):
        # Best scores so far
        temp = []
        show_temp = []
        if os.path.isfile(self.database_name):
            with open(self.database_name, 'rb') as fin:
                reader = pickle.load(fin)
                for i,z in enumerate(reader):
                    if z.count(":") == 1:
                        names = z.split(':')[0].strip()
                        total_score = z.split(':')[1].strip()
                        player_wins = int(total_score.split('-')[1])
                        computer_wins = int(total_score.split('-')[0])
                        total_plays = player_wins + computer_wins
                        percentage = round((player_wins/total_plays)*100, 1)
                        temp.append([names+":", percentage, total_plays, str(computer_wins)+':'+str(player_wins)])
                    else:
                        help = ''
                        for j in range(z.count(":")):
                            if j != 0:
                                help = help + ':' + z.split(":")[j]
                            elif j ==0 and z[0] == ':':
                                help = help + ':' + z.split(":")[j]
                            else:
                                help = help + z.split(":")[j]

                        help = help.strip()
                        total_score = z.split(":")[-1].strip()
                        player_wins = int(total_score.split('-')[1])
                        computer_wins = int(total_score.split('-')[0])
                        total_plays = player_wins + computer_wins
                        percentage = round((player_wins/total_plays)*100, 1)
                        temp.append([help+":", percentage, total_plays, str(computer_wins)+':'+str(player_wins)])

                sorted_temp = sorted(temp, key=lambda x: (x[1], x[2]), reverse = True)

                # present only the 5 best scores of the hallo of fame
                for i,l in enumerate(sorted_temp):
                    if i == 5: break
                    temp1 = [l[0], l[3]]
                    show_temp.append(temp1)

                message = 'Best Scores:\n\n'
                max_len = 0
                for l in show_temp:
                    if len(l[0]) > max_len:
                        max_len = len(l[0])
                for l in show_temp:
                    if len(l[0]) < max_len:
                        message += l[0][:-1] + (max_len - len(l[0]))*" " + ":" + l[1] + '\n'
                    else:
                        message += l[0][:-1] + ":" + l[1] + '\n'

                root_x = self.root.winfo_x()
                root_y = self.root.winfo_y()
                toplevel_w = tk.Toplevel(self.root)
                toplevel_w.title("Hall of Fame")
                toplevel_w.geometry("+%d+%d" % (root_x + 400, root_y+65))
                tk.Label(toplevel_w, text = message,font = self.font_message, background = "lightyellow").pack(side='left', expand=True, fill = "x")
        else:
            message = 'Best Scores:\n\n' + "No saved scores until so far"
            root_x = self.root.winfo_x()
            root_y = self.root.winfo_y()
            toplevel_w = tk.Toplevel(self.root)
            toplevel_w.title("Hall of Fame")
            toplevel_w.geometry("+%d+%d" % (root_x + 400, root_y + 65))
            tk.Label(toplevel_w, text=message, font=self.font_message, background = "lightyellow").pack(side='left', expand=True, fill="x")

    def play_game(self):
        self.number_of_plays +=1
        self.deck = pc.Deck()
        self.deck.shuffle()
        self.computer = ComputerPlayer(self.canvas, self.deck)
        self.human = HumanPlayer(self.canvas, self.deck) #
        self.username = self.human.name
        self.canvas.delete('all')
        self.thescore.set('Score: {}:{}, {}:{}'.format(self.computer.name, self.score[0], self.username, self.score[1]))
        for card in self.deck.content:
            c= GUICard(card, self.canvas)
            c.set_face(False)
            c.move_to(GUI.deck)
        self.run = True
        self.button_new_game.configure(state='disabled')
        self.button_enough.configure(state='normal')
        self.button_save_score.configure(state='disabled')
        self.winner = None
        self.computer.active = True
        self.computer.plays()
        # human to play
        root.update_idletasks()
        if self.computer.score == -1 :
            root.after_idle(self.stop_drawing_cards)
        else:
            root.after_idle(self.human_turn)
    def human_turn(self):
        self.human.active = True

    def board_event_handler(self, event):

        if self.button_new_game['state'] == "normal": return

        if self.computer.active: return
        x = event.x
        y = event.y
        if self.human.active and self.human.score != -1 and self.computer.score != -1:
            if GUI.in_area((x, y), GUI.deck_of_cards_area):
                self.human.plays()

    def find_winner(self):
        max_score = max(self.computer.score, self.human.score)
        if max_score == -1:
            the_winner_is = 'There is no winner in this round!'
            winner = False
        else:
            winner = 'human' if self.human.score == max_score else 'computer'
            if winner == 'human':
                self.score[1] += 1
            else:
                self.score[0] += 1
            self.thescore.set('Score: {}:{}, {}:{}'.format(self.computer.name, self.score[0], self.human.name, self.score[1]))
            the_winner_is = self.human.name if winner=='human' else self.computer.name
            article = '' #''ο' if the_winner_is[-1] in "sς" else 'η'
            the_winner_is = 'The winner is {} {} !!!'.format(article, the_winner_is)
        self.computer.show_cards(all=True)
        self.computer.update_message()
        if self.human.score == 0 and self.computer.score != -1:
            self.human.update_message()
        self.pop_up(the_winner_is)
        self.run = False
        self.winner= None

        if self.number_of_plays >=3 and self.username != "Player" and self.username != "Uplayer":
            self.button_save_score.configure(state='normal')
        self.button_new_game.configure(state='normal')
        self.button_enough.configure(state='disabled')


    def pop_up(self, msg):
        tk.messagebox.showinfo('Result', msg)

    def stop(self):
        self.human.active = False
        self.stop_drawing_cards()
    def stop_drawing_cards(self):
        self.find_winner()
        self.canvas.update_idletasks()

if __name__ == '__main__':
    root = tk.Tk()
    CardImages.generate_card_images()
    app = GUIGame(root)
    root.mainloop()
