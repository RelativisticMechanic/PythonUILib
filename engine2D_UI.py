import engine2D
import os

# PictureBox
# Displays a picture 
class PictureBox(engine2D.Object):
    def __init__(self, filename, x, y, w, h):
        super().__init__()
        self.SetImage(filename, x, y, w, h)
    
    def SetImage(self, filename, x, y, w, h):
        self.image = engine2D.Image(filename, w, h)
        self.x = x
        self.y = y

    def Draw(self, elapsed):
        engine2D.DrawImage(self.image, self.x, self.y)

# Label element
# Displays a label
class Label(engine2D.Object):
    def __init__(self, caption, x, y, font):
        super().__init__()
        self.x = x
        self.y = y
        self.caption = caption
        self.font = font
    
    def SetCaption(self, caption):
        self.caption = caption
    
    def Draw(self, elapsed):
        self.font.PutString(self.caption, self.x, self.y)
    
# Progress bar
# Displays a progress bar
class ProgressBar(engine2D.Object):
    def __init__(self, x, y, w, h, font=None):
        super().__init__()
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.font = font
        self.progress = 0
    
    def SetProgress(self, p):
        if(p > 100):
            p = 100
        self.progress = p
    
    def Draw(self, elapsed):
        engine2D.DrawBlock(self.x, self.y, self.w, self.h, 255, 255, 255, True)
        engine2D.DrawBlock(self.x + 2, self.y + 2, (self.w - 4) * (self.progress/100.0), self.h - 4, 40, 140, 40, True)
        if(self.font):
            progress_string = str(int(self.progress)) + "%"
            self.font.PutString(progress_string, self.x + (self.w) * 0.5 - self.font.ch_w * len(progress_string) * 0.5, self.y + 2)
        


# Simple dialogbox that displays a message
# CallBack must be a Bool -> Always returns true since this is an OK box.

# def ok_callback(id, result):
#   pass

# id is the object id of the calling dialogbox
# result is a bool (True if OK, False if Cancel)
# DialogBoxOK only returns True.

class DialogBoxOK(engine2D.Object):
    def __init__(self, message, x, y, back_color, font, callback = None):
        super().__init__()
        self.callback = callback
        self.message = message
        self.font = font
        self.back_color = back_color
        self.x = x
        self.y = y
        # Ideally, dialog boxes are 0.6 of the screen width
        self.w = (0.6 * engine2D.GetWidth())
        # And 0.2 the height
        self.h = (0.2 * engine2D.GetHeight())
        self.button_w = int(0.25 * self.w)
        self.button_h = self.font.ch_h + 2
        # calculate maximum characters per line
        # leave some space for padding on left and right
        self.max_chars_per_line = int((self.w - 2 * self.font.ch_w) / self.font.ch_w)

        # Leave 3 lines out, one top padding, one bottom padding and one for the buttons line
        self.max_lines = int((self.h - 3 * self.font.ch_h) / self.font.ch_h)

        # Break down the message into lines
        self.message_lines = [ self.message[k - self.max_chars_per_line:k] for k in range(self.max_chars_per_line, len(self.message) + self.max_chars_per_line, self.max_chars_per_line)]
        self.message_lines = self.message_lines[:self.max_lines]

    def OnKeyPress(self, elapsed, key):
        if(key == engine2D.Button.RETURN):
            if(self.callback):
                self.callback(self.id, True)
            
            self.Delete()

    def DrawBox(self):
        engine2D.DrawBlock(self.x, self.y, self.w, self.h, self.back_color[0], self.back_color[1], self.back_color[2], True)
        engine2D.DrawBlock(self.x + 2, self.y + 2, self.w - 4, self.h - 4, 255, 255, 255)
        engine2D.DrawBlock(self.x, self.y, self.w, self.h, 255, 255, 255)

    def DrawMessage(self):
        for i in range(0, len(self.message_lines)):
            self.font.PutString(self.message_lines[i], self.x + self.font.ch_w, self.y + self.font.ch_h + i * self.font.ch_h)

    def DrawButtons(self):
        engine2D.DrawBlock(self.x + self.w * 0.5 - self.button_w * 0.5, self.y + self.h - self.font.ch_h - self.button_h, self.button_w, self.button_h, 255, 0, 0, True)
        self.font.PutString("OK", self.x + self.w * 0.5 - self.font.ch_w, self.y + self.h - self.font.ch_h - self.button_h)

    def Draw(self, elapsed):
        self.DrawBox()
        self.DrawMessage()
        self.DrawButtons()
        
# A dialog box that supports OK and Cancel
# Callback must be a function that takes bool
# OK - True, Cancel - False
class DialogBoxOKCancel(DialogBoxOK):
    def __init__(self, message, x, y, font, back_color, callback = None):
        super().__init__(message, x, y, back_color, font)
        self.callback = callback
        self.selected = True

    def OnKeyPress(self, elapsed, key):
        if(key == engine2D.Button.LEFT or key == engine2D.Button.RIGHT):
            self.selected = not self.selected
        elif(key == engine2D.Button.RETURN):
            if(self.callback):
                self.callback(self.id, self.selected)
            self.Delete()

    def DrawButtons(self):
        ok_color = ()
        cancel_color = ()
        if(self.selected):
            ok_color = (255, 0, 0)
            cancel_color = (40, 40, 40)
        else:
            ok_color = (40,40,40)
            cancel_color = (255, 0, 0)
        
        engine2D.DrawBlock(self.x + self.w * 0.25 - self.button_w * 0.5, self.y + self.h - self.font.ch_h - self.button_h, self.button_w, self.button_h, ok_color[0], ok_color[1], ok_color[2], True)
        engine2D.DrawBlock(self.x + self.w * 0.75 - self.button_w * 0.5, self.y + self.h - self.font.ch_h - self.button_h, self.button_w, self.button_h, cancel_color[0], cancel_color[1], cancel_color[2], True)
        self.font.PutString("OK", self.x + self.w * 0.25 - self.font.ch_w, self.y + self.h - self.font.ch_h - self.button_h)
        self.font.PutString("Cancel", self.x + self.w * 0.75 - self.button_w * 0.5, self.y + self.h - self.font.ch_h - self.button_h)


# Inernal class
class _ListBox_Choice:
    def __init__(self, choice_str, max_chars_per_line, id):
        self.choice_lines = [ choice_str[x - max_chars_per_line: x] for x in range(max_chars_per_line, len(choice_str)+max_chars_per_line, max_chars_per_line)]
        self.n_lines = len(self.choice_lines)
        self.id = id

# Listbox - display a list to the user
# choices - Array of strings with the choices to be listed on the listbox
# input_callback - A function that takes two integers as input
# x,y,w,h - X, Y, W, H of the listbox
# back_color - background colour of the listbox
# select_color - select colour of the listbox

# def input_callback(id, type, choice_index):
#   pass
# Here id is the id of the listbox
# type is the type of output (CHOICE_CHOSEN) or (CHOICE_SELECT) -- Choice chosen is called when RETURN is pressed, CHOICE_SELECT is called when
# the user selects a choice.
# CHOICE_SELECT is also called at start, representing choice 0.
# choice_index is the index of the choice chosen by user in the array passed

class ListBox(engine2D.Object):
    CHOICE_SELECT = 0
    CHOICE_CHOSEN = 1

    def __init__(self, choices, input_callback, x, y, w, h, font, back_color=(0,0,0), select_color=(40, 110, 40), choice_change_callback=0):
        super().__init__()
        self.callback = input_callback
        self.font = font
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.font = font
        self.back_color = back_color
        self.select_color = select_color

        self.max_lines = int(self.h / self.font.ch_h)
        self.max_chars_per_line = int(self.w / self.font.ch_w)

        self.BuildChoiceBlocks(choices)
    
    def BuildChoiceBlocks(self, choices):
        self.choices = []
        for idx, choice_str in enumerate(choices):
            self.choices.append(_ListBox_Choice(choice_str, self.max_chars_per_line, idx))
        
        # Create choice "blocks" - blocks of choices which can be displayed at once on the screen
        # This is because our 'choices' may be too long to put in one go.
        # So we calculate how much line each choice takes,
        # And then group choices into groups that hold maximum lines that can be displayed on the screen
        # So if the user scrolls down past the last choice on screen, we simply switch to the next choice block
        i = 0
        n_lines = 0
        self.choice_blocks = [[]]

        # Here we create a dictionary to allow for quick access to choice blocks
        # directly through the choice indices

        # For example if index 4 belongs to choice block 1, then self.choice_blocks_dict["4"] = 1
        self.choice_blocks_dict = {}
        
        for choice in self.choices:
            n_lines += choice.n_lines
            # Check if we exceeded the capacity of the maxlines on screen
            if(n_lines >= self.max_lines):
                # Don't forget that we're still adding the current file, even if we ran out of
                # space! 
                n_lines = choice.n_lines
                # If we ran out of space, we won't print this file on this choice block
                # and move on to the next
                self.choice_blocks.append([])
                # BUG: There is a possibility that the file name won't fit on the entire choice block at all,
                # the program would simply be stuck in an infinite loop and would keep incrementing i. 
                i += 1
            
            self.choice_blocks[i].append(choice.id)
            self.choice_blocks_dict[choice.id] = i
        
        self.current_choice = 0
    
    def ProcessChoice(self, input_type):
        # Give the callback the choice taken
        if(self.callback):
            self.callback(self.id, input_type, self.current_choice)
            if(input_type == self.CHOICE_CHOSEN):
                self.Delete()
        
    def OnKeyPress(self, elapsed, key):
        if(key == engine2D.Button.UP):
            self.current_choice -= 1
            if(self.current_choice < 0): self.current_choice = 0
        if(key == engine2D.Button.DOWN):
            self.current_choice += 1
            if(self.current_choice >= len(self.choices)): self.current_choice = len(self.choices) - 1
        if(key == engine2D.Button.RETURN):
            self.ProcessChoice(self.CHOICE_CHOSEN)
        if(key == engine2D.Button.UP or engine2D.Button.DOWN):
            self.ProcessChoice(self.CHOICE_SELECT)
    
    def Draw(self, elapsed):
        # Draw the outer of the listbox
        engine2D.DrawBlock(self.x, self.y, self.w, self.h, self.back_color[0], self.back_color[1], self.back_color[2], True)
        engine2D.DrawBlock(self.x-1, self.y-1, self.w+1, self.h+1, 255, 255, 255)

        # Current_Line variable to keep track of where we are at relative to (self.x, self.y)
        current_line = 0

        # Figure out where we are, i.e. which choice block to print
        choice_block_idx =  self.choice_blocks_dict[self.current_choice]
        current_choice_block = self.choice_blocks[choice_block_idx]

        # If there is a choice block above, print a scroll up sign, that is we are at a choice
        # block that is not the first block.
        if(choice_block_idx > 0):
            self.font.PutString("^", self.x + self.w * 0.5 - self.font.ch_w, self.y - self.font.ch_h)
        # If there are choice blocks belows, print a scroll down sign
        if(choice_block_idx < len(self.choice_blocks) - 1):
            self.font.PutString("v", self.x + self.w * 0.5 - self.font.ch_w, self.y + self.h)
        
        for k in current_choice_block:
            choice = self.choices[k]
            # If we ran out of lines to print, leave
            if(current_line >= self.max_lines):
                break
            # Split the lines to contain the maximum of self.max_chars_per_line
            # Now iterate through the split lines and print them one by one
            for idx, line in enumerate(choice.choice_lines):
                # Are we a file list box? If so check if the current choice is a directory and add a '->' as well
                # to tell the user that it is indeed a directory
                if(idx == 0 and type(self) == FileListBox):
                    if(os.path.isdir(self.current_directory + ''.join(choice.choice_lines))):
                        line = "-> " + line

                # If we are drawing the current choice, make sure to draw a redbox around it (to denote selection)
                if(choice.id == self.current_choice):
                    # if its the first line of the selected choice, print an arrow as well
                    if(idx == 0): 
                        self.font.PutString(">", self.x - self.font.ch_w, self.y + (current_line) * self.font.ch_h)
                    engine2D.DrawBlock(self.x + 1, self.y + (current_line) * self.font.ch_h, self.w - 1, self.font.ch_h, self.select_color[0], self.select_color[1], self.select_color[2], True)
                self.font.PutString(line, self.x, self.y + (current_line) * self.font.ch_h)
                current_line += 1

# FileListBox
# root - highest directory in the hierarchy
# input_callback - takes string argument, called when user selects a file, argument is a string containing the file
# x, y - screen location where the file list must be shown
# w, h - width and height of the list box
# font - font to be used for the file-lising
# back_color - back_color of the file list box
# select_color - select color of the file list box
class FileListBox(ListBox):

    def __init__(self, root, input_callback, x, y, w, h, font, back_color=(0,0,0), select_color=(40, 110, 52)):

        # First get a list of files from the root directory
        if(not root[-1] == '\\'):
            root += '\\'
        
        self.root = root
        self.current_directory = root
            
        self.current_file_list = os.listdir(self.current_directory)
        super().__init__(self.current_file_list, input_callback, x, y, w, h, font, back_color, select_color)
    
    def ProcessChoice(self, input_type):
        file_choice = self.current_file_list[self.current_choice]

        # Check if choice is a file or a folder
        if((os.path.isdir(self.current_directory + file_choice) or file_choice == "..") and input_type == self.CHOICE_CHOSEN):
            if(file_choice == ".."):
                # This is the previous directory
                # Back track until we find the previous backslash
                for i in range(2, len(self.current_directory)):
                    if(self.current_directory[len(self.current_directory) - i] == '\\'):
                        self.current_directory = self.current_directory[0:len(self.current_directory)-i+1]
                        break
                
                # Now list the directory
                self.current_file_list = os.listdir(self.current_directory)
                if(self.current_directory != self.root):
                    self.current_file_list = [".."] + self.current_file_list
                
                # Rebuild the choiceblocks
                self.BuildChoiceBlocks(self.current_file_list)
            else:
                # Ok! Its a directory. 
                # Add to it
                self.current_directory += file_choice + "\\"
                self.current_file_list = [".."] + os.listdir(self.current_directory)
                self.BuildChoiceBlocks(self.current_file_list)

        else:
            if(self.callback):
                self.callback(self.id, input_type, self.current_directory + self.current_file_list[self.current_choice])
            if(input_type == self.CHOICE_CHOSEN):
                self.Delete()
        
    def Draw(self, elapsed):
        # Draw the upper ribbon bar
        engine2D.DrawBlock(self.x, self.y - self.font.ch_h * 2, self.w, self.font.ch_h * 2, 30, 30, 110, True)
        engine2D.DrawBlock(self.x - 1, self.y - self.font.ch_h * 2, self.w + 1, self.font.ch_h * 2, 255, 255, 255)
        current_file = "Selected: " + self.current_file_list[self.current_choice]
        if(os.path.isdir(self.current_directory + current_file)):
            current_file += " (DIRECTORY)"
        self.font.PutString(current_file, self.x, self.y - self.font.ch_h * 2)

        # Draw the rest of the list
        super().Draw(elapsed)

# Textbox control
# Creates a textbox control
# x,y,width,font
# height is one character tall (+2 pixels for padding)
class TextBox(engine2D.Object):

    def __init__(self, x, y, width, font):
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.text = ""
        self.display_text = ""
        self.font = font

        self.insertion_index =  0
        self.display_text_start_index = 0
        # How many characters can we display?
        self.max_chars_display = int(self.width / self.font.ch_w)

        self.cursor_timer = 0
        self.cursor_on = True
    
    def OnTextInput(self, elapsed, c):
        self.cursor_on = True
        if(c.isprintable()):
            self.text = self.text[0:self.insertion_index] + c + self.text[self.insertion_index:]
            self.insertion_index += 1
        elif(c == '\b'):
            self.text = self.text[0:self.insertion_index-1] + self.text[self.insertion_index:]
            self.insertion_index -= 1
    
        self.ValidateIndexes()

    def OnKeyPress(self, elapsed, key):
        self.cursor_on = True
        if(key == engine2D.Button.LEFT):
            self.insertion_index -= 1
        elif(key == engine2D.Button.RIGHT):
            self.insertion_index += 1
        
        self.ValidateIndexes()

    def ValidateIndexes(self):
        if(self.insertion_index >= len(self.text)):
            self.insertion_index = len(self.text)
        
        if(self.insertion_index < 0):
            self.insertion_index = 0

        if(self.insertion_index == self.display_text_start_index):
            self.display_text_start_index -= 1
        elif(self.insertion_index - self.display_text_start_index >= self.max_chars_display):
            self.display_text_start_index += 1
        
        if(self.display_text_start_index < 0):
            self.display_text_start_index = 0

    def Update(self, elapsed):
        self.cursor_timer += (elapsed/1000.0)
        if(self.cursor_timer >= 0.5):
            self.cursor_on = not self.cursor_on
            self.cursor_timer = 0

    def Draw(self, elapsed):
        engine2D.DrawBlock(self.x, self.y, self.width, self.font.ch_h, 0, 0, 0, True)
        engine2D.DrawBlock(self.x - 1, self.y - 1, self.width + 2, self.font.ch_h + 2, 255, 255, 255)
        display_text = self.text[self.display_text_start_index : self.display_text_start_index + self.max_chars_display]
        self.font.PutString(display_text, self.x, self.y)
        if(self.cursor_on):
            engine2D.DrawBlock(self.x + (self.insertion_index - self.display_text_start_index) * (self.font.ch_w), self.y + 1, self.font.ch_w * 0.5, self.font.ch_h - 2, 255, 255, 255, True)

# The console class creates a console on the screen
# This console gives a callback everytime ENTER is pressed
# with the arugment being a string passed to the callback that
# the user has entered.

# x,y,w,h - dimensions of the console
# font - font to be used by the console, can be BitmapFont or TrueTypeFont
# input_callback - a function that takes a int and a string as an argument
# called every time the user presses enter

# def input_callback(id, str):
#       pass

# Here "id" is the id of the console object. str is the line inputted to console

class Console(engine2D.Object):
    def __init__(self, x, y, w, h, font, input_callback):
        super().__init__()
        self.x = x
        self.y = y
        self.w = w
        self.h = h

        self.font = font

        # Console variables
        self.console_h = int(self.h / font.ch_h) - 1
        self.console_w = int(self.w / font.ch_w) - 1
        self.console_x = 0
        self.console_y = 0
        self.console_data = [[' ' for _ in range(0, self.console_w)] for _ in range(0,self.console_h)]
    

        # Input related functions
        self.input_callback = input_callback
        self.should_take_input = False
        self.should_take_choice = False
        self.input_string = ""

        # For the console cursor
        self.cursor_on = True
        self.cursor_timer = 0.0
        # 0.5 second interval
        self.cursor_blink_interval = 0.5

    def Update(self, elapsed):
        # Blink the cursor
        self.cursor_timer += (elapsed/1000)
        if(self.cursor_timer >= self.cursor_blink_interval):
            self.cursor_timer = 0
            self.cursor_on = not self.cursor_on

    def GetInput(self, prompt):
        self.PutString(prompt)
        self.should_take_input = True
    
    def OnTextInput(self, elapsed, c):
        # When typing make sure the cursor doesn't blink
        self.timer = 0
        self.cursor_on = True
        # Keyboard handler
        if(self.should_take_input):
            # If received newline, this is the end of the line
            if(c == '\n'):
                self.PutChar('\n')
                self.should_take_input = False
                self.input_callback(self.id, self.input_string)
                self.input_string = ""
            # Backspace handling
            elif(c == '\b'):
                if(len(self.input_string) > 0):
                    self.input_string = self.input_string[:-1]
                    self.UnPutChar()
            else:
                self.input_string += c
                self.PutChar(c)

    def ScrollUp(self):
        for k in range(0, self.console_h - 1):
            self.console_data[k] = [c for c in self.console_data[k+1]]

        for k in range(0, self.console_w):
            self.console_data[self.console_h - 1][k] = ' '
        
        self.console_y = self.console_h - 1
        self.console_x = 0
    
    def PutChar(self, c):
        if(c == '\n'):
            self.console_x = 0
            self.console_y += 1
        else:
            self.console_data[self.console_y][self.console_x] = c
            self.console_x += 1

        if(self.console_x >= self.console_w):
            self.console_y += 1
            self.console_x = 0
        
        # shift up the console since the old text has to be replaced.
        if(self.console_y >= self.console_h):
            self.ScrollUp()
    
    def UnPutChar(self):
        self.console_x -= 1
        if(self.console_x < 0):
            self.console_x = self.console_w - 1
            self.console_y -= 1
        
        if(self.console_y < 0):
            return
        
        self.console_data[self.console_y][self.console_x] = ' '

    def PutString(self, s):
        for c in s:
            self.PutChar(c)


    def Clear(self):
        self.console_x = 0
        self.console_y = 0
        for y in range(0, self.console_h):
            for x in range(0, self.console_w):
                self.console_data[y][x] = ' '
    
    def Draw(self, elapsed):
        # Draw a block around the console
        #engine2D.SetDrawingOpacity(128)
        engine2D.DrawBlock(self.x, self.y,self.w,self.h, 0, 0, 0, True, opacity=150)
        engine2D.DrawBlock(self.x-2, self.y-2,self.w+2, self.h +2, 255, 255, 255)
        #engine2D.SetDrawingOpacity(255)
        
        # Draw the console images

        # Draw the console characters
        for x in range(0, self.console_w):
            for y in range(0, self.console_h):
                self.font.PutChar(self.console_data[y][x], self.x + x * self.font.ch_w, self.y + y * self.font.ch_h)
        
        # Print the cursor if the flag is ON (the flag is toggled in update)
        if(self.cursor_on):
            engine2D.DrawBlock(self.x + self.console_x * self.font.ch_w, self.y + self.console_y * self.font.ch_h, self.font.ch_w, self.font.ch_h, 255, 255, 255, True)