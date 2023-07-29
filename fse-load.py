'''
ICS3U FSE
By: Alan Bui and Elsie Wang

This game features minigames that are very similar to UnderTale, Fruit Ninja, and Geometry dash.
The classes used will be named based on these games.

Classes were learned from https://www.w3schools.com/python/python_classes.asp
File I/O was learned from https://www.w3schools.com/python/python_file_handling.asp

'''
from pygame import *
from random import *
from math import *
from tkinter import *
from tkinter import filedialog
import tkinter.messagebox

font.init()
root=Tk()
root.withdraw()
init()

def quitGame(): #Function that returns True/False for if the user wants to exit the game after being prompted
    return tkinter.messagebox.askyesno(title="Khroma", message="Are you sure you want to exit?") #idea from: https://docs.python.org/3/library/tkinter.messagebox.html

width,height=1000,600
screen=display.set_mode((width,height))
RED=(255,0,0)
GREY=(127,127,127)
BLACK=(0,0,0)
BLUE=(0,0,255)
GREEN=(0,255,0)
YELLOW=(255,255,0)
WHITE=(255,255,255)

#sets window title to "Khroma"
display.set_caption("Khroma")

def loadImage(filename, w, h): #function to return an image given the filename with width w and height h
    img = image.load("FSE-images/"+filename).convert_alpha() #takes image from the filename in folder FSE-images
    img = transform.scale(img, (w, h)) #scales the image
    return img

def blitText(fontType, string, x, y, color): #function to blit a string on the screen at (x, y) given the color and font type
    txtPic = fontType.render(string, 1, color) #generates a picture of the text
    screen.blit(txtPic, (x, y)) #blits the text

def dist(x1, x2, y1, y2): #function to return the distance between two points using the distance formula
    return sqrt((x2-x1)**2 + ((y2-y1)**2))

def loadGame(fname, mainPlayer):
    data = open(fname) #opens text file
    lis = [] 
    for i in range(2): #appends info to lis
        lis.append(int(data.readline().strip("\n")))

    startMusic.stop() #stops the start screen music
    mainMusic.play(loops = -1) #starts the main game music which will loop forever

    mainPlayer.map_num = lis[0]
    mainPlayer.lvl_num = lis[1]
    mainPlayer.x = 5 #starts player on the start of the path
    mainPlayer.y = 130
    
    for i in range(5): #appends the levels beat from the file into mainPlayer.lvls_beat
        mainPlayer.lvls_beat.append([int(i) for i in data.readline().strip("\n").split()])

    return mainPlayer

mainRunning=True
myClock = time.Clock()

curScreen = "Start" #which screen the player is currently on

#Initialize fonts
mainFont = font.SysFont("COMIC SANS MS", 40)
fruitFont = font.SysFont("MS GOTHIC", 40)

#Initialize the images
backRect = Rect(10,10,50,50) #Rect to exit the level
backimg = loadImage("backrect.png", 50,50)
startScreen = loadImage("Khroma.png", 1000,600)
saveRect = Rect(945,5, 50,50)

loadingPics = []
for i in range(1,16): #loop to append all of the loading screen images to loadingPics
    loadingPics.append(loadImage("loading"+str(i)+".png", width, height))

def loadingScreen(spd): #function for the loading screen given the speed spd
    for i in range(15): #loops through each image and pauses for spd milliseconds 
        screen.blit(loadingPics[i], (0,0))
        time.wait(spd)
        display.flip()

#Initialize main music
startMusic = mixer.Sound("FSE-sound/startmusic.mp3")
mainMusic = mixer.Sound("FSE-sound/mainmusic.mp3")

############################################################################################################

#Initialize geo music

lvl_music1 = mixer.Sound("FSE-sound/geolvl1.mp3")
lvl_music2 = mixer.Sound("FSE-sound/geolvl4.mp3")
lvl_music3 = mixer.Sound("FSE-sound/geolvl5.mp3")
bossmusic = mixer.Sound("FSE-sound/bosslvl.mp3")

##################################################

#Initialize geo images

progressbar = loadImage("status bar.png", 200,20)
filledbar = loadImage("filled bar.png", 200,20)
geolvl1pic = loadImage("geolvl1.png",22000,600)
geolvl2pic = loadImage("geolvl2.png",22000,600)
geolvl3pic = loadImage("geolvl3.png",22000,600)
geolvl4pic = loadImage("geolvl4.png",22000,600)
geoplayerpic = loadImage("blob2.png", 50,50)

geoimgs = [geolvl1pic, geolvl2pic, geolvl3pic, geolvl4pic]

class GeoLevel: #class which has the properties of a "Geometry dash" level
    def __init__(self, speed, layout, fullscreen, plats, spikes, spdbumps, length, music):
        self.spd = speed #How fast the screen will move
        self.grid = layout #2D list imported from file which stores where the spikes and platforms are
        self.fullscreen = fullscreen #Image of the level
        self.plats = plats #List of Rects for where the platforms are
        self.spikes = spikes #List of Rects for where the spikes are
        self.spdbumps = spdbumps #List of where the speed will increase
        self.length = length #Length of the level
        self.music = music #Music played during the level

class geoWorld: #Geometry dash class with functions so Geometry dash levels will play
    def __init__(self):
        return

    def makeScreen(): #Function to take a 2D list and append platforms (represented by 1) to the platforms list and spikes(represented by 2) to the spikes list

        for i in range(len(grid)): #Nested for loops check through everything in the 2D list
            for k in range(len(grid[i])):
                if grid[i][k] == 1: #If it is a platform
                    platforms.append(Rect(k*50,i*50,50,1)) #Add to the platforms list
                    spikes.append(Rect(k*50,i*50+50,50,1)) #Adds the bottom of the platform as a "spike" so the user dies if they hit their head on the bottom of a platform
                    
                elif grid[i][k] == 2: #If it is a spike
                    spikes.append(Rect(k*50,i*50,50,50)) #Add to the spikes list

    def onPlatforms(cur, platforms, pX, pY): #function to check if (pX, pY) is on a platform

        if pY == 450: #Checks if on the floor
            return True
        
        for rects in platforms[1:]: #For all the platforms in the platforms list except the main floor
            if rects.collidepoint((pX+cur, pY+50)) or rects.collidepoint((pX+cur+50, pY+50)): #If the player is on top of the platform, return True
                return True

            if rects[0] > pX+cur+100: #Since the platforms are in sorted order, and this platform is in front of the player, we can stop our search here because there can't possibly be any platforms the player is on
                return False #Returns False 

        return False 

    def onSpike(cur, spikes, pX, pY): #function to check if the player is touching a spike

        for spike in spikes: #Goes through all the spikes in the spikelist
            if Rect(pX+cur,pY,50,50).colliderect(spike): #If the player collides with a spike, returns True
                return True
            if spike[0] > pX+cur+100: #Since the spikes are in sorted order, and this spike is in front of the player, we can stop our search here because there can't possibly be any spike the player is touching
                return False
            
        return False

    def drawScene(cur, fullScreen, length, pX, pY): #function to draw the level
        global win

        try: #Tries to screenshot the big image of the map
            newScreen = fullScreen.subsurface(cur,0,1000,600).copy()
            screen.blit(newScreen, (0,0))

        except: 
            1

        screen.blit(geoplayerpic, (pX, pY))
        screen.blit(progressbar, (400,30)) #blits frame of progress bar
        screen.blit(filledbar.subsurface(0,0,min(200,cur/length*200), 20), (400,30))#blits filled in progress bar
        screen.blit(backimg, (10,10))

    def playLevel(L): #Function for actually playing the level
        global win, curScreen, mainRunning
        music = L.music
        music.play() #plays music

        #Initialize variables for convenience
        spd = L.spd
        platforms = L.plats
        spikes = L.spikes
        fullScreen = L.fullscreen
        grid = L.grid
        spdbumps = L.spdbumps
        length = L.length
        pX = 400
        pY = 450
        
        jumpSpd = 220
        cur = 0 #Starting the level, the player is at distance 0
        oldY = 402
        
        myClock = time.Clock()
        
        
        running = 1
        while running:
            mx,my = mouse.get_pos()
            mb = mouse.get_pressed()
            
            for evt in event.get():
                if evt.type==QUIT: 
                    if quitGame(): #If the player quits the game
                        mainRunning = False #mainRunning is False will tell the program to quit
                        return #stops playing the level

                    else:
                        music.stop() #stops the current music
                        geoWorld.playLevel(L) #starts the level from the beginning
                        return 
                    
                if evt.type == MOUSEBUTTONUP:
                    if mb[0] and backRect.collidepoint((mx,my)): #If the player is trying to exit the game
                        curScreen = "Loading" #Goes back to the loading screen
                        music.stop() #stops playing music
                        return
                               
            keys = key.get_pressed()
            if keys[UP] and geoWorld.onPlatforms(cur, platforms, pX, pY): #If the player is trying to jump (by pressing SPACE) and they are on a platform
                jumpSpd = 10 #Gives them "jumping mode"
                oldY = pY-50 #Sets the Y when your jump starts to pY-50

            if jumpSpd < 210: #If the player is going up
                jumpSpd+=5 #Increases how far along the parabola the player is
                pY = int(oldY-((-3/200)*(jumpSpd**2) + (3*jumpSpd))) #Uses jumping formula (a parabola/quadratic) to figure out how high the player should be

            for i in range(15): #For loop for gravity           
                if geoWorld.onPlatforms(cur, platforms, pX, pY): #If the player is on a platform, no more jumping or falling should happen
                    jumpSpd = 220
                    break
                pY += 1

            pY = min(pY, 450) #Makes sure the player is always at least on the floor and doesn't fall below

            geoWorld.drawScene(cur, fullScreen, length, pX, pY) #Draws the scene
            
            if geoWorld.onSpike(cur, spikes, pX, pY): #If the player touches a spike
                music.stop() #stops current music 
                geoWorld.playLevel(L) #restarts the level
                return

            if cur >= length: #The level is won
                win = True
                curScreen = "Game" #returns to the main game and win = True indicates the level was won
                return

            cur += spd #Moves the screen but makes it look like the player is moving
            for bump in spdbumps: #This only applies to World 4, Level 3
                if cur >= bump[0]: #If the player just passed the bump
                    spd = bump[1] #Changes the speed accordingly
            display.flip()
            myClock.tick(60)

allgeomaps = open("geomaps-test.txt") #Opens file with all the Geometry dash maps that we created
LEVELs = [[] for i in range(4)] #List which will stor the layouts for the 4 levels

for n in range(4): #Loop to append the data from the file into the list LEVELs
    for i in range(12):
        LEVELs[n].append([int(k) for k in allgeomaps.readline().strip("\n").split()])
        
allgeomaps.close() #Closes allgeomaps

geosounds = [lvl_music1, lvl_music2, lvl_music3, bossmusic] #list of the music for the levels
            
geolvls = [] #list to store the levels from this world
lengths = [8500,11500,21000,15000] #lengths of the levels

for i in range(3): #Creates the levels and appends to the geolvls list

    platforms = [Rect(0,495,21500,200)] #initializes the floor as a platform
    spikes = []
    grid = LEVELs[i]
    geoWorld.makeScreen() #calls the function to add platforms to the platforms list and spikes to the spikes list
    platforms.sort()
    spikes.sort()
    geolvls.append(GeoLevel(6+(i*2), LEVELs[i], geoimgs[i], platforms, spikes, [], lengths[i], geosounds[i]))

platforms = [Rect(0,495,21500,200)]
spikes = []
grid = LEVELs[3]
geoWorld.makeScreen()
platforms.sort()
spikes.sort()
geolvls.append(GeoLevel(6, LEVELs[3], geoimgs[3], platforms, spikes, [[4900, 8],[9800, 10]], 15000, geosounds[3]))

UP = K_SPACE #keybinds SPACE to jump
pX = 400; pY = 450 #X and Y values for the player in geometry dash

####################################################################################################################################################################

#Initialize images
apple = loadImage("blue_gem.png", 100,100)
banana = loadImage("green_gem.png", 100,100)
pear = loadImage("red_gem.png", 100,100)
bomb = loadImage("bomb.png", 100,100)
fruitPics = [bomb, banana, pear, apple, apple, pear, banana]
fruitlvlbg = loadImage("Fruit Ninja Level.png", 1000,600)
heart = loadImage("heart.png", 50,50)
emptyheart = loadImage("empty heart.png", 50,50)

class fruit: #each fruit object has the following properties
    def __init__(self, pic, x, y, Type):
        self.pic = pic #picture of the fruit
        self.x = x #x coordinate of the picture
        self.y = y #t coordinate of the picture
        self.Type = Type #Type of fruit, namely if it's a bomb (0) or not (anything else)

class fruitLevel: 
    def __init__(self, num, fallspd, spawnspd, cap, winscore, music):
        self.num = num #level number
        self.fallspd = fallspd #how fast the fruit will fall
        self.spawnspd = spawnspd #changing this value increases/decreases the probability of a new fruit being spawned, so on average, a higher spawnspd results in higher spawn rate of fruit
        self.cap = cap #maximum amount of fruit allowed on the screen at a time
        self.winscore = winscore #score needed to beat the level
        self.music = music #music to be played during the level

class fruitNinja: #class for the functions to actually play the level
    def __init__(self):
        1
        
    def randFruit(lvl): #function that returns a random fruit object
        if lvl == 1: #if the level is 1, there are no bombs
            return fruit(choice(fruitPics[1:]),randint(100, 900), randint(0, 50), 1)
        else:
            isbomb = randint(0, 1000)%len(fruitPics) #if isbomb has a value of 0, it's a bomb, otherwise it's a random other fruit 
            return fruit(fruitPics[isbomb], randint(100,900), randint(0,50), isbomb)

    def drawScene(fruits, score, lives, towin): #function to draw the screen
        screen.blit(fruitlvlbg, (0,0))
        for item in fruits: #loops through all the fruit in the fruits list and blits the picture at the location of the picture
            screen.blit(item.pic, (item.x, item.y))

        blitText(fruitFont, str(score)+"/"+str(towin), 930,10, GREEN) #displays score

        for i in range(3, 0, -1): #loops and displays a red heart for every life the player has life, and an empty heart for every life the player has lost in this level
            if lives >= i:
                screen.blit(heart, (820+((3-i)*60), 540))
            else:
                screen.blit(emptyheart, (820+((3-i)*60), 540))

        screen.blit(backimg, (10,10))

        display.flip()

    def makeFruit(fruits, lvl): #function to create new fruit
        numFruits = randint(0,1) #adds extra randomness so the level isn't too overwhelming with a lot of fruit being spawned

        for i in range(numFruits): 
            fruits.append(fruitNinja.randFruit(lvl)) #adds a new fruit to the list

    def interactions(clicking, fruits, x,y, spd): #function for the interactions such as clicking on a fruit or a fruit falling to the bottom
        #this function returns a list of all the fruit that are on the screen
        
        global score, lives 
        newLis = [] #list that will store all the fruits that are on the screen 
        for item in fruits: 
            item.y += spd #Makes the item fall
            RECT = Rect(item.x, item.y, 100, 100) #hitbox of the item
            Type = item.Type #0 for bomb, anything else is not a bomb

            if clicking:
                try:
                    if RECT.collidepoint((x, y)) and screen.get_at((x,y)) != fruitlvlbg.get_at((x, y)): #if the player is clicking on a fruit, checks if the color is not the background color
                        if not Type: #If the player clicked a bomb, they lose a life
                            lives -= 1

                        else: #The player has clicked on a fruit, so their score increases by one and this fruit is NOT added to newLis (it is gone now)
                            score += 1

                    else:
                        if item.y <= 600: #if the fruit is still on the screen, appends it to the list
                            newLis.append(fruit(item.pic, item.x, item.y, item.Type))

                        elif Type: #If the fruit was NOT a bomb and the fruit has hit the bottom, lives decrements
                            lives -= 1
                except:
                    1
            else:
                if item.y <= 600: #if the fruit is still on the screen, appends it to the list
                    newLis.append(fruit(item.pic, item.x, item.y, item.Type))

                elif Type: #If the fruit was NOT a bomb and the fruit has hit the bottom, lives decrements
                    lives -= 1
        
        return newLis

    def playLevel(lvl): #function for actually playing the level
        global lives, score, win, curScreen, mainRunning

        lis = [] #list of the fruits
        score = 0 #score
        lives = 3 #lives left
        lvl.music.play() #starts the music of this level
        while True:
            if score >= lvl.winscore: #If the player has achieved a large enough score, they win the level
                win = True
                curScreen = "Game"
                break

            elif lives <= 0: #If the player has not enough lives left, they lose the level and the player is taken back to the Loading screen
                win = False
                mainMusic.play()
                curScreen = "Lose"
                break

            mx,my=mouse.get_pos()
            mb=mouse.get_pressed()
            
            for evt in event.get():
                if evt.type==QUIT:
                    if quitGame(): #if the player wants to quit and confirmed they want to quit
                        mainRunning = False 
                        return #ends the level; the game will terminate shortly after

                    else:
                        lvl.music.stop() #restarts the level
                        fruitNinja.playLevel(lvl)
                        return

                if evt.type == MOUSEBUTTONUP:

                    if mb[0] and backRect.collidepoint((mx,my)): #If the player is trying to exit the game
                        curScreen = "Loading" #Goes back to the loading screen
                        lvl.music.stop() #stops playing music
                        return

            rng = randint(1, 100) #random number
            if rng < lvl.spawnspd: #if the randomly selected number is < lvl.spawnspd and 
                if len(lis) < lvl.cap: #if the limit to number of fruits allowed at a time is not exceeded
                    fruitNinja.makeFruit(lis, lvl.num) #calls fruitNinja.makeFruit() to potentially add new fruit to the list

            fruitNinja.drawScene(lis, score, lives, lvl.winscore) #draws the screen

            lis = fruitNinja.interactions(mb[0], lis, mx, my, lvl.fallspd) #The list of fruit is what is returned from fruitNinja.interactions() function

            display.flip()
        lvl.music.stop()

fruitmusic = mixer.Sound("FSE-sound/fruitlvl1.mp3")
LEVEL1 = fruitLevel(1, .22, 10, 10, 50,fruitmusic)
LEVEL2 = fruitLevel(2, .21, 10, 10, 30,fruitmusic)
LEVEL3 = fruitLevel(3, .21, 10, 20, 50,fruitmusic)
LEVEL4 = fruitLevel(4, .22, 10, 30, 99,fruitmusic)
fruitlvls = [LEVEL1, LEVEL2, LEVEL3, LEVEL4] #list containing the fruitNinja levels

####################################################################################################################################################################
bullets = []
playerPos = [400, 300]
bulletpic = loadImage("bullet2.png", 30,30)
undertale_bg = loadImage("undertale bg.png", 1000,600)
undertale_player = loadImage("undertale_player.png", 20, 20)

class bullet:
    def __init__(self, x, y, speed, endx, endy): #initializes the values of the bullets

        self.x = x #x coordinate of the center of the bullet
        self.y = y #y coordinate of the center of the bullet
        self.speed = speed #speed the bullet travels
        if x == width or y == 600: #If the bullet starts at the bottom or on the right side
            self.speed *= -1 #allows the bullet to move from bottom to top or from right to left
        self.endx = endx #x coordinate where the bullet's path ends
        self.endy = endy #y coordinate where the bullet's path ends
        try: #calculates using slope formula
            slope = (endy-y)/(endx-x)
        except: #in case of division by 0 error, sets the slope to 0
            slope = 0
        self.slope = slope     

class UnderTaleLevel: #class for each level in this world
    def __init__(self, name, maxb, length, music):
        self.name = name #name of the level 
        self.maxb = maxb #max bullets on the screen at a time
        self.length = length #length of the level
        self.music = music #music to be played during the level
            
class UnderTale:
    def __init__(self):
        1

    def drawScene(): #function to draw the screen 
        global bullets
        screen.blit(undertale_bg, (0,0))
        for b in bullets: #for all the bullets in the bullets list, draws them
            screen.blit(bulletpic, (b.x-15, b.y-15))
            
        screen.blit(undertale_player, (playerPos[0]-10, playerPos[1]-10)) #displays player
        screen.blit(backimg, (10,10)) #displays background image

    def makeBullets(level, curTime): #function to append bullets to the bullets list depending on the level 
        global bullets
        
        if level == "level1": #Only vertically (up and down) moving bullets
            x = randint(0,width) #random starting x point
            y = choice([0,600])#starts at the top or bottom
            bullets.append(bullet(x, y , randint(5,10), x, abs(y-height))) #adds a new bullet to the list
            
        elif level == "level2": #Only horizontally (left and right) moving bullets
            y = randint(0,600) #random starting y coordinate
            x = choice([0,width]) #starts on the far left or far right side
            bullets.append(bullet(x, y , randint(5,10), abs(x-width), y)) 

        elif level == "level3": #Bullets have a defined slope or are vertically moving bullets
            r = randint(0,1) #Randomly variable to decide if it should be vertically moving (and coming from the bottom or the top) 
            if r: #With a theoretical 50% chance of happening, a vertical moving bullet is added to the list by calling the function for vertically moving bullets only
                UnderTale.makeBullets("level1", curTime)
                
            x = choice([0, width]) #random x coordinate
            
            if x == 0: #if starting on the left side
                dx = width #destination x coordinate is on the right side
                dy = randint(0,600) #end y is random
                y = randint(0,600) #starting y is random
                
            elif x == width: #if starting on the right side
                dx = 0 #destination x coordinate is on the left side
                dy = randint(0,600) #end y is random
                y = randint(0,600) #starting y is random
                
            if bullet(x, y , 5, dx, dy).slope != 0: #makes sure the slope is defined and then if so, appends the new bullet to the list of bullets
                bullets.append(bullet(x, y , 5, dx, dy))

        elif level == "level4": #Bullets are of all types
            #Decides which kind of bullets will spawn depending on how long the player has been in the level for
            if curTime < 11000:
                r = 1
            elif curTime <22000:
                r = 2
            elif curTime < 37000:
                r = randint(1, 2)
            else:
                r = 3

            UnderTale.makeBullets("level"+str(r), curTime) #creates bullets

    def stage(level): #function for interactions which returns a list of all the bullets that are on the screen
        global bullets
        nxtbullets = [] #list which will store the bullets on the screen

        keys = key.get_pressed() #list of the pressed keys

        #w moves the player up, d moves the player right, s moves the player down, a moves the player left
        #The player does not go out of bounds
        if keys[K_a]: 
            playerPos[0] = max(playerPos[0]-5, 5)
        if keys[K_d]:
            playerPos[0] = min(playerPos[0]+5, width-5)
        if keys[K_w]:
            playerPos[1] = max(playerPos[1]-5, 5)
        if keys[K_s]:
            playerPos[1] = min(playerPos[1]+5, height-5)
        
        for b in bullets:
            if b.y > 600 or b.y < 0 or b.x > width or b.x < 0: #if the bullet is off the screen, do NOT add it to the new list
                continue
            
            if b.y != b.endy or b.x != b.endx: #if the bullet has not reached its destination yet
                
                if b.x != b.endx: #if the x coordinate is not where it should be:
                    b.x += b.speed #increases the x coordinate by b.speed (which can be negative)
                    b.y = b.x*b.slope + (b.endy - (b.slope * b.endx)) #recalculates the y coordinate using the slope
                    
                elif b.y != b.endy: #if the bullet has reached the correct x coordinate, but not the correct y coordinate (e.g. vertically moving bullet)
                    b.y += b.speed #increases the y coordinate by b.speed
                    try: #tries to recalculate the value of b.x using the slope
                        b.x = ((b.y - (b.endy - (b.slope * b.endx)))/b.slope)
                    except: #b.x does NOT need recalculation if the slope is 0 (e.g. vertical lines have a slope of 0 so it's easier to catch them)
                        1
                        
                if not(b.y == b.endy and b.x == b.endx): #if after the recalculation of the location of the bullet, the bullet still hasn't reached its destination, we add it to the list
                    nxtbullets.append(b)

            if dist(b.x, playerPos[0], b.y, playerPos[1]) < 20: #If the player is touching a bullet, losing function

                return False #Tells the playLevel function that the player lost

        return nxtbullets

    def playLevel(lvl): #function for playing the UnderTale-style levels
        global bullets, curScreen, mainRunning
        bullets = [] #list of bullets
        cur = 0 #stores an int which will increment until the level is over (player dies or cur >= lvl.length)
        lvl.music.play() #starts the music for this level
        playerPos[0] = 500; playerPos[1] = 300
        timer = time.Clock()
        timer.tick(60)
        
        running = True
        while running:
            
            if cur >= lvl.length: #if the player has survived for the entire level, they win
                lvl.music.stop() #stops music
                curScreen = "Game" #sets the curScreen back to the main Game
                return True #returns True, indicating a win

            mx,my=mouse.get_pos()
            mb = mb=mouse.get_pressed()
            
            for evt in event.get():
                if evt.type==QUIT:
                    if quitGame():
                        mainRunning = False
                        return False
                    else:
                        lvl.music.stop()
                        return UnderTale.playLevel(lvl)
                        
                if evt.type == MOUSEBUTTONUP:

                    if mb[0] and backRect.collidepoint((mx,my)): #If the player is trying to exit the game
                        curScreen = "Loading" #Goes back to the loading screen
                        lvl.music.stop() #stops playing music
                        return False
                    
            if len(bullets) < lvl.maxb: #if the limit for number of bullets was not reached yet, adds new bullets
                UnderTale.makeBullets(lvl.name, cur)
            
            bullets = UnderTale.stage(lvl.name) #checks interactions and bullets = current bullets on the screen
            if not bullets: #If the stage function returned False (the player was hit)
                lvl.music.stop() #stops music
                curScreen = "Lose" #sets the screen to the losing screen 
                return False #returns False, indicating a loss

            UnderTale.drawScene() #draws the current screen

            timer.tick(60)
            cur += timer.get_time()
           
            display.flip()
            
        lvl.music.stop()
        curScreen = "Game"
        return False

undertale_music1 = mixer.Sound("FSE-sound/underlvl1.mp3")
undertale_music2 = mixer.Sound("FSE-sound/underlvl2.mp3")
undertale_music3 = mixer.Sound("FSE-sound/underlvl3.mp3")
undertale_music4 = mixer.Sound("FSE-sound/underlvl4.mp3")

UL1 = UnderTaleLevel("level1", 10, 35000, undertale_music1)
UL2 = UnderTaleLevel("level2", 10, 46000, undertale_music2)
UL3 = UnderTaleLevel("level3", 12, 61000, undertale_music3)
UL4 = UnderTaleLevel("level4", 15, 63500, undertale_music4)
UnderTalelvls = [UL1, UL2, UL3, UL4] #list to store all undertale levels

###################################################################################################################################################################

class Player: #class with properties that the main player has
    def __init__(self, map_num, lvl_num, x, y, lvls_beat, frame_row, frame_col):
        self.map_num = map_num #Current map number
        self.lvl_num = lvl_num #Current level number
        self.x = x #x coordinate
        self.y = y #y coordinate
        self.lvls_beat = lvls_beat #2-d list that stores the levels that have been beaten
        self.frame_row = frame_row
        self.frame_col = frame_col

 
mainPlayer = Player(1,1,1,1,[],0,0) #mainPlayer with a bunch of properties which will change when the game is loaded
win = False #the player has not won a game

#Initializing images

geolvl_pic1 = loadImage("Geo1.png", width, height)
geolvl_pic2 = loadImage("Geo2.png", width, height)
geolvl_pic3 = loadImage("Geo3.png", width, height)
talelvl_pic1 = loadImage("Tale1.png", width, height)
talelvl_pic2 = loadImage("Tale2.png", width, height)
talelvl_pic3 = loadImage("Tale3.png", width, height)
fruitlvl_pic1 = loadImage("Fruit1.png", width, height)
fruitlvl_pic2 = loadImage("Fruit2.png", width, height)
fruitlvl_pic3 = loadImage("Fruit3.png", width, height)

bosslvl_pic1 = loadImage("Boss1.png", width, height)
bosslvl_pic2 = loadImage("Boss2.png", width, height)
bosslvl_pic3 = loadImage("Boss3.png", width, height)

rulespics = [[0,0,0,0], #2D list for the pictures of the loading screens 
            [0,fruitlvl_pic1,fruitlvl_pic2,fruitlvl_pic3],
            [0,talelvl_pic1,talelvl_pic2,talelvl_pic3],
            [0,geolvl_pic1,geolvl_pic2,geolvl_pic3],
            [0,bosslvl_pic1, bosslvl_pic2, bosslvl_pic3]]

select1 = loadImage("select1.png", width, height)
select2 = loadImage("select2.png", width, height)
select3 = loadImage("select3.png", width, height)
select4 = loadImage("select4.png", width, height)
selectpics = [select1, select2, select3, select4] #list of arrows for the starting Screen

frames = [] #list of images for when the main player is walking around
for i in range(4):
    frames.append([])
    for j in range(i*3+1, i*3+4):
        frames[-1].append(loadImage("player%02d.png" %j, 50, 50))

mainGame_bg1 = loadImage("World1.png", 1000, 600)
mainGame_bg2 = loadImage("World2.png", 1000, 600)
mainGame_bg3 = loadImage("World3.png", 1000, 600)
mainGame_bg4 = loadImage("World4.png", 1000, 600)

yellow_frg1 = loadImage("yellow_frag1.png", 50, 50)
yellow_frg2 = loadImage("yellow_frag2.png", 50, 50)
yellow_frg3 = loadImage("yellow_frag3.png", 50, 50)
blue_frg1 = loadImage("blue_frag1.png", 50, 50)
blue_frg2 = loadImage("blue_frag2.png", 50, 50)
blue_frg3 = loadImage("blue_frag3.png", 50, 50)
red_frg1 = loadImage("red_frag1.png", 50, 50)
red_frg2 = loadImage("red_frag2.png", 50, 50)
red_frg3 = loadImage("red_frag3.png", 50, 50)
gems = [[red_frg1,red_frg2,red_frg3], [blue_frg1,blue_frg2,blue_frg3], [yellow_frg1,yellow_frg2,yellow_frg3]]

save_button = loadImage("save_btn.png", 50, 50)
creditsImg = loadImage("credits.png", 1000,600)
storyImg = loadImage("story.png", 1000,600)

geoWin = loadImage("win_geo.png", 1000,600)
taleWin = loadImage("win_tale.png", 1000,600)
fruitWin = loadImage("win_fruit.png", 1000,600)

winScreens = [[fruitWin, fruitWin, fruitWin],
              [taleWin, taleWin, taleWin],
              [geoWin, geoWin, geoWin],
              [fruitWin, taleWin, geoWin]]

losepic = loadImage("lose.png", width, height)
enemies = [Rect(160, 80, 70, 70), Rect(495, 424, 60, 60), Rect(750, 230, 45, 60)] #Rects of the enemies

finalPics = []
for i in range(1,9):
    finalPics.append(loadImage("final000"+str(i)+".png", width, height))


def finalScreen(spd):
    
    for i in range(8): #loops through all pictures in finalPics and blits them after pausing for spd milliseconds
        screen.blit(finalPics[i], (0,0))
        time.wait(spd)
        display.flip()

    fname = filedialog.asksaveasfilename(defaultextension=".txt")
    try:
        userData = open(fname, "w")

    except:
        userData = open("newPlayer.txt", "w")

    userData.write(str(4)+"\n")
    userData.write(str(1)+"\n")
    userData.write("0000\n")
    userData.write("0111\n")
    userData.write("0111\n")
    userData.write("0111\n")
    userData.write("0111\n")
    


startMusic.play(loops = -1) #plays music that will loop for the starting screen

def play(): #Depending on what world the player is in, calls the necessary playLevel function
    global win
    
    if mainPlayer.map_num == 3: 
        geoWorld.playLevel(geolvls[mainPlayer.lvl_num-1])
        
    elif mainPlayer.map_num == 4:
        if mainPlayer.lvl_num == 3:
            geoWorld.playLevel(geolvls[3])

        if mainPlayer.lvl_num == 2:
            if UnderTale.playLevel(UnderTalelvls[3]):
                win = True

        if mainPlayer.lvl_num == 1:
            fruitNinja.playLevel(fruitlvls[3])

    elif mainPlayer.map_num == 1:
        fruitNinja.playLevel(fruitlvls[mainPlayer.lvl_num-1])

    if mainPlayer.map_num == 2:
        if UnderTale.playLevel(UnderTalelvls[mainPlayer.lvl_num-1]):
            win = True

def winningScreen():
    global curScreen
    
    screen.blit(winScreens[mainPlayer.map_num-1][mainPlayer.lvl_num-1], (0,0)) #displays the winning screen based on what level was beat
    screen.blit(backimg, (10,10)) #displays back arrow
    display.flip()
    
    while True:
        mx,my = mouse.get_pos()
        mb = mouse.get_pressed()

        for evt in event.get(): 
            if evt.type==QUIT:
                if quitGame():
                    mainRunning = False
                    return 

        if mb[0] and backRect.collidepoint((mx,my)): #If the player hits the back arrow, finishes the winning screen and returns to the regular game
            curScreen = "Game"
            return

while mainRunning:
    for evt in event.get():
        if evt.type==QUIT:
            if quitGame():
                mainRunning = False
                break

        if curScreen == "Game":
            mx,my = mouse.get_pos() #gets the mouse position
            mb = mouse.get_pressed() #gets what mouse button is being pressed
            keys = key.get_pressed() #gets what key is being pressed

            if keys[K_d]: #if 'd' is being pressed...
                prev = False #'prev' is set to False, this makes sure that when player gets out of loading screen, it doesn't automatically send player back to loading screen after going back to the 'Game' portion
                mainPlayer.frame_row = 1 #the row of the frame is 1
                if mainPlayer.x >= 950: #makes sure player cannot go outside of bounds
                    mainPlayer.x = 950
                mainPlayer.x += 5 #moves player 5 pixels right
            elif keys[K_a]: #same as previous, except moves left and row of frame is 2
                prev = False
                mainPlayer.frame_row = 2
                if mainPlayer.x <= 0:
                    mainPlayer.x = 0
                mainPlayer.x -= 5
            elif keys[K_w]: #same as previous, except moves up and row of frame is 3
                prev = False
                mainPlayer.frame_row = 3
                if mainPlayer.y <= 0:
                    mainPlayer.y = 0
                mainPlayer.y -= 5
            elif keys[K_s]: #same as previous, except moves down and row of frame is 0
                prev = False
                mainPlayer.frame_row = 0
                if mainPlayer.y >= 550:
                    mainPlayer.y = 550
                mainPlayer.y += 5
            else:
                mainPlayer.frame_col = 0 #if player is idle (not pressing keys), column is 0, sets to idle position
                mainPlayer.frame_col -= (1/3) #subtracts 1/3 from where it adds in next line, since it is idle

            mainPlayer.frame_col += (1/3) #increases the frame column by 1/3 each iteration, slows down the walking animation

            if mainPlayer.frame_col >= 3: #if the frame column is larger or equal to three...
                mainPlayer.frame_col = 1 #it loops back to first frame

            if enemies[0].colliderect(Rect(mainPlayer.x, mainPlayer.y, 50, 50)) and prev == False: #if enemy is colliding with player's hitbox and 'prev' is False...
                mainPlayer.lvl_num = 1 #the level is set to 1 (enemy is the first one corresponding to level 1)
                curScreen = "Loading" #the current screen is set to loading
            if enemies[1].colliderect(Rect(mainPlayer.x, mainPlayer.y, 50, 50)) and prev == False: #same as previous, except for different enemy
                mainPlayer.lvl_num = 2
                curScreen = "Loading"
            if enemies[2].colliderect(Rect(mainPlayer.x, mainPlayer.y, 50, 50)) and prev == False:
                mainPlayer.lvl_num = 3
                curScreen = "Loading"

            if mainPlayer.x == 950 and mainPlayer.lvls_beat[mainPlayer.map_num] == [0,1,1,1]: #checks if all levels for the map are beaten
                loadingScreen(100) #runs loading animation 
                mainPlayer.x = 5 #starts player on the start of the path
                mainPlayer.y = 130
                mainPlayer.lvl_num = 1 #resets level to 1
                mainPlayer.map_num += 1 #increases map by 1
                if mainPlayer.map_num == 5:
                    finalScreen(100)
                    curScreen = "ENDOFGAME"

            if mainPlayer.x <= 1: #If the player wants to go back to a previous world,
                if mainPlayer.map_num > 1: #checks if there is a world to go back to
                    mainPlayer.map_num -= 1
                    mainPlayer.x = 20
                    
               
    if not mainRunning:
        break
    
    mx,my=mouse.get_pos()
    mb=mouse.get_pressed()
        
      
    if curScreen == "Start": #If it's the starting screen
        screen.blit(startScreen, (0,0))
        
        newGameRect = Rect(195,210,635,80)
        loadRect = Rect(195,290,635,80)
        storyRect = Rect(195,370, 635, 80)
        creditsRect = Rect(195, 450, 635, 80)

        options = [newGameRect,loadRect,storyRect,creditsRect]
        
        for i in range(4):
            if options[i].collidepoint((mx,my)):
                screen.blit(selectpics[i], (0,0))
                break

        if mb[0] and loadRect.collidepoint((mx,my)):
            fname = filedialog.askopenfilename() #gets file from user
            try: #if the file is valid
                extension = fname[fname.rfind("."):]
                if extension != ".txt": #only excepts .txt files
                    print("Bad extension")
                    
                else:
                    loadGame(fname, mainPlayer)
                    loadingScreen(200)

                    curScreen = "Game" #Changes the curScreen to the main Game

            except: #Tells the user invalid data (likely cause of this error is fname being an empty string)
                print("Invalid data")

        if mb[0] and newGameRect.collidepoint((mx,my)):
            fname = "startnew.txt" #startnew.txt contains the information of a new player
            loadGame(fname, mainPlayer) #loads all the details into mainPlayer
            loadingScreen(200)
            curScreen = "Game" #Changes the curScreen to the main Game

        if mb[0] and creditsRect.collidepoint((mx,my)):
            curScreen = "Credits" #Changes the curScreen to the Credits page

        if mb[0] and storyRect.collidepoint((mx,my)):
            curScreen = "Story" #Changes the curScreen to the story page

    if curScreen == "Credits":
        screen.blit(creditsImg, (0,0)) #displays credits
        screen.blit(backimg, (10,10)) #displays back arrow
        if mb[0] and backRect.collidepoint((mx,my)): #if the player clicks the back icon, takes them back to the start screen
            curScreen = "Start"

    if curScreen == "Story":
        screen.blit(storyImg, (0,0)) #displays credits
        screen.blit(backimg, (10,10)) #displays back arrow
        if mb[0] and backRect.collidepoint((mx,my)): #if the player clicks the back icon, takes them back to the start screen
            curScreen = "Start"

    if curScreen == "Game": #In the main Game
        if mainPlayer.map_num == 1:
            screen.blit(mainGame_bg1, (0,0))
        elif mainPlayer.map_num == 2:
            screen.blit(mainGame_bg2, (0,0))
        elif mainPlayer.map_num == 3:
            screen.blit(mainGame_bg3, (0,0))
        elif mainPlayer.map_num == 4:
            screen.blit(mainGame_bg4, (0,0))

        for i in range(3): #displays the completion of the world in the form of a gem 
            if mainPlayer.lvls_beat[mainPlayer.map_num][i+1] == 1:
                screen.blit(gems[min(mainPlayer.map_num - 1, 2)][i], (10,10))
                
           
        
        screen.blit(save_button, (945, 5))

        if mb[0] and saveRect.collidepoint((mx,my)): #if the user tries to save the game
            fname = filedialog.asksaveasfilename(defaultextension=".txt") #gets a file from the user to write the data to

            try:
                userData = open(fname, "w") #opens the file to write all the data

            except:
                fname = "newPlayer.txt"
                userData = open(fname, "w")

            #writes all necessary information about the player to the file
            userData.write(str(mainPlayer.map_num)+"\n")
            userData.write(str(mainPlayer.lvl_num)+"\n")
            for i in range(5):
                line = ""
                for k in range(4):
                    line += str(mainPlayer.lvls_beat[i][k]) + " "
                userData.write(line+"\n")
            userData.close()

        blitText(mainFont, "MAP: "+str(mainPlayer.map_num), 10, 540, WHITE) #Displays to the player which map number they are on                
        screen.blit((frames[mainPlayer.frame_row][int(mainPlayer.frame_col)]), (mainPlayer.x, mainPlayer.y)) #blits the character onto screen with corresponding frame depending on column and row, blits where the character is currently

    if curScreen == "Lose":
        screen.blit(losepic, (0,0))
        replayRect = Rect(640,535,340,50) #rect to replay the level
        rulesRect = Rect(25,530,195,45) #rect to go back to the rules page
      
        if replayRect.collidepoint((mx,my)): 
            if mb[0]:
                mainMusic.stop()
                loadingScreen(100)
                play() #plays the level again
               

        if rulesRect.collidepoint((mx,my)): #goes back to the rules page
            if mb[0]:
                curScreen = "Loading"
                
    if curScreen == "Loading": #Rules screen
        screen.blit(rulespics[mainPlayer.map_num][mainPlayer.lvl_num], (0,0)) #displays the loading image of the level
        playRect = Rect(720,485,270,100) #rect to start the game
        prevRect = Rect(10,10,50,50) #rect to go back
        if playRect.collidepoint((mx,my)): 
            if mb[0]: #if the player clicks on the start button 
                win = False #the player hasn't won the level yet
                curScreen = "Playing"
                mainMusic.stop()
                loadingScreen(100)
                play() #This function will depending on what world the player is in, calls the necessary playlevel function
                    
                if win:
                    mainPlayer.lvls_beat[mainPlayer.map_num][mainPlayer.lvl_num] = 1 #mark that the player has won this level and can advance to the next one
                    winningScreen()
                mainMusic.play(loops = -1)

        if prevRect.collidepoint((mx,my)):
            if mb[0]:
                prev = True
                curScreen = "Game" #Goes back to the main Game screen
            
    display.flip()
    myClock.tick(60)
            
quit()
