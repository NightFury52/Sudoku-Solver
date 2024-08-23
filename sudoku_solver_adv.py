from threading import Thread
import customtkinter as ctk
from random import shuffle
# from time import sleep

class Sudoku(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color = 'white')
        
        # Display Params
        self.title('Sudoku Solver Advance')
        self.geometry('510x602')
        self._set_appearance_mode('light')
        self.resizable(False, False)
        
        # Sudoku Params
        self.sudoku_dict = {}
        self.running = False # bool to check whether the algorithm is running     
        
        # Setup
        self.indicator_label = ctk.CTkLabel(self, text = '', fg_color = 'yellow',
                                            width = 500, corner_radius = 4)
        self.indicator_label.pack()
        self.initiate_sudoku()
        self.sudoku_frame = Sudoku_Frame(self)
        self.create_functioning_buttons()
        
        # Run
        self.mainloop()

    def create_functioning_buttons(self):
        # Create Start, Clear Buttons
        self.start_button = ctk.CTkButton(self, text = 'Start', width = 50, command = self.start)
        self.clear_button = ctk.CTkButton(self, text = 'Clear', width = 50, command = self.clear)
        
        self.start_button.pack()
        self.clear_button.pack()

    def initiate_sudoku(self):
        for row in range(1, 10):
            self.sudoku_dict[row] = {}
            
            for col in range(1, 10):
                # Numbers are stored in StringVar
                self.sudoku_dict[row][col] = ctk.StringVar(self, '')
                self.sudoku_dict[row][col].trace('w', lambda name, index, mode:
                    self.entry_validate(name, index, mode))

    def entry_validate(self, name, index, mode):
        row = None
        col = None
        
        # Name refers to the name of the tkinter variable for which callback is called
        for row in range(1, 10):
            
            for col in range(1, 10):
                
                if str(self.sudoku_dict[row][col]) == name:
                    # Disable the entry widget
                    self.sudoku_frame.entry_dict[row][col].configure(state = 'disabled')
                    
                    # String variable concerned
                    var = self.sudoku_dict[row][col]
                    
                    word = var.get()
                    # print(f'Before: ({row},{col}) {word}')
                    
                    # Prepare the number
                    if len(word) == 1:
                        if (ord(word) < 49) or (ord(word) > 57):
                            word = ''
                    if len(word) > 1:
                        word = word[0]
                    
                    # Set the Number
                    var.set(word)
                    # print(f'After: ({row},{col}) {word}')
                    
                    # Change color of Entry Widget
                    if word:
                        if self.running:
                            self.sudoku_frame.entry_dict[row][col].configure(fg_color = 'green')
                        else:
                            self.sudoku_frame.entry_dict[row][col].configure(fg_color = 'orange')
                    else:
                        self.sudoku_frame.entry_dict[row][col].configure(fg_color = 'white')
                    
                    # Set the entry widget to normal mode
                    self.sudoku_frame.entry_dict[row][col].configure(state = 'normal')
                    
                    break

    def start(self):
        self.running = True
        self.level = 0
        algo_thread = Thread(target = self.run_algo)
        algo_thread.start()

    def clear(self):
        self.running = False
        for row in range(1, 10):
            for col in range(1, 10):
                self.sudoku_dict[row][col].set('')
                self.sudoku_frame.entry_dict[row][col].configure(fg_color = 'white')

    def run_algo(self):
        self.level += 1
        level = self.level
        flag, pos_updated = self.run_exact_method()
        # print(f'Creation, Level: {level}, filling: {pos_updated}')
        
        min_row = None
        min_col = None
        
        if flag:
            return True
        else:
            solution_dict = self.form_solution_set_dict()
            min_row, min_col = self.min_row_col_of_dict(solution_dict)
            
            if min_row:
                for number in solution_dict[min_row][min_col]:
                    self.indicator_label.configure(fg_color = 'red')
                    self.sudoku_dict[min_row][min_col].set(number)
                    # sleep(1)
                    if self.run_algo():
                        return True                        
        
        # clear the mess you've made
        # print(f'Deletion, Level: {level}, clearing: {pos_updated}')
        self.indicator_label.configure(fg_color = 'black')
        if min_row:
            self.sudoku_dict[min_row][min_col].set('')
        for row, col in pos_updated:
            # sleep(1)
            self.sudoku_dict[row][col].set('')
        
        return False

    def min_row_col_of_dict(self, solution_dict):
        min_len = 9
        min_row = None
        min_col = None
        
        for row in range(1, 10):
            for col in range(1, 10):
                length = len(solution_dict[row][col])
                if (length != 0) and (length <= min_len):
                    min_len = length
                    min_row = row
                    min_col = col
                    
        return min_row, min_col

    def run_exact_method(self):
        flag = True
        pos_updated = [] # list of positions it has updated
        while self.not_solved() and flag:
            # sleep(1)
            solution_dict = self.form_solution_set_dict()
            
            flag = False
            for row in range(1, 10):
                flag = False
                for col in range(1, 10):
                    if self.sudoku_dict[row][col].get() == '':
                        flag = self.search_solution(row, col, solution_dict)
                    if flag:
                        self.indicator_label.configure(fg_color = 'green')
                        pos_updated.append((row, col))
                        break
                
                if flag:
                    break
        
        if self.not_solved():
            flag = False # setting flag to False if Sudoku hasn't been solved yet
        
        return flag, pos_updated # True if exact method has passed, False otherwise

    def not_solved(self):
        # Checks if sudoku's not solved, returns True
        flag = False
        for row in range(1, 10):
            for col in range(1, 10):
                if self.sudoku_dict[row][col].get() == '':
                    flag = True
                    break
            if flag == True:
                break
        
        return flag # True if not solved

    def form_solution_set_dict(self):
        solution_dict = {}
        for row in range(1, 10):
            solution_dict[row] = {}
            
            for col in range(1, 10):
                solution_dict[row][col] = []
                if self.sudoku_dict[row][col].get() == '':
                    solution_dict[row][col] = [f'{i}' for i in range(1, 10)]
                    # row-wise
                    for i in range(1, 10):
                        number = self.sudoku_dict[row][i].get()
                        if number and (number in solution_dict[row][col]):
                            solution_dict[row][col].remove(number)
                    
                    # column-wise
                    for i in range(1, 10):
                        number = self.sudoku_dict[i][col].get()
                        if number and (number in solution_dict[row][col]):
                            solution_dict[row][col].remove(number)
                    
                    # box-wise
                    row_idx = int((row+(-row%3))/3) - 1
                    col_idx = int((col+(-col%3))/3) - 1

                    for i in range(3*row_idx+1, 3*row_idx+4):
                        for j in range(3*col_idx+1, 3*col_idx+4):
                            number = self.sudoku_dict[i][j].get() 
                            if number and (number in solution_dict[row][col]):
                                solution_dict[row][col].remove(number)
                            
                    solution_dict[row][col] = list(set(solution_dict[row][col]))
                
        return solution_dict

    def search_solution(self, row, col, solution_dict):
        flag = False
        
        if len(solution_dict[row][col]) == 1:
            flag = True
            self.sudoku_dict[row][col].set(solution_dict[row][col][0])
        
        else:
            for number in solution_dict[row][col]:
                flag = True
                for i in range(1, 10):
                    if (i != col) and (number in solution_dict[row][i]):
                        flag = False
                        break
                
                if not flag:
                    flag = True
                    for i in range(1, 10):
                        if (i != row) and (number in solution_dict[i][col]):
                            flag = False
                            break
                
                if not flag:
                    row_idx = int((row+(-row%3))/3) - 1
                    col_idx = int((col+(-col%3))/3) - 1

                    for i in range(3*row_idx+1, 3*row_idx+4):
                        for j in range(3*col_idx+1, 3*col_idx+4):
                            if not((i == row) and (j == col)) and (number in solution_dict[i][j]):
                                flag = False
                                break
                
                if flag:
                    self.sudoku_dict[row][col].set(number)
                    break
        
        return flag # True if some place has been filled, False otherwise

    def sudoku_validity(self, row, col):
        valid = True
        
        # Check for the row
        number_list =[]
        for i in range(1, 10):
            number = self.sudoku_dict[row][i].get()
            if number:
                if number in number_list:
                    valid = False
                    break
                else:
                    number_list.append(number)

        # Check for the column
        if valid:
            number_list =[]
            for i in range(1, 10):
                number = self.sudoku_dict[i][col].get()
                if number:
                    if number in number_list:
                        valid = False
                        break
                    else:
                        number_list.append(number)

        # Check for each box
        if valid:
            row_idx = int((row+(-row%3))/3) - 1
            col_idx = int((col+(-col%3))/3) - 1
            number_list = []
            for i in range(3*row_idx+1, 3*row_idx+4):
                for j in range(3*col_idx+1, 3*col_idx+4):
                    number = self.sudoku_dict[i][j].get()
                    if number:
                        if number in number_list:
                            valid = False
                            break
                        else:
                            number_list.append(number)
        
        return valid


# Main Frame of the Sudoku
class Sudoku_Frame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(master = parent, height = 500,
                         width = 500, fg_color = 'black',
                         bg_color = 'white', corner_radius = 4)
        self.pack_propagate(0)
        self.grid_propagate(0)
        
        self.create_grid()
        self.entry_dict = self.create_entry(parent)
        
        # packing the widget here
        self.pack()

    def create_grid(self):
        # Creating the grids
        
        for row in range(13):
            if row%4 == 0:
                self.rowconfigure(row, weight = 1, uniform = 'a')
            else:
                self.rowconfigure(row, weight = 10, uniform = 'a')
        
        for col in range(13):
            if col%4 == 0:
                self.columnconfigure(col, weight = 1, uniform = 'a')
            else:
                self.columnconfigure(col, weight = 10, uniform = 'a')

    def create_entry(self, parent):
        # Creating the entry widgets for Sudoku
        entry_dict = {}
        
        for row in range(1, 10):
            entry_dict[row] = {}
            
            for col in range(1, 10):
                entry = ctk.CTkEntry(self, textvariable = parent.sudoku_dict[row][col],
                                     corner_radius = 4, font = ctk.CTkFont(size = 35),
                                     justify ='center', fg_color = 'white',
                                     text_color = 'black')
                entry.grid(row = int((row+(-row%3))/3) + row - 1,
                           column = int((col+(-col%3))/3) + col - 1,
                           sticky = 'nsew', padx = 1, pady = 1)
                entry_dict[row][col] = entry
                
        return entry_dict


if __name__ == '__main__':
    Sudoku()