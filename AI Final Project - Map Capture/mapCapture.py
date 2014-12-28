
from Tkinter import *
from ttk import Style
import traceback
import math
import random
import tkMessageBox
from copy import  deepcopy


class node:
    '''
    Node represents a region;
    id is the node number; 
    owner is the current owner of the node - either a player number or 0 for unowned; 
    '''
    def __init__(self, id, owner):
        self.id = id
        self.owner = owner
        self.population = 0
        #self.edge_list = []
        self.color = 'white'
        #self.frontier_node = True

    def capture(self, owner, pop):
        self.owner = owner
        self.population += pop
        

    def add_edge(self, adj_node):
        self.edge_list.append(adj_node)

    def pop_update(self, new_pop):
        self.population += new_pop
    
    def population_grow(self):
        self.population += max(random.randint(0,math.ceil(self.population/2)+1), 1)
            

class node_map:

    def __init__(self, size, grid = None):
        self.size = size
        #self.node_list = [] #a list of nodes for easy access
        if grid is not None:
            self.node_grid = deepcopy(grid)
             
        else:
            self.node_grid = [] # an n by y grid representing the node map grid locations using the nodes id
            self.assign_map()

        #----------------------------------Game Scoring Values--------------------------------------------------------#
        self.empty_val = 10
        self.owned_val = 0
        self.enmy_owned_val = 2
        self.battle_win_val = 5
        self.battle_loose_val = -4
    

    def assign_map(self):
        '''Fills in grid with default nodes'''
        n = int(math.ceil(math.sqrt(self.size)))
        self.node_grid = [[node((i,j),0) for j in range(n)] for i in range(n)]

        return n

    def capture_best_neighbor(self, x, y):
        '''Finds the best move for node[x][y] and returns the best neighbor (i,j) and best val'''
        best_move_val = 0
        best_n = None

        for i in range(-1,2):
            for j in range(-1,2):
                if (j is 0 and i is -1) or (j is -1 and i is 0) or (j is 1 and i is 0) or (j is 0 and i is 1): #valid moves are up down left right
                    try:
                        temp_move_val = 0
                        if self.node_grid[i+x][j+y].owner is 0:
                            #then open node
                            temp_move_val = self.empty_val
                        elif self.node_grid[i+x][j+y].owner is self.node_grid[x][y].owner:
                            temp_move_val += self.owned_val
                        else: #battle!!
                            if self.node_grid[i+x][j+y].population >= self.node_grid[x][y].population: # if enemy has more or equal than (x,y)
                                temp_move_val = self.battle_loose_val+(self.node_grid[i+x][j+y].population - self.node_grid[x][y].population) # battle loose value plus the difference between pops
                            else:
                                temp_move_val = self.battle_win_val+(self.node_grid[x][y].population - self.node_grid[x+i][y+j].population)
                    except IndexError:
                        pass
                    if best_move_val < temp_move_val:
                        best_move_val = temp_move_val
                        best_n = (i,j)

        return best_n, best_move_val

    
    def get_capture_val(self, sx,sy,fx,fy):
        '''Returns a value of moving from sx -> sx+fx and sy -> sy+fy'''
        move_val = 0

        if self.node_grid[sx+fx][sy+fy].owner is 0:
            #then open node
            move_val = self.empty_val
        elif self.node_grid[sx+fx][sy+fy].owner is self.node_grid[sx][sy].owner:
            move_val = self.owned_val
        else: #battle!!
            if self.node_grid[sx+fx][sy+fy].population > self.node_grid[sx][sy].population:
                move_val = self.battle_loose_val+(self.node_grid[sx][sy].population - self.node_grid[sx+fx][sy+fy].population)
            else:
                move_val = self.battle_win_val-(self.node_grid[sx+fx][sy+fy].population - self.node_grid[sx][sy].population)

        return move_val



class mapCaptureGame:

    def __init__(self, num_AI = 1, diff = 1, map_size = 2):
        self.human_player = 1
        random.seed()
        self.height = diff + num_AI #max search depth 
        self.AI_players = {i:random.randint(1,self.height) for i in range(2, (2+num_AI))} # generates AI players id's and difficulity starting at 2 to num_AI+2 since range in exclusive end point
        
        self.node_owner_dict = {} # to keep track of what node each player owns - dict with key = player - value is list of nodes or could be a dict with the node id as key and node as value -- there could be a better way though
        
        
        self.map_size = int(2**(num_AI + 2)+1) #min number of players would be 2(HvC) so the smallest map would be 9 squares
        self.map = node_map(self.map_size)


    def generate_game(self):
        #will probably first call the generate_map function of the self.map and then assign players to locations with a min distance between them
        self.nodes_long = self.map.assign_map()

        all_assigned = len(self.AI_players)


        ai_player_id = 2

        if len(self.AI_players) is 1:
            self.map.node_grid[0][0].owner = 1
            self.node_owner_dict[1] = [(0,0)]
            self.map.node_grid[2][2].owner = 2
            self.node_owner_dict[2] = [(2,2)]
        else:
            px = random.randint(0,self.nodes_long-1)
            py = random.randint(0,self.nodes_long-1)
            self.map.node_grid[px][py].owner = 1
            self.node_owner_dict[1] = [(px,py)]

            while all_assigned is not 0:
                allowed = True
                x = random.randint(0,self.nodes_long-1)
                y = random.randint(0,self.nodes_long-1)
                for i in range(-1,2):
                    for j in range(-1, 2):
                        try:
                            if self.map.node_grid[i+x][j+y].owner is not 0:
                                allowed = False
                        except IndexError:
                            pass
                if allowed:
                    self.map.node_grid[x][y].owner = ai_player_id
                    self.node_owner_dict[ai_player_id] = [(x,y)]
                    ai_player_id += 1
                    all_assigned -= 1



        return self.nodes_long

    def population_grow(self, id):
        for owned in self.node_owner_dict[id]:
            self.map.node_grid[owned[0]][owned[1]].population_grow()
    
    def remove_owner(self, lost_node, id, owner_dict = None):
        '''lost_node is tuple pair coordinates of node to be removed from owner ship
           id is owner of node id
           owner_dict is either passed in temp dict for minmax or class level owner dict '''
        if owner_dict is None:
            owner_dict = self.node_owner_dict[id]
        #    for i in range(len(owned_nodes)):
        #        if owned_nodes[i][0] is lost_node[0] and owned_nodes[i][1] is lost_node[1]:
        #            self.node_owner_dict[id].pop(i)
        #            return True
        #else:
        owned_nodes = owner_dict[id]
        for i in range(len(owned_nodes)):
            if owned_nodes[i][0] is lost_node[0] and owned_nodes[i][1] is lost_node[1]:
                owner_dict[id].pop(i)
                return True
            
        return False #<----------------------This shouldn't happen -- if does that means the pass in tuple coordinates aren't owned by the id
    
    def battle_chance(self, a, d):
        '''takes in an attacking pop - a, and a defending pop - d, and simulates battles for a winner. 
           return the new attacking pop and defending pop after the sim-ed battles'''
        a_pop = a
        d_pop = d

        chances = min( a_pop, d_pop)
        while chances > 0 and a_pop > 0 and d_pop > 0:
            total_p = a_pop + d_pop # need to get the total pop
            per = 100/total_p #what percent one pop is
            a_per = a_pop*per
            rolls = [random.randint(0, 100) for i in range(total_p)] #<---------- right now its total pop but may want to change it too a_pop*d_pop for a better guess
            win_c = 0
            lose_c = 0
            for i in range(len(rolls)):
                if rolls[i] <= a_per:
                    win_c += 1
                else:
                    lose_c += 1

            if win_c > lose_c:
                d_pop -=1
            elif lose_c > win_c:
                a_pop -=1
            else:
                a_pop -=1
                d_pop -=1
            chances -= 1

        return (a_pop, d_pop)

    def battle(self, a_node, d_node, a_pop = None, map = None, t_dict = None):
        
        if map is None:
            map = self.map.node_grid
        if a_pop is None:
            a_pop = map[a_node[0]][a_node[1]].population - 1
        if t_dict is None:
            t_dict = self.node_owner_dict

        a_id = map[a_node[0]][a_node[1]].owner
        d_id = map[d_node[0]][d_node[1]].owner

        d_pop = map[d_node[0]][d_node[1]].population

        new_pops = self.battle_chance(a_pop, d_pop)
        a_pop_n = new_pops[0]
        d_pop_n = new_pops[1]

        if d_pop_n > 0:
            #defended against attack
            map[d_node[0]][d_node[1]].population = d_pop_n

            if (map[a_node[0]][a_node[1]].population - a_pop) is 0: #<---shouldnt need but just in case for now
                self.remove_owner(a_node, a_id, t_dict)
                map[a_node[0]][a_node[1]].owner = 0
            else:
                map[a_node[0]][a_node[1]].population = a_pop_n
        elif d_pop_n is 0 and a_pop_n is not 0:
            left_over  = a_pop_n #-d_pop
            map[d_node[0]][d_node[1]].owner = a_id
            self.remove_owner(d_node, d_id, t_dict)
            map[d_node[0]][d_node[1]].population = left_over
            map[a_node[0]][a_node[1]].population -= a_pop
            t_dict[a_id].append(d_node)
        else:
            self.remove_owner(d_node, d_id, t_dict)
            map[d_node[0]][d_node[1]].owner = 0
            map[d_node[0]][d_node[1]].population = 0
            map[a_node[0]][a_node[1]].population -= a_pop
            #dont need to remove owner of attacking node because you always have to leave 1 pop when attacking


    def player_turn(self, s_node, f_node, moving_pop):
        self.current_player = 1
        if self.map.node_grid[f_node[0]][f_node[1]].owner is 0:
            self.map.node_grid[f_node[0]][f_node[1]].capture(1, moving_pop) #capture move node
            self.map.node_grid[s_node[0]][s_node[1]].pop_update(-(moving_pop)) #update pop from start node
            self.node_owner_dict[1].append(f_node)
        elif self.map.node_grid[f_node[0]][f_node[1]].owner is 1:
            #just need to update pops for both places <---------------------------------may want to change to where it just balances the pops so that they are ==
            self.map.node_grid[f_node[0]][f_node[1]].pop_update(moving_pop)
            self.map.node_grid[s_node[0]][s_node[1]].pop_update(-(moving_pop))
        else:
            #battle!
            self.battle(s_node, f_node, moving_pop)

        self.population_grow(1)
        return self.game_win_check()

    def AI_turn(self, AI_id):
        self.alpha = float('-inf')
        self.beta = float('inf')
        self.current_player = AI_id
        if not self.node_owner_dict[AI_id]:
            return
        current_owners = deepcopy(self.node_owner_dict)
        temp_m = node_map(self.map.size, self.map.node_grid)
        best_move_loc, best_move_val, best_move_start = self.expecti_mini_max(temp_m, self.AI_players[AI_id], self.alpha, self.beta, self.current_player, current_owners)

        print "Computer move from:",best_move_start,' with pop ',  self.map.node_grid[best_move_start[0]][best_move_start[1]].population,"--TO: ", best_move_loc, 'with pop ', self.map.node_grid[best_move_loc[0]][best_move_loc[1]].population
        curr_ai_pop = self.map.node_grid[best_move_start[0]][best_move_start[1]].population

        if self.map.node_grid[best_move_loc[0]][best_move_loc[1]].owner is 0:

            self.map.node_grid[best_move_loc[0]][best_move_loc[1]].capture(AI_id, curr_ai_pop-1) #capture move node
            self.map.node_grid[best_move_start[0]][best_move_start[1]].pop_update(-(curr_ai_pop-1)) #update pop from start node
            self.node_owner_dict[AI_id].append(best_move_loc)
        elif self.map.node_grid[best_move_loc[0]][best_move_loc[1]].owner is AI_id:
            #just need to update pops for both places <---------------------------------may want to change to where it just balances the pops so that they are ==
            self.map.node_grid[best_move_loc[0]][best_move_loc[1]].pop_update(curr_ai_pop-1)
            self.map.node_grid[best_move_start[0]][best_move_start[1]].pop_update(-(curr_ai_pop-1))
        else:
            #battle!
            self.battle(best_move_start, best_move_loc, None,self.map.node_grid,self.node_owner_dict)

                
        self.population_grow(AI_id)
        return self.game_win_check()

    def game_win_check(self):
        for k in range(1, len(self.AI_players)+2):
            all_owned = True
            for i in range(self.nodes_long):
                for j in range(self.nodes_long):
                    if self.map.node_grid[i][j].owner is not k or self.map.node_grid[i][j].owner is 0:
                        all_owned = False
                        break
            if all_owned:
                return True, k
        return False, 0

    def expecti_mini_max(self, Node, height, a, b, player, owners_dict):
        if height is 0:
            best_move = None
            best_val = None
            move_node = None
            if owners_dict.get(player) is not None:
                for owned_node in owners_dict[player]:
                    temp_m, temp_v = Node.capture_best_neighbor(owned_node[0],owned_node[1])
                    if best_val < temp_v or best_move is None:
                        best_move = temp_m
                        best_val = temp_v
                        move_node = owned_node

            #if player is self.current_player:
            #    return best_move, best_val, move_node
            #else:
            return best_move, best_val, move_node
        else:
            
            best_move_final = None #move to node - finish
            best_val_final = None
            move_node_final = None #move from node - start
            for owned_node in owners_dict[player]:
                #temp_m, temp_v = self.map.capture_best_neighbor(owned_node[0],owned_node[1])
                curr_pop = Node.node_grid[owned_node[0]][owned_node[1]].population
                try:
                    for i in range(-1,2):
                        for j in range(-1,2):
                            if (j is 0 and i is -1) or (j is -1 and i is 0) or (j is 1 and i is 0) or (j is 0 and i is 1): #valid moves are up down left right
                                #not really sure what best to do here either go all the way to the child and then bound back up or take move val first then make moves?
                                if  Node.node_grid[i+owned_node[0]][j+owned_node[1]].owner is player  or (i+owned_node[0]) < 0 or (j+owned_node[1]) < 0:
                                    continue
                                curr_move_val = Node.get_capture_val(owned_node[0], owned_node[1], i, j)

                                if  Node.node_grid[owned_node[0]][owned_node[1]].owner is not player:
                                    continue

                                if Node.node_grid[i+owned_node[0]][j+owned_node[1]].owner is 0:

                                    new_map = node_map(Node.size, Node.node_grid)                                           #creating a new child temp map based off of passed in Node param
                                    new_map.node_grid[i+owned_node[0]][j+owned_node[1]].capture(player, curr_pop-1)         #updating child map with a capture of the possible move
                                    new_map.node_grid[owned_node[0]][owned_node[1]].pop_update(-(curr_pop-1))          #adjusting population is original location
                                    new_owners = deepcopy(owners_dict)                                                   #creating a new owners dict from copy of the current owners dict to not corrupt the original
                                    new_owners[player].append((i+owned_node[0], j+owned_node[1]))                           #updating new owners dict with new owned tile
                                    
                                else:#battle!
                                    fo = False
                                    for t in owners_dict[Node.node_grid[i+owned_node[0]][j+owned_node[1]].owner]:
                                        if t == Node.node_grid[i+owned_node[0]][j+owned_node[1]].id:
                                            fo=True
                                    if not fo:
                                        break
                                    new_map = node_map(Node.size, Node.node_grid)
                                    new_owners = deepcopy(owners_dict)  
                                    self.battle(owned_node, (owned_node[0]+i, owned_node[1]+j), None, new_map.node_grid, new_owners)

                                next_player = (player+1)%(2+len(self.AI_players))
                                if next_player is 0:
                                    next_player += 1

                                child_best_temp, child_val_temp, child_start_temp = self.expecti_mini_max(new_map, height-1, a,b, next_player, new_owners)

                                if child_val_temp is None:
                                    child_val = 0
                                    
                                if player is self.current_player: #then maximizing so pick highest val move
                                    
                                    if a is float('-inf') or (curr_move_val + child_val_temp) >= a:
                                        a = child_val_temp
                                        best_move_final = (i+owned_node[0],j+owned_node[1])
                                        move_node_final = owned_node #<----------------------------may need to create new tuple if owned_node is lost by garbage 
                                    if b <= a:
                                        return best_move_final, a, move_node_final
                                else: #then minimizing so pick lowest val move
                                    if b is float('inf') or (child_val_temp) <= b:
                                        b = child_val_temp
                                        best_move_final = (i+owned_node[0],j+owned_node[1])
                                        move_node_final = owned_node
                                    if b <= a:
                                        return best_move_final, b, move_node_final
                except IndexError, e:
                    pass
                    #print traceback.format_exc()
                    #print e
            if player is self.current_player:
                return best_move_final, a, move_node_final
            else:
                return best_move_final, b, move_node_final
            #return best_move_final, best_val_final, move_node_final #need to return all three for recurision but dont need for final return



class newButton(Button):
    def __init__(self, master=None, n = None ,*args,**options):
        self.node = n
        Button.__init__(self, master, *args, **options)



class captureGame_gui:

    def __init__(self):
        self.root = Tk()
        #self.root.geometry("350x300+300+300")
        self.root.resizable(width = False, height = False)
        
        self.win_x_size = 600 #window width
        self.win_y_size = 800 #window height

        self.main_window = Frame(self.root, width=self.win_x_size, height=self.win_y_size)
        
        self.main_window.pack()

        self.game_menu_init()

        self.root.mainloop()
       
    def game_menu_init(self):

        self.main_window.style = Style()
        self.main_window.style.theme_use("default")
        self.main_window.pack(fill=BOTH, expand=1)

        '''self.columnconfigure(1, weight=1)
        self.columnconfigure(3, pad=7)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(5, pad=7)'''
        
        self.lbl_name = Label(self.main_window, text="Player Name: ")
        self.lbl_name.grid(sticky=W, pady=2, padx=3)
        
        self.name_entry = Entry(self.main_window)
        self.name_entry.grid(row=0, column=1, columnspan=2, rowspan=2, 
            padx=5, sticky=E+W+S+N)

        
        self.lbl_AI_players = Label(self.main_window, text="Number of Enemies")
        self.lbl_AI_players.grid(sticky=W, row=2, pady=2, padx=3)
        
        self.AI_var = StringVar()
        self.AI_var.set("1")
        self.mn_AI = OptionMenu(self.main_window, self.AI_var, '1','2','3')
        self.mn_AI.grid(row=2, column=1)

        self.diff_var = StringVar()
        self.diff_var.set("1")
        self.lbl_diff = Label(self.main_window, text="Difficulty")
        self.lbl_diff.grid(sticky=W, row=3, pady=2, padx=3)
        self.mn_dff = OptionMenu(self.main_window, self.diff_var, '1','2')
        self.mn_dff.grid(row=3, column=1)

        self.btn_start = Button(self.main_window, text="Start")
        self.btn_start.bind("<Button-1>", self.init_game)
        self.btn_start.grid(sticky=S, row=4, column=1)

    def init_game(self, event):
        '''removes all game menu items and inits the board'''

         #-----------------Cleaning up game window---------------------------------------------#
        self.player_1_name = self.name_entry["text"]
        self.name_entry.grid_forget()
        self.lbl_name.grid_forget()

        self.AI_Players_num = int(self.AI_var.get())
        self.lbl_AI_players.grid_forget()
        self.mn_AI.grid_forget()

        self.game_diff = int(self.diff_var.get())
        
        self.lbl_diff.grid_forget()
        self.mn_dff.grid_forget()

        self.btn_start.grid_forget()

        #-----------------Setting up game stuff---------------------------------------------#

        self.game = mapCaptureGame(int(self.AI_Players_num), int(self.game_diff))

        self.nodes_long = self.game.generate_game() #generate game return n of the nXn board

        self.button_width  = int((math.floor(self.win_x_size/self.nodes_long))/10)
        self.button_height = int((math.floor(self.win_y_size/self.nodes_long))/30)

        #print self.button_width
        #print self.button_height

        self.pop_grid = [[StringVar() for j in range(self.nodes_long)] for i in range(self.nodes_long)] #grid to store StringVars for game board to update test

        self.game_board = [[newButton(self.main_window, self.game.map.node_grid[i][j], width = self.button_width, height=self.button_height, textvariable=self.pop_grid[i][j]) for j in range(self.nodes_long)] for i in range(self.nodes_long)]
        #---------------------Drawing board---------------------------------------------#
        self.colors = ['dim gray', 'violet red', 'yellow', 'red', 'blue', 'green', 'orange', 'pink', 'green', 'brown']
        self.color_dict = {} #to easily reference the players colors

        self.turn_str_var = StringVar()
        
        self.lbl_turn = Label(self.main_window, textvariable = self.turn_str_var)
        self.turn_str_var.set("Generating Board")
        self.lbl_turn.grid(row=0, column = (int(self.nodes_long/2)))

        for i in range(self.nodes_long):
            for j in range(self.nodes_long):
                self.game_board[i][j].bind("<Button-1>",self.map_click)
                
                if self.game_board[i][j].node.owner is not 0:
                    chosen = self.color_pick()
                    self.game_board[i][j].node.color = chosen
                    self.game_board[i][j]['bg'] = chosen
                    self.color_dict[self.game_board[i][j].node.owner] = chosen
                    self.game_board[i][j].node.population = 5
                else:
                    self.game_board[i][j]['bg'] = 'white'
                self.pop_grid[i][j].set(self.game_board[i][j].node.population)
                self.game_board[i][j].grid(row = i+1, column=j) 

        
        #----------------Setting rules---------------------------------------#
        self.win = False #winner trigger
        self.turn = True #turn trigger
        self.winning_player = 0
        self.button_counter = 0
        self.clicked_buttons = []

        first = random.randint(1,self.AI_Players_num+1)

        if first is 1: #player goes first
            self.turn = False
            self.player_turn_string_set()
        else:
            self.ai_turn_string_set(2)

        self.root.after(100, self.main_game_loop)

    def main_game_loop(self):
        if self.win:
            self.win = False
            self.lbl_turn["text"] = "Player %i Wins!" % self.winning_player
            self.game_end()
            return

        elif self.turn:
            self.root.update_idletasks()
            self.computer_turn()
            self.turn = False
        self.root.after(100, self.main_game_loop)

        
    def computer_turn(self):
        #move_list = {}

        for i in range(2,self.AI_Players_num+2): #<-------------------could overflow
            self.ai_turn_string_set(i)
            self.root.update_idletasks()
            win, p = self.game.AI_turn(i)
            self.root.update_idletasks()
            if win:
                self.win = True
                self.winning_player = p
                break
            self.gameboard_update()
        self.player_turn_string_set()

    def player_turn_string_set(self):
        self.turn_str_var.set("Player's Turn")
        self.lbl_turn['fg'] = self.color_dict[1]

    def ai_turn_string_set(self, id):
        self.turn_str_var.set("AI Player %i Turn" %id)
        self.lbl_turn['fg'] = self.color_dict[id]

    def color_pick(self):
        
        x = random.randint(0, len(self.colors)-1)
        try:
            c = self.colors.pop(x)
            return c #chosen
        except:
            l = len(self.colors)
            print x
    
    def gameboard_update(self):
        for i in range(self.nodes_long):
            self.root.update_idletasks()
            for j in range(self.nodes_long):
                if self.game_board[i][j].node.owner is 0:
                    self.game_board[i][j]['bg'] = 'white'
                else:
                    self.game_board[i][j]['bg'] = self.color_dict[self.game_board[i][j].node.owner]
                self.pop_grid[i][j].set(self.game_board[i][j].node.population)

    def map_click(self,event):
        #print event.widget.node.owner,' -- ', event.widget.node.id
        self.root.update_idletasks()
        if not self.turn:
            if self.button_counter % 2 is 0: #first button clicked
                if event.widget.node.owner is 1:
                    self.clicked_buttons.append(event.widget.node)
                    self.button_counter += 1
            else:
                #second button clicked
                self.clicked_buttons.append(event.widget.node)
                self.pop_ask_win =Frame()
                self.pop_ask_win.pack()
            
                self.lbl_num_pop = Label(self.pop_ask_win, text="Population to Move")
                self.lbl_num_pop.grid(row=1, column = 1)
        

                pop_options = [str(i) for i in range(0, self.clicked_buttons[0].population)]
                self.pop_var = StringVar()
                self.pop_var.set(pop_options[0])
                self.mn_AI = apply(OptionMenu, (self.pop_ask_win, self.pop_var) + tuple(pop_options))
                self.mn_AI.grid(row=2, column=1)
            
                self.pop_butt_ok = Button(self.pop_ask_win, text='Ok')
                self.pop_butt_ok.bind("<Button-1>", self.pop_select)
                self.pop_butt_ok.grid(row = 3, column=0)

                self.pop_butt_cancel = Button(self.pop_ask_win, text='Cancel')
                self.pop_butt_cancel.bind("<Button-1>", self.pop_select)
                self.pop_butt_cancel.grid(row = 3, column = 2)
                self.button_counter = 0

    def pop_select(self, event):
        if event.widget is self.pop_butt_cancel:
            self.clicked_buttons = []
            
        else:
            move_pop = self.pop_var.get()

            win, p = self.game.player_turn(self.clicked_buttons[0].id, self.clicked_buttons[1].id, int(move_pop))
            if win:
                self.win = True
                self.winning_player = p
            self.clicked_buttons = []
            

            self.gameboard_update()
            self.turn = True
            self.root.after(100, self.main_game_loop)
        self.pop_ask_win.destroy()
        self.root.update_idletasks()
        self.root.after(100, self.main_game_loop)

    def hide_game_board(self):
        for i in range(self.nodes_long):
            for j in range(self.nodes_long):
                self.game_board[i][j].grid_forget()


    def game_end(self):
        ans = tkMessageBox.askyesno("Replay", "Would you like to play again?")
        if ans:
            self.hide_game_board()
            self.game_menu_init()
            #replay
        else:
            #self.main_window.destroy()
            self.root.destroy()


if __name__=='__main__':
    test = captureGame_gui()
