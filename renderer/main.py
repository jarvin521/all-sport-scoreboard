from PIL import Image, ImageFont, ImageDraw, ImageSequence
import os
if os.name == 'nt':  # 'nt' means Windows
    from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions, graphics
else:  # Assume Linux
    from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from utils import center_text
from calendar import month_abbr
from datetime import datetime, timedelta
import time as t
import debug
import os
import unicodedata

GAMES_REFRESH_RATE = 900.0

class MainRenderer:
    def __init__(self, matrix, data):
        self.matrix = matrix
        self.data = data
        self.canvas = matrix.CreateFrameCanvas()
        self.width = 64
        self.height = 64
        # Create a new data image.
        self.image = Image.new('RGB', (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)
        # Load the fonts
        self.font = ImageFont.truetype("fonts/score_large.otf", 16)
        self.font_mini = ImageFont.truetype("fonts/LcdSolid-VPzB.ttf", 8)
        self.font_micro = ImageFont.truetype("fonts/04B_03B_.TTF", 6)
    
    def __all_games_final(self):
        for game in self.data.games:
            if game['state'] != 'post':
                return False
        return True
    
    def render(self):
        while True:
            self.starttime = t.time()
            self.data.get_current_date()
            self.__render_game()

    def __render_game(self):
        while True:
            # Check if all games are final
            if self.__all_games_final():
                self.data.needs_refresh = False

            # If we need to refresh the overview data, do that
            if self.data.needs_refresh:
                self.data.refresh_games()

            # Draw the current game
            self.__draw_game(self.data.current_game())

            # Set the refresh rate
            refresh_rate = self.data.config.scrolling_speed
            t.sleep(refresh_rate)
            endtime = t.time()
            time_delta = endtime - self.starttime
            rotate_rate = self.__rotate_rate_for_game(self.data.current_game())

            # If we're ready to rotate, let's do it
            if time_delta >= rotate_rate:
                self.starttime = t.time()
                #self.data.needs_refresh = True

                if self.__should_rotate_to_next_game(self.data.current_game()):
                    self.data.advance_to_next_game()

                if endtime - self.data.games_refresh_time >= GAMES_REFRESH_RATE:
                    self.data.refresh_games()

                if self.data.needs_refresh:
                    self.data.refresh_games()

    def __rotate_rate_for_game(self, game):
        rotate_rate = self.data.config.rotation_rates_live
        if game['state'] == 'pre':
            rotate_rate = self.data.config.rotation_rates_pregame
        if game['state'] == 'post':
            rotate_rate = self.data.config.rotation_rates_final
        return rotate_rate

    def __should_rotate_to_next_game(self, game):
        if self.data.config.rotation_enabled == False:
            return False
        else:
            return True

    def __draw_game(self, game):
        time = datetime.now()
        gametime = datetime.strptime(game['date'], "%Y-%m-%dT%H:%MZ")
        debug.info(game['name'])
        # Trying to add some Golf to the scoreboard
        if game['sport'] == 'golf':
            if time < gametime and game['state'] == 'pre':
                debug.info('Golf State')
                self._draw_pre_golf(game)
            elif game['stateDetail'] == 'Postponed':
                debug.info('Postponed')
                self._draw_postponed(game)
            else:
                self._draw_live_golf(game)
        else:
            if time < gametime and game['state'] == 'pre':
                debug.info('Pre-Game State')
                self._draw_pregame(game)
            elif game['state'] == 'post':
                if game['stateDetail'] == 'Postponed':
                    debug.info('Postponed')
                    self._draw_postponed(game)
                else:
                    debug.info('Final State')
                    self._draw_post_game(game)
            else:
                debug.info('Live State, checking every 5s')
                if game['league'] == 'mlb' or game['sport'] == 'baseball':
                    self._draw_live_baseball(game)
                else:
                    self._draw_live_game(game)
        #debug.info('ping render_game')

    def _draw_pregame(self, game):
        # Clear the canvas by creating a blank image
        self.image = Image.new('RGB', (self.width, self.height), (0, 0, 0))  # Black background
        self.draw = ImageDraw.Draw(self.image)

        time = datetime.now()
        gamedatetime = self.data.get_gametime()
        if gamedatetime.day == time.day:
            date_text = 'TODAY'
        else:
            if os.name == 'nt':
                date_text = gamedatetime.strftime('%#m/%#d')  # Windows
            else:
                date_text = gamedatetime.strftime('%-m/%-d') # Mac
        if os.name == 'nt':
            gametime = gamedatetime.strftime("%#I:%M %#p")  # Windows
        else:
            gametime = gamedatetime.strftime("%-I:%M %p") # Mac
            

        # Center the game time on screen.
        date_pos = center_text(self.font_mini.getbbox(date_text)[2], 32) + 1
        gametime_pos = center_text(self.font_mini.getbbox(gametime)[2], 32) + 1

        # Draw the text on the Data image.
        self.draw.text((date_pos, 0), date_text, font=self.font_mini)
        self.draw.multiline_text((gametime_pos, 6), gametime, fill=(255, 255, 255), font=self.font_mini, align="center")
        self.draw.text((26, 15), 'VS', font=self.font)

        # self.draw.text((1, 3), f"O/v {game['overUnder']}", font=self.font_micro, fill=(0, 255, 0))
        # self.draw.text((46, 3), f"{game['hometeam']} {game['spread']}", font=self.font_micro, fill=(0, 255, 0))

        # Put the data on the canvas
        self.canvas.SetImage(self.image, 0, 0)

        # TEMP Open the logo image file
        away_team_logo_path = 'logos/{}/{}.png'.format(game['league'], game['awayteam'])
        home_team_logo_path = 'logos/{}/{}.png'.format(game['league'], game['hometeam'])
        default_logo_path = 'logos/scoreboard/Missing.png'

        if os.path.exists(away_team_logo_path):
            away_team_logo = Image.open(away_team_logo_path).resize((16, 16), Image.BOX)
        else:
            away_team_logo = Image.open(default_logo_path).resize((16, 16), Image.BOX)

        if os.path.exists(home_team_logo_path):
            home_team_logo = Image.open(home_team_logo_path).resize((16, 16), Image.BOX)
        else:
            home_team_logo = Image.open(default_logo_path).resize((16, 16), Image.BOX)
        
        # Calculate x-positions for the logos
        logo_width = 16
        away_logo_x = (self.width // 3 - logo_width) // 2
        home_logo_x = 2 * (self.width // 3) + (self.width // 3 - logo_width) // 2

        # Put the images on the canvas
        self.canvas.SetImage(away_team_logo.convert("RGB"), away_logo_x, 14)
        self.canvas.SetImage(home_team_logo.convert("RGB"), home_logo_x, 14)

        # Add a basketball or football to the top right corner to differentiate between college games
        if game['league'] == 'ncaa':
            sport_logo = Image.open('logos/scoreboard/{}.png'.format(game['sport'])).resize((8, 8), Image.BOX)
            self.canvas.SetImage(sport_logo.convert("RGB"), 55, 1)

        # Load the canvas on screen.
        self.canvas = self.matrix.SwapOnVSync(self.canvas)
        # Refresh the Data image.
        self.image = Image.new('RGB', (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)

    def _draw_live_baseball(self, game):
        # Clear the canvas
        self.image = Image.new('RGB', (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)

        homescore = game['homescore']
        awayscore = game['awayscore']
        print("home: ", homescore, "away: ", awayscore)

        if "Top" in game['stateDetail']:
            quarter = f"T{game['quarter']}"
            quarter_position = 25
        else:
            quarter = f"B{game['quarter']}"
            quarter_position = 26
        # Image for the bases; could definitely be better code here
        if not game['1b'] and not game['2b'] and not game['3b']:
            bases = Image.open('logos/scoreboard/Bases_0.png').resize((32, 24), Image.BOX)
        elif game['1b'] and not game['2b'] and not game['3b']:
            bases = Image.open('logos/scoreboard/Bases_1.png').resize((32, 24), Image.BOX)
        elif not game['1b'] and game['2b'] and not game['3b']:
            bases = Image.open('logos/scoreboard/Bases_2.png').resize((32, 24), Image.BOX)
        elif not game['1b'] and not game['2b'] and  game['3b']:
            bases = Image.open('logos/scoreboard/Bases_2.png').resize((32, 24), Image.BOX)
        elif game['1b'] and game['2b'] and not game['3b']:
            bases = Image.open('logos/scoreboard/Bases_12.png').resize((32, 24), Image.BOX)
        elif game['1b'] and not game['2b'] and game['3b']:
            bases = Image.open('logos/scoreboard/Bases_13.png').resize((32, 24), Image.BOX)
        elif not game['1b'] and game['2b'] and game['3b']:
            bases = Image.open('logos/scoreboard/Bases_23.png').resize((32, 24), Image.BOX)
        elif game['1b'] and game['2b'] and game['3b']:
            bases = Image.open('logos/scoreboard/Bases_123.png').resize((32, 24), Image.BOX)
        elif game['1b'] and not game['2b'] and game['3b']:
            bases = Image.open('logos/scoreboard/Bases_13.png').resize((32, 24), Image.BOX)
        else:
            bases = Image.open('logos/scoreboard/Bases_0.png').resize((32, 24), Image.BOX)
        # Image for the count
        if game['balls'] == 0:
            balls = Image.open('logos/scoreboard/Balls_0.png').resize((9, 3), Image.BOX)
        elif game['balls'] == 1:
            balls = Image.open('logos/scoreboard/Balls_1.png').resize((9, 3), Image.BOX)
        elif game['balls'] == 2:
            balls = Image.open('logos/scoreboard/Balls_2.png').resize((9, 3), Image.BOX)
        elif game['balls'] == 3:
            balls = Image.open('logos/scoreboard/Balls_3.png').resize((9, 3), Image.BOX)
        elif game['balls'] == 4:
            balls = Image.open('logos/scoreboard/Balls_3.png').resize((9, 3), Image.BOX)
        else:
            balls = Image.open('logos/scoreboard/Balls_0.png').resize((9, 3), Image.BOX)
        if game['strikes'] == 0:
            strikes = Image.open('logos/scoreboard/Strikes_0.png').resize((6, 3), Image.BOX)
        elif game['strikes'] == 1:
            strikes = Image.open('logos/scoreboard/Strikes_1.png').resize((6, 3), Image.BOX)
        elif game['strikes'] == 2:
            strikes = Image.open('logos/scoreboard/Strikes_2.png').resize((6, 3), Image.BOX)
        elif game['strikes'] == 3:
            strikes = Image.open('logos/scoreboard/Strikes_2.png').resize((6, 3), Image.BOX)
        else:
            strikes = Image.open('logos/scoreboard/Strikes_0.png').resize((9, 3), Image.BOX)
        if game['outs'] == 0:
            outs = Image.open('logos/scoreboard/Outs_0.png').resize((6, 3), Image.BOX)
        elif game['outs'] == 1:
            outs = Image.open('logos/scoreboard/Outs_1.png').resize((6, 3), Image.BOX)
        elif game['outs'] == 2:
            outs = Image.open('logos/scoreboard/Outs_2.png').resize((6, 3), Image.BOX)
        elif game['outs'] == 3:
            outs = Image.open('logos/scoreboard/Outs_2.png').resize((6, 3), Image.BOX)
        else:
            outs = Image.open('logos/scoreboard/Outs_0.png').resize((6, 3), Image.BOX)

        # Set the position of the information on screen.
        homescore = '{0:d}'.format(homescore)
        awayscore = '{0:d}'.format(awayscore)
        home_score_size = self.font.getbbox(homescore)[2]

        # Write the score
        self.draw.multiline_text((quarter_position, 0), quarter, fill=(255, 255, 255), font=self.font, align="center")
        self.draw.multiline_text((6, 19), awayscore, fill=(255, 255, 255), font=self.font, align="center")
        self.draw.multiline_text((59 - home_score_size, 19), homescore, fill=(255, 255, 255), font=self.font, align="center")

        # Put the data on the canvas
        self.canvas.SetImage(self.image, 0, 0)

        # TEMP Open the logo image file
        away_team_logo_path = 'logos/{}/{}.png'.format(game['league'], game['awayteam'])
        home_team_logo_path = 'logos/{}/{}.png'.format(game['league'], game['hometeam'])
        default_logo_path = 'logos/scoreboard/Missing.png'

        if os.path.exists(away_team_logo_path):
            away_team_logo = Image.open(away_team_logo_path).resize((16, 16), Image.BOX)
        else:
            away_team_logo = Image.open(default_logo_path).resize((16, 16), Image.BOX)

        if os.path.exists(home_team_logo_path):
            home_team_logo = Image.open(home_team_logo_path).resize((16, 16), Image.BOX)
        else:
            home_team_logo = Image.open(default_logo_path).resize((16, 16), Image.BOX)

        # Put the image on the canvas
        self.canvas.SetImage(bases.convert("RGB"), 16, 17)
        self.canvas.SetImage(balls.convert("RGB"), 20, 15)
        self.canvas.SetImage(strikes.convert("RGB"), 30, 15)
        self.canvas.SetImage(outs.convert("RGB"), 37, 15)
        
        # Calculate x-positions for the logos
        logo_width = 16
        away_logo_x = (self.width // 3 - logo_width) // 2
        home_logo_x = 2 * (self.width // 3) + (self.width // 3 - logo_width) // 2

        # Put the images on the canvas
        self.canvas.SetImage(away_team_logo.convert("RGB"), away_logo_x, 1)
        self.canvas.SetImage(home_team_logo.convert("RGB"), home_logo_x, 1)

        # Load the canvas on screen.
        self.canvas = self.matrix.SwapOnVSync(self.canvas)

        # Refresh the Data image.
        self.image = Image.new('RGB', (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)

        # Check if the game is over
        if game['state'] == 'post':
            debug.info('GAME OVER')

        # Save the scores.
        self.data.needs_refresh = True

    def _draw_live_game(self, game):
        # Clear the canvas
        self.image = Image.new('RGB', (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)

        homescore = game['homescore']
        awayscore = game['awayscore']
        print("home: ", homescore, "away: ", awayscore)

        # Center the quarter text
        quarter = str(game['quarter'])  # Quarter, half, period, or inning
        quarter_width = self.font.getbbox(quarter)[2]
        quarter_x = (self.width - quarter_width) // 2  # Center horizontally

        # Center the time_period text
        if game['league'] != 'mlb':
            time_period = game['time']
            time_period_width = self.font_mini.getbbox(time_period)[2]
            time_period_x = (self.width - time_period_width) // 2  # Center horizontally
            self.draw.multiline_text((time_period_x, 14), time_period, fill=(255, 255, 255), font=self.font_mini, align="center")

        # Center the away score in the first third
        awayscore = '{0:d}'.format(awayscore)
        awayscore_width = self.font.getbbox(awayscore)[2]
        away_score_x = (self.width // 3 - awayscore_width) // 2

        # Center the home score in the last third
        homescore = '{0:d}'.format(homescore)
        homescore_width = self.font.getbbox(homescore)[2]
        home_score_x = 2 * (self.width // 3) + (self.width // 3 - homescore_width) // 2

        # Draw the quarter text
        self.draw.multiline_text((quarter_x, 0), quarter, fill=(255, 255, 255), font=self.font, align="center")

        # Draw the away score
        self.draw.multiline_text((away_score_x, 19), awayscore, fill=(255, 255, 255), font=self.font, align="center")

        # Draw the home score
        self.draw.multiline_text((home_score_x, 19), homescore, fill=(255, 255, 255), font=self.font, align="center")

        # Put the data on the canvas
        self.canvas.SetImage(self.image, 0, 0)

        # TEMP Open the logo image file
        away_team_logo_path = 'logos/{}/{}.png'.format(game['league'], game['awayteam'])
        home_team_logo_path = 'logos/{}/{}.png'.format(game['league'], game['hometeam'])
        default_logo_path = 'logos/scoreboard/Missing.png'

        if os.path.exists(away_team_logo_path):
            away_team_logo = Image.open(away_team_logo_path).resize((16, 16), Image.BOX)
        else:
            away_team_logo = Image.open(default_logo_path).resize((16, 16), Image.BOX)

        if os.path.exists(home_team_logo_path):
            home_team_logo = Image.open(home_team_logo_path).resize((16, 16), Image.BOX)
        else:
            home_team_logo = Image.open(default_logo_path).resize((16, 16), Image.BOX)

        # Calculate x-positions for the logos
        logo_width = 16
        away_logo_x = (self.width // 3 - logo_width) // 2
        home_logo_x = 2 * (self.width // 3) + (self.width // 3 - logo_width) // 2

        # Put the images on the canvas
        self.canvas.SetImage(away_team_logo.convert("RGB"), away_logo_x, 1)
        self.canvas.SetImage(home_team_logo.convert("RGB"), home_logo_x, 1)

        # Load the canvas on screen
        self.canvas = self.matrix.SwapOnVSync(self.canvas)

        # Refresh the Data image
        self.image = Image.new('RGB', (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)

        # Check if the game is over
        if game['state'] == 'post':
            debug.info('GAME OVER')

        # Save the scores
        self.data.needs_refresh = True

    def _draw_postponed(self, game):
        # Clear the canvas
        self.image = Image.new('RGB', (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)

        # Calculate the position to center the "PPD" text
        final_text_width = self.font_mini.getbbox("PPD")[2]
        final_text_x = (self.width - final_text_width) // 2  # Center horizontally

        # Draw the "FINAL" text
        self.draw.multiline_text((final_text_x, 0), "PPD", fill=(255, 255, 255), font=self.font_mini, align="center")

        # Put the data on the canvas
        self.canvas.SetImage(self.image, 0, 0)

        # TEMP Open the logo image file
        away_team_logo_path = 'logos/{}/{}.png'.format(game['league'], game['awayteam'])
        home_team_logo_path = 'logos/{}/{}.png'.format(game['league'], game['hometeam'])
        default_logo_path = 'logos/scoreboard/Missing.png'
        rain = Image.open('logos/scoreboard/rain.png').resize((16, 16), Image.BOX)

        if os.path.exists(away_team_logo_path):
            away_team_logo = Image.open(away_team_logo_path).resize((16, 16), Image.BOX)
        else:
            away_team_logo = Image.open(default_logo_path).resize((16, 16), Image.BOX)

        if os.path.exists(home_team_logo_path):
            home_team_logo = Image.open(home_team_logo_path).resize((16, 16), Image.BOX)
        else:
            home_team_logo = Image.open(default_logo_path).resize((16, 16), Image.BOX)

        # Calculate x-positions for the logos
        logo_width = 16
        away_logo_x = (self.width // 3 - logo_width) // 2
        home_logo_x = 2 * (self.width // 3) + (self.width // 3 - logo_width) // 2
        rain_x = (self.width - logo_width) // 2  # Center horizontally

        # Put the images on the canvas
        self.canvas.SetImage(rain.convert("RGB"), rain_x, 12)
        self.canvas.SetImage(away_team_logo.convert("RGB"), away_logo_x, 7)
        self.canvas.SetImage(home_team_logo.convert("RGB"), home_logo_x, 7)

        # Load the canvas on screen.
        self.canvas = self.matrix.SwapOnVSync(self.canvas)

        # Refresh the Data image.
        self.image = Image.new('RGB', (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)

    def _draw_post_game(self, game):
        # Clear the canvas
        self.image = Image.new('RGB', (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)

        # Calculate the position to center the "FINAL" text
        final_text_width = self.font_mini.getbbox("FINAL")[2]
        final_text_x = (self.width - final_text_width) // 2  # Center horizontally

        # Draw the "FINAL" text
        self.draw.multiline_text((final_text_x, 0), "FINAL", fill=(255, 255, 255), font=self.font_mini, align="center")

        # Calculate the position to center the score text
        score = '{}-{}'.format(game['awayscore'], game['homescore'])
        score_width = self.font.getbbox(score)[2]
        score_x = (self.width - score_width) // 2  # Center horizontally

        # Draw the score text
        self.draw.multiline_text((score_x, 19), score, fill=(255, 255, 255), font=self.font, align="center")

        # Put the data on the canvas
        self.canvas.SetImage(self.image, 0, 0)

        # TEMP Open the logo image file
        away_team_logo_path = 'logos/{}/{}.png'.format(game['league'], game['awayteam'])
        home_team_logo_path = 'logos/{}/{}.png'.format(game['league'], game['hometeam'])
        default_logo_path = 'logos/scoreboard/Missing.png'

        if os.path.exists(away_team_logo_path):
            away_team_logo = Image.open(away_team_logo_path).resize((16, 16), Image.BOX)
        else:
            away_team_logo = Image.open(default_logo_path).resize((16, 16), Image.BOX)

        if os.path.exists(home_team_logo_path):
            home_team_logo = Image.open(home_team_logo_path).resize((16, 16), Image.BOX)
        else:
            home_team_logo = Image.open(default_logo_path).resize((16, 16), Image.BOX)

        # Calculate x-positions for the logos
        logo_width = 16
        away_logo_x = (self.width // 3 - logo_width) // 2
        home_logo_x = 2 * (self.width // 3) + (self.width // 3 - logo_width) // 2

        # Put the images on the canvas
        self.canvas.SetImage(away_team_logo.convert("RGB"), away_logo_x, 3)
        self.canvas.SetImage(home_team_logo.convert("RGB"), home_logo_x, 3)

        # Load the canvas on screen.
        self.canvas = self.matrix.SwapOnVSync(self.canvas)
        # Refresh the Data image.
        self.image = Image.new('RGB', (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)


    def _draw_pre_golf(self, game):
        # Clear the canvas
        self.image = Image.new('RGB', (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)

        gametime = game['date']
        gamedate = datetime.strptime(gametime, "%Y-%m-%dT%H:%MZ")
        if os.name == 'nt':
            date_text = gamedate.strftime('%-m/%-d') # Mac
        else:
            date_text = gamedate.strftime('%#m/%#d')  # Windows
        

        # Calculate the position to center the date text
        date_width = self.font_mini.getbbox(date_text)[2]
        date_x = (64 - date_width) // 2  # Center horizontally

        # Draw the text on the Data image.
        self.draw.text((date_x, 0), date_text, font=self.font_mini)

        # Put the data on the canvas
        self.canvas.SetImage(self.image, 0, 0)

        golf_tournament_logo_path = 'logos/{}/{}.png'.format(game['league'], game['name'])
        default_logo_path = 'logos/scoreboard/Missing.png'
        
        if os.path.exists(golf_tournament_logo_path):
            golf_tournament_logo = Image.open(golf_tournament_logo_path).resize((24, 24), Image.BOX)
        else:
            golf_tournament_logo = Image.open(default_logo_path).resize((24, 24), Image.BOX)
        
        # Calculate the position to center the logo
        logo_x = (64 - 24) // 2  # Center horizontally
        
        # Put the images on the canvas
        self.canvas.SetImage(golf_tournament_logo.convert("RGB"), (logo_x - 1), 8)

        # Load the canvas on screen.
        self.canvas = self.matrix.SwapOnVSync(self.canvas)
        # Refresh the Data image.
        self.image = Image.new('RGB', (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)

    def _draw_live_golf(self, game):
        # Clear the canvas
        self.image = Image.new('RGB', (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)

        # Define fixed x-positions for the columns
        short_name_x = 1
        score_x = 41
        hole_x = 53

        # Draw the tournament name centered at the top in green
        if game['name'] == 'Masters Tournament':
            tournament_name = "The Masters"
        else:
            tournament_name = game['name']
        tournament_width = self.font_mini.getbbox(tournament_name)[2]
        tournament_x = (self.width - tournament_width) // 2  # Center horizontally
        self.draw.text((tournament_x, 3), tournament_name, font=self.font_mini, fill=(0, 255, 0))  # Green color

        # Scroll through all golfers
        total_golfers = len(game['leader_scores'])
        golfers_per_screen = 3  # Number of golfers to display at a time
        scroll_delay = 8.0  # Delay in seconds between scrolls

        for start_index in range(0, total_golfers, golfers_per_screen):
            # Clear the canvas for each scroll frame
            self.image = Image.new('RGB', (self.width, self.height))
            self.draw = ImageDraw.Draw(self.image)

            # Draw the tournament name again
            self.draw.text((tournament_x, 0), tournament_name, font=self.font_mini, fill=(0, 255, 0))

            # Display a subset of golfers
            for i, leader in enumerate(game['leader_scores'][start_index:start_index + golfers_per_screen]):
                # Extract golfer details
                short_name = leader['golfer']
                if leader['score'] == 'E':
                    score = "E"
                else:
                    score = f"{int(leader['score']):+d}"
                hole_number = leader['hole']
                today_score = leader['today_score']

                # Process the short_name to trim the last name to 4 letters
                if " " in short_name:
                    first_name, last_name = short_name.split(" ", 1)
                    last_name = last_name[:5]  # Trim the last name to 4 letters
                    short_name = f"{first_name} {last_name}"
                    short_name = unicodedata.normalize('NFKD', short_name).encode('ASCII', 'ignore').decode('ASCII')

                # Calculate the y-position for each golfer (spacing by 6 pixels)
                y_position = 10 + i * 6

                # Draw the golfer's short name, score, and hole number
                self.draw.text((short_name_x, y_position), short_name, font=self.font_mini, fill=(255, 255, 255))
                self.draw.text((score_x, y_position), score, font=self.font_mini, fill=(255, 255, 255))
                if game['state'] == 'post':
                    self.draw.text((hole_x, y_position), str(today_score), font=self.font_mini, fill=(255, 255, 255))
                else:
                    self.draw.text((hole_x, y_position), str(hole_number), font=self.font_mini, fill=(255, 255, 255))

            # Update the canvas
            self.canvas.SetImage(self.image, 0, 0)
            self.canvas = self.matrix.SwapOnVSync(self.canvas)

            # Add a delay to control scrolling speed
            if start_index + golfers_per_screen < total_golfers:
                t.sleep(scroll_delay)
    