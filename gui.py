# -*- coding: utf-8 -*-

"""
Created on Sun Apr 16 16:11:31 2017

@author: Tyler
"""
import time
import pickle
import os.path
import tkinter as tk
import sqlite3
from tkinter import ttk
from tkinter import messagebox
import tweepy
from string import punctuation
import webbrowser
import urllib

LARGE_FONT= ("Times New Roman", 12)
TWEET_FONT= ("Times New Roman",12)
LINK_FONT= ("Times New Roman", 18, 'underline')       #displays in the informational frame
BIG_WORD_FONT=("Times New Roman",32)                  #displays in the informational frame

class real_app(tk.Tk):
    def __init__(self, *args, **kwargs):
        '''builds the app, an MVC module'''
        tk.Tk.__init__(self, *args, **kwargs)

        self.auth = None
        self.api = None
        self.db = None

        container = tk.Frame(self)

        container.pack(side='top', fill='both', expand = True)
        container.grid_rowconfigure(0,weight=1)
        container.grid_columnconfigure(0,weight=1)

        self.check_pass = self.check_for_credidentials()

        self.frames={}

        for F in (StartPage, MainPage):

            frame = F(container, self)

            self.frames[F]= frame

            frame.grid(row=0, column = 0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):
        '''brings the desired from to the front of the application'''
        frame = self.frames[cont]
        frame.tkraise()


    def check_for_credidentials(self):
        '''is there a save file? if yes load it'''
        #TODO: this messes up if called to run from command line outside of src folder...
        if os.path.isfile('secrets.pkl'):
            with open('secrets.pkl','rb') as p:
                return pickle.load(p)

        return False

class StartPage(tk.Frame):
    '''this frame is where the user enters their credidentials'''

    def __init__(self,parent,controller):
        self.controller = controller
        tk.Frame.__init__(self,parent)

        tk.Message(self, text="Enter your credentials obtained from developer.twitter.com",
                        justify = 'left',
                        aspect = 400).pack(pady=(15,0))

        dialog_frame = tk.Frame(self)
        dialog_frame.pack(padx=20, pady=15, anchor='w')

        ###################################################################################
        #code below needs fine tuning, it works for my screen but could be wack for others#
        ###################################################################################
        self.x = (self.controller.winfo_screenwidth() -
            self.controller.winfo_reqwidth()) // 3
        self.y = (self.controller.winfo_screenheight() -
             self.controller.winfo_reqheight()) // 6
        self.controller.geometry("+{}+{}".format(self.x,self.y))
        ####################################################################

        #StringVars to load in twitter access keys and tokens
        self.civ = tk.StringVar()
        self.civ_secret = tk.StringVar()
        self.atv = tk.StringVar()
        self.atv_secret = tk.StringVar()
        self.checked = tk.IntVar()

        if controller.check_pass:
            self.civ.set(self.controller.check_pass['consumer_key'])
            self.civ_secret.set(self.controller.check_pass['consumer_secret'])
            self.atv.set(self.controller.check_pass['access_token'])
            self.atv_secret.set(self.controller.check_pass['access_token_secret'])
            self.checked.set(1)

        tk.Label(dialog_frame, text='Consumer Key:').grid(row=0, column= 0, sticky = 'w')

        self.consumer_input = tk.Entry(dialog_frame, textvariable = self.civ, background = 'white', width=24, show = '*')
        self.consumer_input.grid(row=0, column=1, sticky = 'w')
        self.consumer_input.focus_set()

        tk.Label(dialog_frame, text='Consumer Secret').grid(row=1, column=0, sticky='w')

        self.consumer_secret_input = tk.Entry(dialog_frame, textvariable = self.civ_secret, background='white', width = 24, show='*')
        self.consumer_secret_input.grid(row=1, column=1, sticky = 'w')

        tk.Label(dialog_frame, text='acess token').grid(row=2, column=0, sticky='w')

        self.access_token_input = tk.Entry(dialog_frame, textvariable =self.atv, background='white', width = 24, show='*')
        self.access_token_input.grid(row=2,column=1, sticky = 'w')

        tk.Label(dialog_frame, text= 'access token secret').grid(row=3, column=0, sticky='w')

        self.access_token_secret_input = tk.Entry(dialog_frame, textvariable = self.atv_secret, background = 'white', width=24, show= '*')
        self.access_token_secret_input.grid(row=3,column=1, sticky = 'w')


        button_frame = tk.Frame(self)
        button_frame.pack(padx=15, pady=(0,15),anchor='w')

        cbox = tk.Checkbutton(button_frame, text = 'remember tokens/secrets', variable = self.checked)
        cbox.pack()

        tk.Button(button_frame, text='OK', height=1, width=6, default='active', command=self.click_ok).pack(side='right')

    def connectToApi(self,consumer_token, consumer_secret,access_token,access_secret):
        self.controller.auth = tweepy.OAuthHandler(consumer_token, consumer_secret)
        self.controller.auth.set_access_token(access_token,access_secret)
        return tweepy.API(self.controller.auth)

    def click_ok(self):
        if not self.controller.check_pass and self.checked.get() == 1:
         #there is no save file and the user would like to save
             self.controller.api = self.connectToApi(self.consumer_input.get(),
                                                    self.consumer_secret_input.get(),
                                                    self.access_token_input.get(),
                                                    self.access_token_secret_input.get())

             with open('secrets.pkl','wb') as p:
                 pickle.dump({'consumer_key':self.consumer_input.get(),
                             'consumer_secret':self.consumer_secret_input.get(),
                             'access_token':self.access_token_input.get(),
                             'access_token_secret':self.access_token_secret_input.get()},p)
             try:
                 self.controller.api.auth.get_username()
                 self.controller.show_frame(MainPage)

             except:
                 return tk.messagebox.showerror("Error","could not connect to api")


        elif self.checked.get() == 1 and self.controller.check_pass:
            #is this the best way to check?
            if self.controller.check_pass['consumer_key'] == self.consumer_input.get():
                self.controller.api = self.connectToApi(self.consumer_input.get(),self.consumer_secret_input.get(),
                                        self.access_token_input.get(),self.access_token_secret_input.get())
                try:
                    self.controller.api.auth.get_username()
                    self.controller.show_frame(MainPage)
                except:
                    tk.messagebox.showerror('error',' could not connect to api')

            else:
                #this looks awful
                test = messagebox.askokcancel("overwrite request","overwrite save data?")
                if test:
                    self.api = self.connectToApi(self.consumer_input.get(),self.consumer_secret_input.get(),
                    self.access_token_input.get(),self.access_token_secret_input.get())
                    try:
                        self.api.auth.get_username()
                        self.controller.show_frame(MainPage)

                        with open('src/secrets.pkl','wb') as p:
                            pickle.dump({'consumer_key':self.consumer_input.get(),
                                         'consumer_secret':self.consumer_secret_input.get(),
                                         'access_token':self.access_token_input.get(),
                                         'access_token_secret':self.access_token_secret_input.get()},p)
                    except ValueError:
                        tk.messagebox.showerror('error', 'unable to connect to api')

        else:
                try:
                    self.controller.api = self.connectToApi(self.consumer_input.get(),self.consumer_secret_input.get(),
                                    self.access_token_input.get(),self.access_token_secret_input.get())

                    self.controller.show_frame(MainPage)
                except:
                    messagebox.showerror('error', 'could not connect to api')
        self.controller.db = connectToDB()
            #tk.Label(text = "failed to connect to api", justify = 'center').pack()



class MainPage(tk.Frame):
    def __init__(self, parent, controller):
        self.controller = controller
        self.tweet_list = None
        self.buttons_displayed = False
        self.rate_limit_displayed = False
        self.tweet_list_position = 0
        self.trend_time = None

        tk.Frame.__init__(self, parent)

        self.left_frame = tk.Frame(self)
        self.left_frame.pack(side = 'left',anchor = 'n')

        self.middle_frame = tk.Frame(self, width = 800, height = 200)
        self.middle_frame.pack(side = 'left', anchor = 'nw')

        self.word_information_frame = tk.Frame(self.middle_frame)
        self.word_information_frame.pack(side = 'bottom', anchor ='nw')

        self.word_information_header_frame = tk.Frame(self.word_information_frame)
        self.word_information_header_frame.pack()

        self.translation_frame = tk.Frame(self.word_information_frame)

        self.note_frame = tk.Frame(self.word_information_frame)
        self.note_text_frame = tk.Frame(self.word_information_frame)


        self.remaining_calls_var = tk.StringVar()
        self.show_remaining_calls = tk.Label(self.left_frame,
                                            textvariable = self.remaining_calls_var)

        self.position_frame = tk.Frame(self.middle_frame)
        self.position_frame.pack()

        self.left_button_frame = tk.Frame(self.middle_frame)
        self.left_button_frame.pack(side = 'left')

        self.tweet_frame = tk.Frame(self.middle_frame)
        self.tweet_frame.pack(side='left')
        self.tweet_frame.pack_propagate('false')

        self.word_button_frame1 = tk.Frame(self.tweet_frame)
        self.word_button_frame1.pack(side = 'top')

        self.word_button_frame2 = tk.Frame(self.tweet_frame)
        self.word_button_frame2.pack(side = 'top')

        self.word_button_frame3 = tk.Frame(self.tweet_frame)
        self.word_button_frame3.pack(side = 'top')

        self.right_button_frame = tk.Frame(self.middle_frame)
        self.right_button_frame.pack(side='left')

        self.next_tweet_button = tk.Button(self.right_button_frame,
                                           text = ">",
                                           command = self.get_next_tweet,
                                           state = 'disabled')

        self.big_word_var = tk.StringVar()
        self.big_word = tk.Entry(self.word_information_header_frame,
                                textvariable = self.big_word_var,
                                font = LARGE_FONT,
                                width = 31,
                                relief = 'flat',
                                state = 'readonly')#width = 23????

        self.position_display_var = tk.StringVar()
        self.position_display = tk.Label(self.position_frame,
                                        textvariable = self.position_display_var)

        self.position_display.pack(anchor = 'n')

        self.display_tweet_var = tk.StringVar()

        self.previous_tweet_button = tk.Button(self.left_button_frame,
                                               text= "<",
                                               command = self.get_previous_tweet,
                                               state = 'disabled')

        self.combbox = ttk.Combobox(self.left_frame,state='readonly')
        self.combbox['values'] = ('English','Spanish','Russian')
        self.combbox.current(0)
        self.combbox.pack()

        self.get_trends_var = tk.StringVar()
        self.get_trends_var.set("get trends")
        self.get_trends_button = tk.Button(self.left_frame,
                                           textvariable = self.get_trends_var,
                                           command = self.load_trends)
        self.get_trends_button.pack()

        #TODO: scroll bar for lbox
        self.lbox = tk.Listbox(self.left_frame)
        self.lbox.pack()

        self.get_tweets_var = tk.StringVar()
        self.get_tweets_var.set('get tweets')
        self.get_tweets_button = tk.Button(self.left_frame,
                                           textvariable = self.get_tweets_var,
                                           command = self.get_tweets).pack()

        self.dictionary_popup_menu = tk.Menu(self.word_information_frame,tearoff = 0)
        self.dictionary_popup_menu.add_command(label = 'Copy', command = self.copy_word)
        self.big_word.bind("<Button-3>",self.popup)

#TODO : learn how to unit test properly

    def load_test_trends(self):
        '''testing loading in to the listbox'''
        for item in ['one','two','three','four']:
            self.lbox.insert('end',item)
        self.get_trends_button.config(state = 'disabled')

    def load_trends(self):
        #this will have a way to check what item from combobox is selected and push it in to the id number)
        #would it help to put these somewhere else as they are always constant.
        self.WOEIDS = {'English':23424977,
                       'Russian':23424936,
                       'Spanish':23424900 }
        #check if it has been 5 minutes since the last request for trends.
        if self.trend_time and time.time()-self.trend_time < 300:
            if self.selectedLanaguage == self.WOEIDS[self.combbox.get()]:
            #WHY ISN"T THIS WORKING
                tk.messagebox.showerror("error","trends only update every five minutes. please wait.")
        self.selectedLanaguage = self.WOEIDS[self.combbox.get()]

        for trend in [t['name'] for t in self.controller.api.trends_place(self.selectedLanaguage)[0]['trends']]:
            self.lbox.insert('end',trend)
        self.trend_time = time.time()
        #self.get_trends_button.config(state='disabled')

    def get_tweets(self):
        search_term = self.lbox.get('active')
        if search_term == '':
            return
        self.controller.minsize(850,0)
        #should i just make tweet_list an empty list to begin with and append
        #everything so i don't need if else statements?
        #self.tweet_frame.pack(side='left')
        #TODO: more language codes
        self.tweet_frame.config(width = 600, height = 100, relief = 'ridge')
        self.languageCodes = {'English': 'en',
                              'Russian': 'ru',
                              'Spanish': 'es'}

        #if self.tweet_frame['relief'] == 'flat':
        #    self.tweet_frame.config(relief = 'ridge')

        if self.buttons_displayed:
            pass
        else:
            self.display_buttons()

        self.tweet_frame.pack(side='left')

        if self.rate_limit_displayed:
            pass
        else:
            self.display_rate_limit()
        if not self.tweet_list:
            self.tweet_list = [i for i in self.controller.api.search(q = search_term +
                               "-filter:retweets AND -filter:replies",lang = self.languageCodes[self.combbox.get()], count = 20)]
            #self.tweet_list = [i.text.lower().strip() for i in self.controller.api.api.search(q = search_term +
            #                   " -filter:retweets AND -filter:replies", lang = self.languageCodes[self.combbox.get()], count = 20)]
        else:
            for i in [i for i in self.controller.api.search(q = search_term +
                                                                "-filter:retweets AND -filter:replies", lang = 'ru', count = 20)]:
                self.tweet_list.append(i)
            #for i in [i.text.strip() for i in self.controller.api.api.search(q = search_term +
            #          " -filter:retweets AND -filter:replies", lang = 'ru', count = 20)]:
            #    self.tweet_list.append(i)
        if self.next_tweet_button['state'] == 'disabled':
            self.next_tweet_button.config(state='normal')
        if len(self.tweet_list) > 0:
            self.get_tweet_list_position()
            self.display_tweets()
            self.update_rate_limit()

    def display_tweets(self):
        max_frame_length = 525
        #can i make this more dynamic?
        # an if statement that says if tweet_list is none do this

        #Bindings do not work perfectly but can improve workflow
        # issues arise when focus is lost from the middle frame, the below code
        # can take care of most instances but the user may still find cases where
        # the left and right keys do not display the next or previous tweet.
        #
        ##TODO an if statement that says 'are these keys already bound? or a func that says isBound() true pass else bind'
        #self.middle_frame.focus_set()
        #self.left_frame.bind('<1>', lambda e: self.middle_frame.focus_set())
        #self.middle_frame.bind('<1>',lambda e: self.middle_frame.focus_set())
        #self.middle_frame.bind('<Right>',lambda e: self.get_next_tweet())
        #self.middle_frame.bind('<Left>',lambda e: self.get_previous_tweet())
        #
        ############################################################################################
        #TODO: save button configurations for easier method of going backwards?
        for button in self.word_button_frame1.winfo_children():
            button.destroy()
            self.word_button_frame1.update_idletasks()

        for button in self.word_button_frame2.winfo_children():
            button.destroy()
            self.word_button_frame2.update_idletasks()

        for button in self.word_button_frame3.winfo_children():
            button.destroy()
            self.word_button_frame3.update_idletasks()
        self.tweet_text = self.tweet_list[self.tweet_list_position].text.replace(',',' ')
        self.expanded_url = None
        #try catch used in case there is more than one link, second link is usually an image and not reachable via browser.
        #TODO: tidy this up later
        self.entities = self.tweet_list[self.tweet_list_position].entities
        if self.entities['urls']:
            self.expanded_url = self.tweet_list[self.tweet_list_position].entities['urls'][0]['expanded_url']

        self.split_tweet = self.tweet_text.split()
            # original one line method, now we replace comma with space and then move forward
            #self.split_tweet = self.tweet_list[self.tweet_list_position].split()

        for word in self.split_tweet:
                ##############################################
                # at size 12 font each button has a width of 15, and each character adds length 10, roughly #
                # this will be important to know if i want to make it adjustable in the future #
                ###############################################
            if self.word_button_frame1.winfo_width() < max_frame_length:
                self.create_word_buttons(word, self.word_button_frame1)
            elif self.word_button_frame1.winfo_width() > max_frame_length and self.word_button_frame2.winfo_width() < max_frame_length:
                if self.word_button_frame3.winfo_children():
                    self.create_word_buttons(word, self.word_button_frame2)
                elif (self.word_button_frame2.winfo_width() + 11 + (len(word) * 10)) > max_frame_length + 50:
                    #could probably consilidate this elif with the original...
                    self.create_word_buttons(word, self.word_button_frame3)
                else:
                    self.create_word_buttons(word, self.word_button_frame2)

            else:
                self.create_word_buttons(word, self.word_button_frame3)
            self.tweet_frame.update_idletasks()

    def create_word_buttons(self, word, frame):
        try:
            self.b = tk.Button(frame, text = word, font = TWEET_FONT, relief = 'flat', cursor = 'hand2', command = lambda: self.display_word_definition(word))
            self.b.pack(side = 'left')
        except:
            pass

    def display_word_definition(self, word):
        #TODO: wrap this in an if statement?
        #if self.word_ifnromation_frame['borderwidth'] == 2: ???
        self.word_information_frame.config( borderwidth = 2,relief = 'ridge')

        if word[:4] == 'http':
            self.big_word.config(width = 56) #slight height difference with this method, figure out hieght later
            for i in (self.translation_frame,self.note_frame, self.note_text_frame):
                for child in i.winfo_children():
                    child.destroy()
            self.big_word.pack()
            self.big_word.config(fg = 'blue', cursor = 'hand2', font = LINK_FONT, width = 50)
            self.big_word_var.set(self.expanded_url)
            self.big_word.bind('<Button-1>',self.click_link)

        else:
            self.big_word.config(width = 32)
            self.big_word.unbind('<Button-1>')
            self.big_word.config(fg = 'black', cursor = 'arrow', font = BIG_WORD_FONT, width = 30)
            punc = punctuation.replace('-','«»') + '…'
            self.word_no_punctuation = ''.join(c for c in word if c not in punc if not c.isdigit()).lower()

            if self.word_no_punctuation == self.big_word_var.get():
                return
            if len(self.word_no_punctuation) == 0:
            #TODO: something here to avoid buttons coming up to add translation for it
                return

            if self.word_no_punctuation[-1] == '-':
                self.word_no_punctuation = self.word_no_punctuation[:-1]

            self.big_word.pack(side = 'top', anchor = 'w')
            self.big_word_var.set(self.word_no_punctuation)
        #TODO maybe make this a select 1 statement to save time when the document gets big?
            self.result = self.controller.db.cursor.execute('''select * from words where word = :bigword''',{'bigword': self.word_no_punctuation})
            self.result =self.controller.db.cursor.fetchone()

            self.load_entry_fields(self.result)

    def click_link(self,event):
        webbrowser.open_new(self.big_word_var.get())

    def load_entry_fields(self, data):
        #this would delete any work not saved to db...
        #TODO: should i declare these buttons in __init__ like i do the frames?
        #then config them??? i feel like i did it this way for a reason...
        for i in (self.translation_frame,self.note_frame, self.note_text_frame):
            for child in i.winfo_children():
                child.destroy()
        self.translation_frame.pack(anchor = 'w')
        self.note_frame.pack(anchor = 'w')
        self.note_text_frame.pack(anchor = 'w')

        self.translation_label = tk.Label(self.translation_frame, text = 'Translation: ',justify = 'left').pack(side = 'left', anchor = 'w')

        self.note_label = tk.Label(self.note_frame, text = 'Notes: ').pack(side = 'left')
        self.web_translate = tk.Button(self.translation_frame,
                                        text = 'google translate',
                                        command = self.get_web_translation)
        if data == None:
            self.web_translate.pack()
            self.translation_button = tk.Button(self.translation_frame,
                                                text = 'add translation',
                                                command = lambda: self.add_translation_entry(self.translation_button))
            self.translation_button.pack(side = 'left')
            self.note_button = tk.Button(self.note_frame, text = 'add notes', command = lambda: self.add_note_text(self.note_button))
            self.note_button.pack(side = 'left')

        else:
            if not data[2]:
                self.web_translate.pack()
                self.add_informational_buttons('translation')

            else:
                self.edit_translation_button = tk.Button(self.translation_frame, text = 'edit', command = self.edit_translation)
                self.edit_translation_button.pack(side='left')
                self.trans_v = tk.StringVar()
                self.trans_v.set(str(data[2]))
                self.translation = tk.Entry(self.translation_frame, state = 'readonly', textvariable = self.trans_v, relief = 'flat')
                #self.translation.insert(0,str(data[2]))
                #self.translation.insert(str(data[2]))
                self.translation.pack(side='left')

            if not data[5]:
                self.add_informational_buttons('note')
            else:
                self.note_save_button = tk.Button(self.note_text_frame, text = 'edit', command = self.edit_note)
                self.note_save_button.pack(side = 'left')
                self.note_text = tk.Text(self.note_text_frame, width = 30, height = 5, relief = 'flat')
                self.note_text.insert('end',str(data[5]))
                self.note_text.config(state='disabled')
                self.note_text.pack(side = 'left')

    def add_informational_buttons(self,btype):
        if btype == 'translation':
            self.translation_button = tk.Button(self.translation_frame, text = 'add translation', command = lambda: self.add_translation_entry(self.translation_button))
            self.translation_button.pack(side='left')

        elif btype == 'note':
            self.note_button = tk.Button(self.note_frame, text = 'add note ', command = lambda: self.add_note_text(self.note_button))
            self.note_button.pack(side = 'right')

    def display_buttons(self):
        self.next_tweet_button.pack(side = 'left', anchor = 'n')
        self.previous_tweet_button.pack()

        self.buttons_displayed = True

    def add_translation_entry(self, button):
        button.destroy()
        self.translation_entry = tk.Entry(self.translation_frame)
        self.translation_entry.pack(side = 'left')
        self.translation_entry.bind('<Return>', lambda e: self.update_translation_field())

    def edit_translation(self):
        #we need to change translation to a read only entry
        self.translation.config(state = 'normal', relief = 'ridge')
        self.translation.bind('<Return>', lambda e: self.update_existing_translation())

    def edit_new_translation(self):
        self.translation_entry.config(state='normal',relief = 'ridge')
        self.translation_entry.bind('<Return>', lambda e: self.update_new_existing_translation())

    def get_web_translation(self):
        q= urllib.parse.quote(self.big_word_var.get())
        url= 'https://translate.google.com/#ru/en/'
        webbrowser.open(url+q)

    def add_note_text(self, button):
        button.destroy()
        self.note_text = tk.Text(self.note_text_frame, height = 5, width = 30, pady = 0, padx = 0)
        self.note_text.focus_set()
        self.note_text.pack(side = 'left', anchor = 'sw')
        self.note_save_button = tk.Button(self.note_text_frame, text = 'save', command = self.save_note)
        self.note_save_button.pack()

    def save_note(self):
        nstring = self.note_text.get(1.0,'end')
        wstring = self.big_word_var.get()

        if nstring == '':
            pass

        else:
            is_in_db = self.controller.db.cursor.execute('''select * from words where word = :word''',{'word': wstring})
            is_in_db = is_in_db.fetchone()

            if is_in_db == None:
                self.controller.db.cursor.execute('''insert into words(word, notes) VALUES(:word,:note)''',{'word': wstring, 'note':nstring})

            else:
                self.controller.db.cursor.execute('''update words SET notes = :note where word = :word''',{'note': nstring, 'word':wstring})

        self.controller.db.db.commit()
        self.note_text.config(relief = 'flat', state = 'disabled')
        self.note_save_button.config(text = 'edit', command = self.edit_note)

    def edit_note(self):
        self.note_text.config(state = 'normal')
        self.note_save_button.config(text = 'save', command = self.save_note)

    def update_existing_translation(self):
        '''i know 100 percent i can consolodate this with update translation field, just gotta figure out those last 2 linesish'''
        wstring = self.big_word_var.get()
        tstring = self.translation.get()
        self.controller.db.cursor.execute('''update words SET translation = :tstring where word = :wstring''',{'tstring': tstring,'wstring':wstring})
        self.controller.db.db.commit()
        self.translation.config(state = 'readonly', relief = 'flat')

    def update_new_existing_translation(self):
        wstring = self.big_word_var.get()
        tstring = self.translation_entry.get()
        self.controller.db.cursor.execute('''update words SET translation = :tstring where word = :wstring''',{'tstring': tstring,'wstring':wstring})
        self.controller.db.db.commit()
        self.translation_entry.config(state = 'readonly', relief = 'flat')

    def update_translation_field(self):
        wstring = self.big_word_var.get()
        tstring = self.translation_entry.get()

        if tstring == '':
            pass
        else:
            #TODO: efficient check for if the word is already in the dictionary?
            is_in_db = self.controller.db.cursor.execute('''select * from words where word = :word''',{'word': wstring} )
            is_in_db = is_in_db.fetchone()
            if is_in_db:
                self.controller.db.cursor.execute('''update words SET translation = :tstring where word = :wstring''',{'tstring': tstring,
                                                                                                                    'wstring':wstring})
            else:
                self.controller.db.cursor.execute('''insert into words(word,translation) VALUES(:word, :tstring)''',{'tstring': tstring,
                                                                                                          'word':wstring})

            self.controller.db.db.commit()
            self.translation_entry.config(state = 'readonly')
            self.translation_entry.config(relief = 'flat')
            self.edit_translation_button = tk.Button(self.translation_frame, text = 'edit', command = self.edit_new_translation)
            self.edit_translation_button.pack(side='left')

    def get_previous_tweet(self):
        if self.tweet_list_position == 0:
            return
        if self.tweet_list_position == 1:
            self.previous_tweet_button.config(state= 'disabled')

        elif self.tweet_list_position == len(self.tweet_list) - 1:
            self.next_tweet_button.config(state='normal')

        self.tweet_list_position -= 1
        self.display_tweets()

        self.get_tweet_list_position()

    def get_next_tweet(self):
        if self.tweet_list_position == len(self.tweet_list) - 1:
            #this if statement needed for key binding
            return
        if self.tweet_list_position + 1 == len(self.tweet_list) - 1:
            self.tweet_list_position += 1
            self.display_tweets()
            self.next_tweet_button.config(state='disabled')

        elif self.tweet_list_position == 0:
            self.tweet_list_position += 1
            self.display_tweets()
            self.previous_tweet_button.config(state= 'normal')

        else:
            self.tweet_list_position += 1
            self.display_tweets()
        self.get_tweet_list_position()

    def get_tweet_list_position(self):
        self.position_display_var.set("{} of {}".format(self.tweet_list_position + 1, len(self.tweet_list)))

    def update_rate_limit(self):
        self.limit = self.controller.api.rate_limit_status()['resources']['search']['/search/tweets']['remaining']
        self.remaining_calls_var.set("calls remaining: {}".format(self.limit))

    def display_rate_limit(self):
        self.show_remaining_calls.pack(side = 'bottom')
        self.rate_limit_displayed = True

    def copy_word(self):
        self.big_word.selection_range(0,'end')
        self.controller.clipboard_clear()
        self.controller.clipboard_append(self.big_word_var.get())
        self.controller.update()

    def popup(self, event):
        self.dictionary_popup_menu.post(event.x_root, event.y_root)

class connectToDB:
    def __init__(self):
        self.db = sqlite3.connect('guidb.db')
        self.cursor = self.db.cursor()

if __name__ =='__main__':
    app = real_app()
    app.wm_title('twitter_language_enhancer')
    app.mainloop()
