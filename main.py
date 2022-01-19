import kivy
from kivymd.app import MDApp
__version__ = '0.1'
import sqlite3
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager,Screen
from kivymd.uix.dialog import MDDialog
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivymd.uix.button import MDRectangleFlatButton
from kivy.uix.scrollview import ScrollView
from kivy.base import runTouchApp
from kivy.core.window import Window
from kivymd.uix.list import MDList
from kivymd.uix.button import MDIconButton
from kivymd.uix.list import OneLineIconListItem,OneLineListItem,IconLeftWidget
from kivy.uix.dropdown import DropDown
import datetime
from kivy.utils import rgba
from kivy.storage.jsonstore import JsonStore
from os.path import join



#global variables to be referenced by multiple Screen
screenManager=ScreenManager()
chat_messages_list_view = MDList()
data_dir = MDApp().user_data_dir
store = JsonStore(join(data_dir, 'storage.json'))


#Screen and Layout classes
class BottomMenu(BoxLayout):
    pass

class AfterTopMenuLayout(BoxLayout):
    pass
class SearchBarLayout(BoxLayout):
    pass

class WelcomeScreen(Screen):
    pass
class MessageScrollView(ScrollView):
    pass
class ContactScrollView(ScrollView):
    pass
class ChatContactsScreen(Screen):
    chatContactsBoxLayout=ObjectProperty()
    pass
class ChatScreen(Screen):
    chatScreenBoxLayout=ObjectProperty()
    chatMessage = ObjectProperty(None)
    dialog=None
    def sendChat(self):
        chatMessage=self.chatMessage.text
        if chatMessage.strip()!="" and chatMessage is not None:
            self.chatMessage.text=""
            icons = IconLeftWidget(icon="account")
            items = OneLineIconListItemAligned(halign="left",text=chatMessage)
            
            items.add_widget(icons)
            chat_messages_list_view .add_widget(items)
        else:
             self.dialog=MDDialog(
                title="Type a message",
                text="Empty Message",
                buttons=[
                   MDRectangleFlatButton(text="OK",on_release=self.close_dialog)
                ]
            )
             self.dialog.open()
    def close_dialog(self,obj):
        self.dialog.dismiss()

class NotifyMessageListScreen(Screen):
    def redirect_home_login(self):
        if isLoggedIn():
            screenManager.current="welcomeScreen"
        else:
            screenManager.current="loginScreen"


class NotifyMessageScreen(Screen):
    pass

class MailInboxScreen(Screen):
    pass

class SearchScreen(Screen):
    def search(self):
        #populate search results list  based on search text
        searchText=self.searchText.text
        if searchText.strip()!="" and searchText is not None:
            self.searchText.text=""
            searchResultScroll = ScrollView()       
            searchResultList = MDList()
            for i in range(5):
                item = OneLineListItemAligned(halign="left",text=searchText+"-->"+str(i))
                searchResultList.add_widget(item)

            searchResultScroll.add_widget(searchResultList)
            self.ids.searchResultsBox.clear_widgets()
            self.ids.searchResultsBox.add_widget(searchResultScroll)
          
        else:
             self.dialog=MDDialog(
                title="Empty Text",
                text="Type a search text",
                buttons=[
                   MDRectangleFlatButton(text="OK",on_release=self.close_dialog)
                ]
            )
             self.dialog.open()
    def close_dialog(self,obj):
        self.dialog.dismiss()


class GamesScreen(Screen):
    pass

class OneLineIconListItemAligned(OneLineIconListItem):
    def __init__(self, halign, **kwargs):
        super(OneLineIconListItemAligned, self).__init__(**kwargs)
        self.ids._lbl_primary.halign = halign
class OneLineListItemAligned(OneLineListItem):
    def __init__(self, halign, **kwargs):
        super(OneLineListItemAligned, self).__init__(**kwargs)
        self.ids._lbl_primary.halign = halign

class LoginScreen(Screen):

    #property in main.kv
    email = ObjectProperty(None)
    password = ObjectProperty(None)

    dialog=None

    def login(self):
        #login user with kp@gmail.com and almond.2 as password as pre-loaded in sqlite db
        conn=sqlite3.connect('eezyn_app.db')
        cursor=conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email='"+self.email.text+"' and password='"+self.password.text+"'")
        rows = cursor.fetchall()
        
        #if logged in email in store and change to welcome screen else popup a validation message
        if len(rows)>0:
            screenManager.get_screen('welcomeScreen').welcomeName.text="Welcome,"+self.email.text
            store.put('credentials', username=self.email.text, password=self.email.password)
            screenManager.current='welcomeScreen'           
        else:
            self.dialog=MDDialog(
                title="Invalid User",
                text="Wrong Email or Password",
                buttons=[
                   MDRectangleFlatButton(text="OK",on_release=self.close_dialog)
                ]
            )
            self.dialog.open()

    def close_dialog(self,obj):
        self.dialog.dimiss()

class ScreenManager(ScreenManager):
  
    pass



class ScrollableTopMenu(ScrollView):
    manager=screenManager
    pass


class MainApp(MDApp):

     def build(self):
         
         self.theme_cls.primary_palette = "Gray"
         #create app screens
         self.chatScreen=ChatScreen(name='chatScreen')
         self.loginScreen=LoginScreen(name='loginScreen')
         self.notifyMessageListScreen=NotifyMessageListScreen(name='notifyMessageListScreen')
         self.chatContactsScreen=ChatContactsScreen(name='chatContactsScreen')
         self.welcomeScreen=WelcomeScreen(name='welcomeScreen')
         self.notifyMessageScreen=NotifyMessageScreen(name='notifyMessageScreen')
         self.mailInboxScreen=MailInboxScreen(name='mailInboxScreen')
         self.searchScreen=SearchScreen(name='searchScreen')
         self.gameScreen=GamesScreen(name='gamesScreen')
         self.chatContactScreen=ChatScreen(name='chatContactScreen')

         #add screens to screen manager
         self.add_screens()

         #create notifylist dropdown menu
         dropDown = DropDown()
         notifyList=["Notify-Rewards","Notify-Auctions","Notify-AMS-Social","Notify-AMS-Discuss","Notify-AMS-Blog"]
         for item in notifyList:
            notify_item_btn = Button(text =item, size_hint_y = None,size_hint_x=(1), height = 30,width=100)
            notify_item_btn.bind(on_release = lambda btn: dropDown.select(notify_item_btn.text))
            dropDown.add_widget(notify_item_btn)
  
         mainbutton = Button(text ='Notify All', size_hint =(0.8, None), height=35)
         mainbutton.bind(on_release = dropDown.open)
         dropDown.bind(on_select = lambda instance, x: setattr(mainbutton, 'text', x))
         self.notifyMessageListScreen.notifyDropDownLayout.add_widget(mainbutton)

         #populate notify messages list
         notifyMessages_scroll = ScrollView()       
         notifyMessages_view = MDList()
         for i in range(5):
            items = OneLineListItemAligned(halign="left",text='Message '+str(i),on_release=self.click_message_handler)
            notifyMessages_view.add_widget(items)

         notifyMessages_scroll.add_widget(notifyMessages_view)
         self.notifyMessageListScreen.notifyMessageListLayout.add_widget(notifyMessages_scroll)


         #populate mail inbox list
         mailInbox_scroll = ScrollView()       
         mailInbox_view = MDList()
         for i in range(5):
            items = OneLineListItemAligned(halign="left",text='Mail '+str(i))
            mailInbox_view.add_widget(items)

         mailInbox_scroll.add_widget(mailInbox_view)
         self.mailInboxScreen.inboxListLayout.add_widget(mailInbox_scroll)
         
         #populate chat contacts list
         contacts_scroll = ContactScrollView()
         
         contactlist_view = MDList()
         for i in range(5):

            icons = IconLeftWidget(icon="account")
            items = OneLineIconListItemAligned(halign="left",text='Contact '+str(i),on_release=self.click_contact_handler )
            items.add_widget(icons)
            contactlist_view.add_widget(items)

         contacts_scroll.add_widget(contactlist_view)
         self.chatContactsScreen.chatContactsBoxLayout.add_widget(contacts_scroll)
               
         #initialize chat message listview and scrollview
         chat_messages_scroll =MessageScrollView()       
         chat_messages_scroll.add_widget(chat_messages_list_view )
         self.chatScreen.chatScreenBoxLayout.add_widget(chat_messages_scroll)


         #build games screen widgets
         seeMoreButton =Button(text="See More",size_hint=(0.2,0.1),pos_hint={"center_x":0.9},background_color=(0, 1, 0, 1),font_size="10dp")


         for i in range(3):
             games_grid=GridLayout()
             games_grid.cols=3
             games_grid.rows=1

             game_item_btn=Button(text="Game "+str(i),background_normal="images/game.jpg",size_hint_x=(None))
             game_item_name1=Label(text="Item "+str(i+1),color=(0, 0, 0, 1),pos_hint={"center_x":0.1})
             game_item_name1.font_style="bold"
             game_item_name2=Label(font_size="8dp",text="Item "+str(i+2),color=(0, 0, 0, 1),size_hint_y=(0.15),pos_hint={"center_x":0.1})
             game_item_name1.background_color=(1, 1, 0,1)
             game_item_name2.background_color=(1, 1, 0,1)
             game_item_box=BoxLayout(orientation="vertical",padding=5)
             game_item_box.add_widget(game_item_btn)

             game_item_texts_box=BoxLayout(orientation="vertical",size_hint=(None,0.1),padding=5)
             game_item_texts_box.add_widget(game_item_name1)
             game_item_texts_box.add_widget(game_item_name2)


             #review section box
             review_box=BoxLayout(orientation="horizontal",size_hint=(None,0.1),pos_hint={"center_y":0.5,"center_x":0.1}, padding=2)

             rev_btn1 = MDIconButton(
                icon="star" 
                         
                    )
             rev_btn2=MDIconButton(
                icon="star" 
                    
        
                    )
             rev_btn3 =  MDIconButton(
                icon="star" 
              
                    )
             rev_btn4 = MDIconButton(
                icon="star"
               
                    )
             rev_btn5 =  MDIconButton(
                icon="star" 
               
                    )
             review_box.add_widget(rev_btn1)
             review_box.add_widget(rev_btn2)
             review_box.add_widget(rev_btn3)
             review_box.add_widget(rev_btn4)
             review_box.add_widget(rev_btn5)

             review_box.add_widget(Label(text="FREE",pos_hint={"right":0.8},color=(0,0,0,1)))
   
             game_item_box.add_widget(game_item_texts_box)
             game_item_box.add_widget(review_box)

             games_grid.add_widget(game_item_box)  
         
         self.gameScreen.gamesBoxLayout.add_widget(Label(text="New + Updated Games",pos_hint={"right":0.8},color=(0,0,0,1)))
         for i in range(3):
            games_grid2=GridLayout()
            games_grid2.cols=3
            games_grid2.rows=1
            game_item_btn=Button(text="Game "+str(i),background_normal="images/game.jpg",size_hint_x=(None))
            game_item_name1=Label(text="Item "+str(i+1),color=(0, 0, 0, 1),pos_hint={"center_x":0.1})
            game_item_name1.font_style="bold"
            game_item_name2=Label(font_size="8dp",text="Item "+str(i+2),color=(0, 0, 0, 1))
            game_item_name1.background_color=(1, 1, 0,1)
            game_item_name2.background_color=(1, 1, 0,1)
            game_item_box=BoxLayout(orientation="vertical",padding=5)
            game_item_box.add_widget(game_item_btn)

            game_item_texts_box=BoxLayout(orientation="vertical",size_hint=(None,0.1),padding=5)
            game_item_texts_box.add_widget(game_item_name1)
            game_item_texts_box.add_widget(game_item_name2)


            #review section box
            review_box=BoxLayout(orientation="horizontal",size_hint=(None,0.1),padding=2)

            rev_btn1 = MDIconButton(
                icon="star" ,
                size_hint_x=(None),
                pos_hint={"center_y":0.5,"center_x":0.1}                
                    )
            rev_btn2=MDIconButton(
                icon="star" ,
                size_hint_x=(None),
                pos_hint={"center_y":0.5,"center_x":0.1}                
        
                    )
            rev_btn3 =  MDIconButton(
                icon="star" ,
                size_hint_x=(None),
                pos_hint={"center_y":0.5,"center_x":0.1}                
        
                    )
            rev_btn4 = MDIconButton(
                icon="star",
                size_hint_x=(None),
                pos_hint={"center_y":0.5,"center_x":0.1}                

                    )
            rev_btn5 =  MDIconButton(
                icon="star" ,
                size_hint_x=(None),
                pos_hint={"center_y":0.5,"center_x":0.1}                

                    )
            review_box.add_widget(rev_btn1)
            review_box.add_widget(rev_btn2)
            review_box.add_widget(rev_btn3)
            review_box.add_widget(rev_btn4)
            review_box.add_widget(rev_btn5)

            review_box.add_widget(Label(text="FREE",pos_hint={"right":0.8},color=(0,0,0,1)))

            game_item_box.add_widget(game_item_texts_box)
            game_item_box.add_widget(review_box)

            games_grid2.add_widget(game_item_box)  
         

         self.gameScreen.gamesBoxLayout.add_widget(seeMoreButton)
         self.gameScreen.gamesBoxLayout.add_widget(games_grid)
         self.gameScreen.gamesBoxLayout.add_widget(Label(text="New + Updated Games",pos_hint={"center_x":0.2},color=(0,0,0,1)))
         self.gameScreen.gamesBoxLayout.add_widget(games_grid2)
      
         
         return screenManager
         
     def click_contact_handler(self, onelinelistitem):
         screenManager.current='chatScreen'
         print('click:', onelinelistitem.text)

     def click_message_handler(self, onelinelistitem):
         
         self.notifyMessageScreen.ids.notifyMessageScreenBreadCrumb.text="Rewards->Notifications->"+onelinelistitem.text
         self.notifyMessageScreen.ids.notifyMessageScreenDate.text=datetime.date.today().ctime()
         self.notifyMessageScreen.ids.notifyMessageScreenMessage.text="The values for the calendar date can be represented via the date class. So also the ......"
         screenManager.current='notifyMessageScreen'
         print('click:', onelinelistitem.text)

     def add_screens(self):
         screenManager.add_widget(self.loginScreen)
         screenManager.add_widget(self.welcomeScreen)
         screenManager.add_widget(self.notifyMessageListScreen)
         screenManager.add_widget(self.notifyMessageScreen)
         screenManager.add_widget(self.mailInboxScreen)
         screenManager.add_widget(self.searchScreen)
         screenManager.add_widget(self.gameScreen)
         screenManager.add_widget(self.chatContactsScreen)
         screenManager.add_widget(self.chatScreen)
        

def isLoggedIn():
    try:
        store.get('credentials')['username']
    except KeyError:
        username = ""
    else:
        username = store.get('credentials')['username']
    if username:
        return True
    else:
        return

    

main=MainApp()
runTouchApp(main.run())