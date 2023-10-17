import pygame
from random import choice, randrange
import pygame_gui
import random
from .Screens import Screens

from scripts.utility import get_text_box_theme, scale, generate_sprite
from scripts.clan import Clan
from scripts.cat.cats import create_example_cats, Cat
from scripts.cat.pelts import Pelt
from scripts.cat.names import names
from re import sub
from scripts.game_structure.image_button import UIImageButton, UISpriteButton, UITextBoxTweaked
from scripts.game_structure.game_essentials import game, MANAGER
from scripts.patrol.patrol import Patrol


class MakeClanScreen(Screens):
    # UI images
    clan_frame_img = pygame.transform.scale(pygame.image.load(
        'resources/images/pick_clan_screen/clan_name_frame.png').convert_alpha(), (432, 100))
    name_clan_img = pygame.transform.scale(pygame.image.load(
        'resources/images/pick_clan_screen/name_clan_light.png').convert_alpha(), (1600, 1400))
    leader_img = pygame.transform.scale(pygame.image.load(
        'resources/images/pick_clan_screen/choose cat.png').convert_alpha(), (1600, 1400))
    leader_img_dark = pygame.transform.scale(pygame.image.load(
        'resources/images/pick_clan_screen/choose cat dark.png').convert_alpha(), (1600, 1400))
    deputy_img = pygame.transform.scale(pygame.image.load(
        'resources/images/pick_clan_screen/deputy_light.png').convert_alpha(), (1600, 1400))
    medic_img = pygame.transform.scale(pygame.image.load(
        'resources/images/pick_clan_screen/med_light.png').convert_alpha(), (1600, 1400))
    clan_img = pygame.transform.scale(pygame.image.load(
        'resources/images/pick_clan_screen/clan_light.png').convert_alpha(), (1600, 1400))
    bg_preview_border = pygame.transform.scale(
        pygame.image.load("resources/images/bg_preview_border.png").convert_alpha(), (466, 416))
    
    your_name_img = pygame.transform.scale(pygame.image.load(
        'resources/images/pick_clan_screen/your name.png').convert_alpha(), (1600, 1400))
    your_name_img_dark = pygame.transform.scale(pygame.image.load(
        'resources/images/pick_clan_screen/your name dark.png').convert_alpha(), (1600, 1400))


    # This section holds all the information needed
    game_mode = 'expanded'  # To save the users selection before conformation.
    clan_name = ""  # To store the clan name before conformation
    leader = None  # To store the clan leader before conformation
    deputy = None
    med_cat = None
    members = []
    elected_camp = None
    your_cat = None

    # Holds biome we have selected
    biome_selected = None
    selected_camp_tab = 1
    selected_season = None
    # Camp number selected
    camp_num = "1"
    # Holds the cat we have currently selected.
    selected_cat = None
    # Hold which sub-screen we are on
    sub_screen = 'name clan'
    # Holds which ranks we are currently selecting.
    choosing_rank = None
    # To hold the images for the sections. Makes it easier to kill them
    elements = {}
    tabs = {}

    def __init__(self, name=None):
        super().__init__(name)
        self.rolls_left = game.config["clan_creation"]["rerolls"]
        self.menu_warning = None

    def screen_switches(self):
        # Reset variables
        self.game_mode = 'expanded'
        self.clan_name = ""
        self.selected_camp_tab = 1
        self.biome_selected = None
        self.selected_season = "Newleaf"
        self.choosing_rank = None
        self.leader = None  # To store the Clan leader before conformation
        self.deputy = None
        self.med_cat = None
        self.members = []
        self.clan_size = "medium"
        
        self.custom_cat = None
        self.elements = {}
        self.pname="SingleColour"
        self.length="short"
        self.colour="WHITE"
        self.white_patches=None
        self.eye_color="BLUE"
        self.eye_colour2=None
        self.tortiebase=None
        self.tortiecolour=None
        self.pattern=None
        self.tortiepattern=None
        self.vitiligo=None
        self.points=None
        self.accessory=None
        self.paralyzed=False
        self.opacity=100
        self.scars=None
        self.tint="none"
        self.skin="BLACK"
        self.white_patches_tint="none"
        self.kitten_sprite=None
        self.adol_sprite=None
        self.adult_sprite=None
        self.senior_sprite=None
        self.para_adult_sprite=None
        self.reverse=False
        self.accessories=[]

        # Buttons that appear on every screen.
        self.menu_warning = pygame_gui.elements.UITextBox(
            'Note: going back to main menu resets the generated cats.',
            scale(pygame.Rect((50, 50), (1200, -1))),
            object_id=get_text_box_theme("#text_box_22_horizleft"), manager=MANAGER
        )
        self.main_menu = UIImageButton(scale(pygame.Rect((50, 100), (306, 60))), "", object_id="#main_menu_button"
                                       , manager=MANAGER)
        create_example_cats()
        self.open_name_clan()

    def handle_event(self, event):
        if self.sub_screen == 'customize cat':
            self.handle_customize_cat_event(event)
        elif event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.main_menu:
                self.change_screen('start screen')
            if self.sub_screen == 'name clan':
                self.handle_name_clan_event(event)
            elif self.sub_screen == 'choose name':
                self.handle_choose_name_event(event)
            elif self.sub_screen == 'choose leader':
                self.handle_choose_leader_event(event)
            elif self.sub_screen == 'choose camp':
                self.handle_choose_background_event(event)
            elif self.sub_screen == 'saved screen':
                self.handle_saved_clan_event(event)
        
        elif event.type == pygame.KEYDOWN and game.settings['keybinds']:
            if self.sub_screen == 'name clan':
                self.handle_name_clan_key(event)
            elif self.sub_screen == 'choose camp':
                self.handle_choose_background_key(event)
            elif self.sub_screen == 'saved screen' and (event.key == pygame.K_RETURN or event.key == pygame.K_RIGHT):
                self.change_screen('start screen')

    def handle_name_clan_event(self, event):
        if event.ui_element == self.elements["random"]:
            self.elements["name_entry"].set_text(choice(names.names_dict["normal_prefixes"]))
        elif event.ui_element == self.elements["reset_name"]:
            self.elements["name_entry"].set_text("")
        elif event.ui_element == self.elements['next_step']:
            new_name = sub(r'[^A-Za-z0-9 ]+', "", self.elements["name_entry"].get_text()).strip()
            if not new_name:
                self.elements["error"].set_text("Your Clan's name cannot be empty")
                self.elements["error"].show()
                return
            if new_name.casefold() in [clan.casefold() for clan in game.switches['clan_list']]:
                self.elements["error"].set_text("A Clan with that name already exists.")
                self.elements["error"].show()
                return
            self.clan_name = new_name
            self.open_choose_leader()
        elif event.ui_element == self.elements['previous_step']:
            self.clan_name = ""
            self.change_screen('start screen')
        elif event.ui_element == self.elements['small']:
            self.elements['small'].disable()
            self.elements['medium'].enable()
            self.elements['large'].enable()
            self.clan_size = "small"
        elif event.ui_element == self.elements['medium']:
            self.elements['small'].enable()
            self.elements['medium'].disable()
            self.elements['large'].enable()
            self.clan_size = "medium"
        elif event.ui_element == self.elements['large']:
            self.elements['small'].enable()
            self.elements['large'].disable()
            self.elements['medium'].enable()
            self.clan_size = "large"
    
    def handle_name_clan_key(self, event):
        if event.key == pygame.K_ESCAPE:
            self.change_screen('start screen')
        elif event.key == pygame.K_LEFT:
            if not self.elements['name_entry'].is_focused:
                self.clan_name = ""
        elif event.key == pygame.K_RIGHT:
            if not self.elements['name_entry'].is_focused:
                new_name = sub(r'[^A-Za-z0-9 ]+', "", self.elements["name_entry"].get_text()).strip()
                if not new_name:
                    self.elements["error"].set_text("Your Clan's name cannot be empty")
                    self.elements["error"].show()
                    return
                if new_name.casefold() in [clan.casefold() for clan in game.switches['clan_list']]:
                    self.elements["error"].set_text("A Clan with that name already exists.")
                    self.elements["error"].show()
                    return
                self.clan_name = new_name
                self.open_choose_leader()
        elif event.key == pygame.K_RETURN:
            new_name = sub(r'[^A-Za-z0-9 ]+', "", self.elements["name_entry"].get_text()).strip()
            if not new_name:
                self.elements["error"].set_text("Your Clan's name cannot be empty")
                self.elements["error"].show()
                return
            if new_name.casefold() in [clan.casefold() for clan in game.switches['clan_list']]:
                self.elements["error"].set_text("A Clan with that name already exists.")
                self.elements["error"].show()
                return
            self.clan_name = new_name
            self.open_choose_leader()

    def handle_choose_leader_event(self, event):
        if event.ui_element in [self.elements['roll1'], self.elements['roll2'], self.elements['roll3'],
                                self.elements["dice"]]:
            self.elements['select_cat'].hide()
            create_example_cats()  # create new cats
            self.selected_cat = None  # Your selected cat now no longer exists. Sad. They go away.
            self.refresh_cat_images_and_info()  # Refresh all the images.
            self.rolls_left -= 1
            if game.config["clan_creation"]["rerolls"] == 3:
                event.ui_element.disable()
            else:
                self.elements["reroll_count"].set_text(str(self.rolls_left))
                if self.rolls_left == 0:
                    event.ui_element.disable()

        elif event.ui_element in [self.elements["cat" + str(u)] for u in range(0, 12)]:
            self.selected_cat = event.ui_element.return_cat_object()
            self.refresh_cat_images_and_info(self.selected_cat)
            self.refresh_text_and_buttons()
        elif event.ui_element == self.elements['select_cat']:
            self.your_cat = self.selected_cat
            self.selected_cat = None
            self.open_name_cat()
        elif event.ui_element == self.elements['previous_step']:
            self.clan_name = ""
            self.open_name_clan()
        elif event.ui_element == self.elements['customize']:
            self.open_customize_cat()
            
    def handle_choose_name_event(self, event):
        if event.ui_element == self.elements['next_step']:
            new_name = sub(r'[^A-Za-z0-9 ]+', "", self.elements["name_entry"].get_text()).strip()
            if not new_name:
                self.elements["error"].set_text("Your cat's name cannot be empty")
                self.elements["error"].show()
                return
            self.your_cat.name.prefix = new_name
            self.open_choose_background()
        elif event.ui_element == self.elements["random"]:
            self.elements["name_entry"].set_text(choice(names.names_dict["normal_prefixes"]))
        elif event.ui_element == self.elements['previous_step']:
            self.selected_cat = None
            self.open_choose_leader()
    
    def handle_create_other_cats(self):
        self.create_example_cats2()
        for cat in game.choose_cats.values():
            if cat.status == "warrior":
                if self.leader is None:
                    self.leader = cat
                elif self.deputy is None:
                    self.deputy = cat
                    cat.status = "deputy"
                elif self.med_cat is None:
                    self.med_cat = cat
                    cat.status = "medicine cat"
                else:
                    self.members.append(cat)
            else:
                self.members.append(cat)
        self.members.append(self.your_cat)
        
    def create_example_cats2(self):
        e = random.sample(range(12), 3)
        not_allowed = ['NOPAW', 'NOTAIL', 'HALFTAIL', 'NOEAR', 'BOTHBLIND', 'RIGHTBLIND', 'LEFTBLIND', 'BRIGHTHEART',
                    'NOLEFTEAR', 'NORIGHTEAR', 'MANLEG']
        c_size = 15
        if self.clan_size == "small":
            c_size = 10
        elif self.clan_size == 'large':
            c_size = 20
        for a in range(c_size):
            if a in e:
                game.choose_cats[a] = Cat(status='warrior', biome=None)
            else:
                r = random.randint(1,60)
                s = "warrior"
                if r > 40:
                    s = "warrior"
                elif r > 30:
                    s = "apprentice"
                elif r > 25:
                    s = "kitten"
                elif r > 20:
                    s = "elder"
                elif r > 15:
                    s = "mediator"
                elif r > 10:
                    s = "mediator apprentice"
                elif r > 5:
                    s = "queen"
                elif r >= 0:
                    s = "queen's apprentice"
                game.choose_cats[a] = Cat(status=s, biome=None)
            if game.choose_cats[a].moons >= 160:
                game.choose_cats[a].moons = choice(range(120, 155))
            elif game.choose_cats[a].moons == 0:
                game.choose_cats[a].moons = choice([1, 2, 3, 4, 5])
    
    def handle_choose_background_event(self, event):
        if event.ui_element == self.elements['previous_step']:
            self.open_choose_leader()
        elif event.ui_element == self.elements['forest_biome']:
            self.biome_selected = "Forest"
            self.selected_camp_tab = 1
            self.refresh_text_and_buttons()
        elif event.ui_element == self.elements['mountain_biome']:
            self.biome_selected = "Mountainous"
            self.selected_camp_tab = 1
            self.refresh_text_and_buttons()
        elif event.ui_element == self.elements['plains_biome']:
            self.biome_selected = "Plains"
            self.selected_camp_tab = 1
            self.refresh_text_and_buttons()
        elif event.ui_element == self.elements['beach_biome']:
            self.biome_selected = "Beach"
            self.selected_camp_tab = 1
            self.refresh_text_and_buttons()
        elif event.ui_element == self.tabs["tab1"]:
            self.selected_camp_tab = 1
            self.refresh_selected_camp()
        elif event.ui_element == self.tabs["tab2"]:
            self.selected_camp_tab = 2
            self.refresh_selected_camp()
        elif event.ui_element == self.tabs["tab3"]:
            self.selected_camp_tab = 3
            self.refresh_selected_camp()
        elif event.ui_element == self.tabs["newleaf_tab"]:
            self.selected_season = "Newleaf"
            self.refresh_text_and_buttons()
        elif event.ui_element == self.tabs["greenleaf_tab"]:
            self.selected_season = "Greenleaf"
            self.refresh_text_and_buttons()
        elif event.ui_element == self.tabs["leaffall_tab"]:
            self.selected_season = "Leaf-fall"
            self.refresh_text_and_buttons()
        elif event.ui_element == self.tabs["leafbare_tab"]:
            self.selected_season = "Leaf-bare"
            self.refresh_text_and_buttons()
        elif event.ui_element == self.elements["random_background"]:
            # Select a random biome and background
            old_biome = self.biome_selected
            possible_biomes = ['Forest', 'Mountainous', 'Plains', 'Beach']
            # ensuring that the new random camp will not be the same one
            if old_biome is not None:
                possible_biomes.remove(old_biome)
            self.biome_selected = choice(possible_biomes)
            if self.biome_selected != 'Plains':
                self.selected_camp_tab = randrange(1, 4)
            else:
                self.selected_camp_tab = randrange(1, 3)
            self.refresh_selected_camp()
            self.refresh_text_and_buttons()
        elif event.ui_element == self.elements['done_button']:
            self.save_clan()
            self.open_clan_saved_screen()
    
    def handle_choose_background_key(self, event):
        if event.key == pygame.K_RIGHT:
            if self.biome_selected is None:
                self.biome_selected = "Forest"
            elif self.biome_selected == "Forest":
                self.biome_selected = "Mountainous"
            elif self.biome_selected == "Mountainous":
                self.biome_selected = "Plains"
            elif self.biome_selected == "Plains":
                self.biome_selected = "Beach"
            self.selected_camp_tab = 1
            self.refresh_text_and_buttons()
        elif event.key == pygame.K_LEFT:
            if self.biome_selected is None:
                self.biome_selected = "Beach"
            elif self.biome_selected == "Beach":
                self.biome_selected = "Plains"
            elif self.biome_selected == "Plains":
                self.biome_selected = "Mountainous"
            elif self.biome_selected == "Mountainous":
                self.biome_selected = "Forest"
            self.selected_camp_tab = 1
            self.refresh_text_and_buttons()
        elif event.key == pygame.K_UP and self.biome_selected is not None:
            if self.selected_camp_tab > 1:
                self.selected_camp_tab -= 1
                self.refresh_selected_camp()
        elif event.key == pygame.K_DOWN and self.biome_selected is not None:
            if self.biome_selected != 'Plains' and self.selected_camp_tab < 3:
                self.selected_camp_tab += 1
                self.refresh_selected_camp()
            elif self.biome_selected == 'Plains' and self.selected_camp_tab < 2:
                self.selected_camp_tab += 1
                self.refresh_selected_camp()
        elif event.key == pygame.K_RETURN:
            self.save_clan()
            self.open_clan_saved_screen()

    def handle_saved_clan_event(self, event):
        if event.ui_element == self.elements["continue"]:
            self.change_screen('camp screen')

    def exit_screen(self):
        self.main_menu.kill()
        self.menu_warning.kill()
        self.clear_all_page()
        self.rolls_left = game.config["clan_creation"]["rerolls"]
        return super().exit_screen()

    def on_use(self):

        # Don't allow someone to enter no name for their clan
        if self.sub_screen == 'name clan':
            if self.elements["name_entry"].get_text() == "":
                self.elements['next_step'].disable()
            elif self.elements["name_entry"].get_text().startswith(" "):
                self.elements["error"].set_text("Clan names cannot start with a space.")
                self.elements["error"].show()
                self.elements['next_step'].disable()
            elif self.elements["name_entry"].get_text().casefold() in [clan.casefold() for clan in
                                                                       game.switches['clan_list']]:
                self.elements["error"].set_text("A Clan with that name already exists.")
                self.elements["error"].show()
                self.elements['next_step'].disable()
                return
            else:
                self.elements["error"].hide()
                self.elements['next_step'].enable()
        elif self.sub_screen == 'choose name':
            if self.elements["name_entry"].get_text() == "":
                self.elements['next_step'].disable()
            elif self.elements["name_entry"].get_text().startswith(" "):
                self.elements["error"].set_text("Your name cannot start with a space.")
                self.elements["error"].show()
                self.elements['next_step'].disable()
            else:
                self.elements["error"].hide()
                self.elements['next_step'].enable()

    def clear_all_page(self):
        """Clears the entire page, including layout images"""
        for image in self.elements:
            self.elements[image].kill()
        for tab in self.tabs:
            self.tabs[tab].kill()
        self.elements = {}

    def refresh_text_and_buttons(self):
        """Refreshes the button states and text boxes"""
        if self.sub_screen == "game mode":
            # Set the mode explanation text
            if self.game_mode == 'classic':
                display_text = self.classic_mode_text
                display_name = "Classic Mode"
            elif self.game_mode == 'expanded':
                display_text = self.expanded_mode_text
                display_name = "Expanded Mode"
            elif self.game_mode == 'cruel':
                display_text = self.cruel_mode_text
                display_name = "Cruel Season"
            else:
                display_text = ""
                display_name = "ERROR"
            self.elements['mode_details'].set_text(display_text)
            self.elements['mode_name'].set_text(display_name)

            # Update the enabled buttons for the game selection to disable the
            # buttons for the mode currently selected. Mostly for aesthetics, and it
            # make it very clear which mode is selected. 
            if self.game_mode == 'classic':
                self.elements['classic_mode_button'].disable()
                self.elements['expanded_mode_button'].enable()
                self.elements['cruel_mode_button'].enable()
            elif self.game_mode == 'expanded':
                self.elements['classic_mode_button'].enable()
                self.elements['expanded_mode_button'].disable()
                self.elements['cruel_mode_button'].enable()
            elif self.game_mode == 'cruel':
                self.elements['classic_mode_button'].enable()
                self.elements['expanded_mode_button'].enable()
                self.elements['cruel_mode_button'].disable()
            else:
                self.elements['classic_mode_button'].enable()
                self.elements['expanded_mode_button'].enable()
                self.elements['cruel_mode_button'].enable()

            # Don't let the player go forwards with cruel mode, it's not done yet.
            if self.game_mode == 'cruel':
                self.elements['next_step'].disable()
            else:
                self.elements['next_step'].enable()
        # Show the error message if you try to choose a child for leader, deputy, or med cat.
        elif self.sub_screen in ['choose leader', 'choose deputy', 'choose med cat']:
            self.elements['select_cat'].show()
        # Refresh the choose-members background to match number of cat's chosen.
        elif self.sub_screen == 'choose members':
            if len(self.members) == 0:
                self.elements["background"].set_image(
                    pygame.transform.scale(
                        pygame.image.load("resources/images/pick_clan_screen/clan_none_light.png").convert_alpha(),
                        (1600, 1400)))
                self.elements['next_step'].disable()
            elif len(self.members) == 1:
                self.elements["background"].set_image(
                    pygame.transform.scale(
                        pygame.image.load("resources/images/pick_clan_screen/clan_one_light.png").convert_alpha(),
                        (1600, 1400)))
                self.elements['next_step'].disable()
            elif len(self.members) == 2:
                self.elements["background"].set_image(
                    pygame.transform.scale(
                        pygame.image.load("resources/images/pick_clan_screen/clan_two_light.png").convert_alpha(),
                        (1600, 1400)))
                self.elements['next_step'].disable()
            elif len(self.members) == 3:
                self.elements["background"].set_image(
                    pygame.transform.scale(
                        pygame.image.load("resources/images/pick_clan_screen/clan_three_light.png").convert_alpha(),
                        (1600, 1400)))
                self.elements['next_step'].disable()
            elif 4 <= len(self.members) <= 6:
                self.elements["background"].set_image(
                    pygame.transform.scale(
                        pygame.image.load("resources/images/pick_clan_screen/clan_four_light.png").convert_alpha(),
                        (1600, 1400)))
                self.elements['next_step'].enable()
                # In order for the "previous step" to work properly, we must enable this button, just in case it
                # was disabled in the next step.
                self.elements["select_cat"].enable()
            elif len(self.members) == 7:
                self.elements["background"].set_image(
                    pygame.transform.scale(
                        pygame.image.load("resources/images/pick_clan_screen/clan_full_light.png").convert_alpha(),
                        (1600, 1400)))
                self.elements["select_cat"].disable()
                self.elements['next_step'].enable()

            # Hide the recruit cat button if no cat is selected.
            if self.selected_cat is not None:
                self.elements['select_cat'].show()
            else:
                self.elements['select_cat'].hide()

        elif self.sub_screen == 'choose camp':
            # Enable/disable biome buttons
            if self.biome_selected == 'Forest':
                self.elements['forest_biome'].disable()
                self.elements['mountain_biome'].enable()
                self.elements['plains_biome'].enable()
                self.elements['beach_biome'].enable()
            elif self.biome_selected == "Mountainous":
                self.elements['forest_biome'].enable()
                self.elements['mountain_biome'].disable()
                self.elements['plains_biome'].enable()
                self.elements['beach_biome'].enable()
            elif self.biome_selected == "Plains":
                self.elements['forest_biome'].enable()
                self.elements['mountain_biome'].enable()
                self.elements['plains_biome'].disable()
                self.elements['beach_biome'].enable()
            elif self.biome_selected == "Beach":
                self.elements['forest_biome'].enable()
                self.elements['mountain_biome'].enable()
                self.elements['plains_biome'].enable()
                self.elements['beach_biome'].disable()

            if self.selected_season == 'Newleaf':
                self.tabs['newleaf_tab'].disable()
                self.tabs['greenleaf_tab'].enable()
                self.tabs['leaffall_tab'].enable()
                self.tabs['leafbare_tab'].enable()
            elif self.selected_season == 'Greenleaf':
                self.tabs['newleaf_tab'].enable()
                self.tabs['greenleaf_tab'].disable()
                self.tabs['leaffall_tab'].enable()
                self.tabs['leafbare_tab'].enable()
            elif self.selected_season == 'Leaf-fall':
                self.tabs['newleaf_tab'].enable()
                self.tabs['greenleaf_tab'].enable()
                self.tabs['leaffall_tab'].disable()
                self.tabs['leafbare_tab'].enable()
            elif self.selected_season == 'Leaf-bare':
                self.tabs['newleaf_tab'].enable()
                self.tabs['greenleaf_tab'].enable()
                self.tabs['leaffall_tab'].enable()
                self.tabs['leafbare_tab'].disable()

            if self.biome_selected is not None and self.selected_camp_tab is not None:
                self.elements['done_button'].enable()

            # Deal with tab and shown camp image:
            self.refresh_selected_camp()

    def refresh_selected_camp(self):
        """Updates selected camp image and tabs"""
        self.tabs["tab1"].kill()
        self.tabs["tab2"].kill()
        self.tabs["tab3"].kill()
        if self.biome_selected == 'Forest':
            self.tabs["tab1"] = UIImageButton(scale(pygame.Rect((190, 360), (308, 60))), "", object_id="#classic_tab"
                                              , manager=MANAGER)
            self.tabs["tab2"] = UIImageButton(scale(pygame.Rect((216, 430), (308, 60))), "", object_id="#gully_tab"
                                              , manager=MANAGER)
            self.tabs["tab3"] = UIImageButton(scale(pygame.Rect((190, 500), (308, 60))), "", object_id="#grotto_tab"
                                              , manager=MANAGER)
        elif self.biome_selected == 'Mountainous':
            self.tabs["tab1"] = UIImageButton(scale(pygame.Rect((222, 360), (308, 60))), "", object_id="#cliff_tab"
                                              , manager=MANAGER)
            self.tabs["tab2"] = UIImageButton(scale(pygame.Rect((180, 430), (308, 60))), "", object_id="#cave_tab"
                                              , manager=MANAGER)
            self.tabs["tab3"] = UIImageButton(scale(pygame.Rect((85, 500), (358, 60))), "", object_id="#crystal_tab"
                                              , manager=MANAGER)
        elif self.biome_selected == 'Plains':
            self.tabs["tab1"] = UIImageButton(scale(pygame.Rect((128, 360), (308, 60))), "", object_id="#grasslands_tab"
                                              , manager=MANAGER, )
            self.tabs["tab2"] = UIImageButton(scale(pygame.Rect((178, 430), (308, 60))), "", object_id="#tunnel_tab"
                                              , manager=MANAGER)
        elif self.biome_selected == 'Beach':
            self.tabs["tab1"] = UIImageButton(scale(pygame.Rect((152, 360), (308, 60))), "", object_id="#tidepool_tab"
                                              , manager=MANAGER)
            self.tabs["tab2"] = UIImageButton(scale(pygame.Rect((130, 430), (308, 60))), "", object_id="#tidal_cave_tab"
                                              , manager=MANAGER)
            self.tabs["tab3"] = UIImageButton(scale(pygame.Rect((140, 500), (308, 60))), "", object_id="#shipwreck_tab"
                                              , manager=MANAGER)

        if self.selected_camp_tab == 1:
            self.tabs["tab1"].disable()
            self.tabs["tab2"].enable()
            self.tabs["tab3"].enable()
        elif self.selected_camp_tab == 2:
            self.tabs["tab1"].enable()
            self.tabs["tab2"].disable()
            self.tabs["tab3"].enable()
        elif self.selected_camp_tab == 3:
            self.tabs["tab1"].enable()
            self.tabs["tab2"].enable()
            self.tabs["tab3"].disable()
        else:
            self.tabs["tab1"].enable()
            self.tabs["tab2"].enable()
            self.tabs["tab3"].enable()

        # I have to do this for proper layering.
        if "camp_art" in self.elements:
            self.elements["camp_art"].kill()
        if self.biome_selected:
            self.elements["camp_art"] = pygame_gui.elements.UIImage(scale(pygame.Rect((350, 340), (900, 800))),
                                                                    pygame.transform.scale(
                                                                        pygame.image.load(
                                                                            self.get_camp_art_path(
                                                                                self.selected_camp_tab)).convert_alpha(),
                                                                        (900, 800)), manager=MANAGER)
            self.elements['art_frame'].kill()
            self.elements['art_frame'] = pygame_gui.elements.UIImage(scale(pygame.Rect(((334, 324), (932, 832)))),
                                                                     pygame.transform.scale(
                                                                         pygame.image.load(
                                                                             "resources/images/bg_preview_border.png").convert_alpha(),
                                                                         (932, 832)), manager=MANAGER)

    def refresh_selected_cat_info(self, selected=None):
        # SELECTED CAT INFO
        if selected is not None:

            if self.sub_screen == 'choose leader':
                self.elements['cat_name'].set_text(str(selected.name))
            else:
                self.elements['cat_name'].set_text(str(selected.name))
            self.elements['cat_name'].show()
            self.elements['cat_info'].set_text(selected.gender + "\n" +
                                               "fur length: " + str(selected.pelt.length) + "\n" +
                                                   str(selected.personality.trait) + "\n" +
                                                   str(selected.skills.skill_string()))
            if selected.permanent_condition:
                self.elements['cat_info'].set_text(selected.gender + "\n" +
                                               "fur length: " + str(selected.pelt.length) + "\n" +
                                                   str(selected.personality.trait) + "\n" +
                                                   str(selected.skills.skill_string()) + "\n" +
                                                   "permanent condition: " + list(selected.permanent_condition.keys())[0])
            self.elements['cat_info'].show()


    def refresh_cat_images_and_info(self, selected=None):
        """Update the image of the cat selected in the middle. Info and image.
        Also updates the location of selected cats. """

        column_poss = [100, 200]

        # updates selected cat info
        self.refresh_selected_cat_info(selected)

        # CAT IMAGES
        for u in range(6):
            if "cat" + str(u) in self.elements:
                self.elements["cat" + str(u)].kill()
            if game.choose_cats[u] == selected:
                self.elements["cat" + str(u)] = self.elements["cat" + str(u)] = UISpriteButton(
                    scale(pygame.Rect((540, 350), (300, 300))),
                    pygame.transform.scale(game.choose_cats[u].sprite, (300, 300)),
                    cat_object=game.choose_cats[u])
            elif game.choose_cats[u] in [self.leader, self.deputy, self.med_cat] + self.members:
                self.elements["cat" + str(u)] = UISpriteButton(scale(pygame.Rect((1300, 250 + 100 * u), (100, 100))),
                                                               game.choose_cats[u].sprite,
                                                               cat_object=game.choose_cats[u], manager=MANAGER)
                self.elements["cat" + str(u)].disable()
            else:
                self.elements["cat" + str(u)] = UISpriteButton(
                    scale(pygame.Rect((column_poss[0], 260 + 100 * u), (100, 100))),
                    game.choose_cats[u].sprite,
                    cat_object=game.choose_cats[u], manager=MANAGER)
        for u in range(6, 12):
            if "cat" + str(u) in self.elements:
                self.elements["cat" + str(u)].kill()
            if game.choose_cats[u] == selected:
                self.elements["cat" + str(u)] = self.elements["cat" + str(u)] = UISpriteButton(
                    scale(pygame.Rect((540, 350), (300, 300))),
                    pygame.transform.scale(game.choose_cats[u].sprite, (300, 300)),
                    cat_object=game.choose_cats[u], manager=MANAGER)
            elif game.choose_cats[u] in [self.leader, self.deputy, self.med_cat] + self.members:
                self.elements["cat" + str(u)] = self.elements["cat" + str(u)] = UISpriteButton(
                    scale(pygame.Rect((540, 400), (300, 300))),
                    pygame.transform.scale(game.choose_cats[u].sprite, (300, 300)),
                    cat_object=game.choose_cats[u], manager=MANAGER)
            else:
                self.elements["cat" + str(u)] = UISpriteButton(
                    scale(pygame.Rect((column_poss[1], 260 + 100 * (u - 6)), (100, 100))),
                    game.choose_cats[u].sprite,
                    cat_object=game.choose_cats[u], manager=MANAGER)
                
    def refresh_cat_images_and_info2(self, selected=None):
        """Update the image of the cat selected in the middle. Info and image.
        Also updates the location of selected cats. """

        column_poss = [100, 200]

        # updates selected cat info
        self.refresh_selected_cat_info(selected)

        # CAT IMAGES
        for u in range(6):
            if game.choose_cats[u] in [self.leader, self.deputy, self.med_cat] + self.members:
                self.elements["cat" + str(u)] = self.elements["cat" + str(u)] = UISpriteButton(
                    scale(pygame.Rect((620, 400), (300, 300))),
                    pygame.transform.scale(game.choose_cats[u].sprite, (300, 300)),
                    cat_object=game.choose_cats[u])

        for u in range(6, 12):
             if game.choose_cats[u] in [self.leader, self.deputy, self.med_cat] + self.members:
                self.elements["cat" + str(u)] = self.elements["cat" + str(u)] = UISpriteButton(
                    scale(pygame.Rect((620, 400), (300, 300))),
                    pygame.transform.scale(game.choose_cats[u].sprite, (300, 300)),
                    cat_object=game.choose_cats[u])
        
    def open_name_cat(self):
        """Opens the name clan screen"""
        
        self.clear_all_page()
        self.elements["leader_image"] = pygame_gui.elements.UIImage(scale(pygame.Rect((700, 400), (200, 200))),
                                                                    pygame.transform.scale(
                                                                        self.your_cat.sprite,
                                                                        (200, 200)), manager=MANAGER)
        if game.settings['dark mode']:
            self.elements['background'] = pygame_gui.elements.UIImage(scale(pygame.Rect((500, 800), (600, 70))),
                                                                  MakeClanScreen.your_name_img_dark, manager=MANAGER)
        else:
            self.elements['background'] = pygame_gui.elements.UIImage(scale(pygame.Rect((500, 800), (600, 70))),
                                                                  MakeClanScreen.your_name_img, manager=MANAGER)

        self.elements['background'].disable()
        
        self.refresh_cat_images_and_info2()
        
        self.sub_screen = 'choose name'
        
        self.elements["random"] = UIImageButton(scale(pygame.Rect((520, 995), (68, 68))), "",
                                                object_id="#random_dice_button"
                                                , manager=MANAGER)

        self.elements["error"] = pygame_gui.elements.UITextBox("", scale(pygame.Rect((506, 1310), (596, -1))),
                                                               manager=MANAGER,
                                                               object_id="#default_dark", visible=False)

        self.elements['previous_step'] = UIImageButton(scale(pygame.Rect((506, 1270), (294, 60))), "",
                                                       object_id="#previous_step_button", manager=MANAGER)
        self.elements['next_step'] = UIImageButton(scale(pygame.Rect((800, 1270), (294, 60))), "",
                                                   object_id="#next_step_button", manager=MANAGER)
        self.elements["name_entry"] = pygame_gui.elements.UITextEntryLine(scale(pygame.Rect((600, 1000), (280, 58)))
                                                                          , manager=MANAGER, initial_text=self.your_cat.name.prefix)
        self.elements["name_entry"].set_allowed_characters(
            list("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_- "))
        self.elements["name_entry"].set_text_length_limit(11)

        if game.settings['dark mode']:
            self.elements["clan"] = pygame_gui.elements.UITextBox("-kit",
                                                              scale(pygame.Rect((820, 1005), (200, 50))),
                                                              object_id="#text_box_30_horizcenter_light",
                                                              manager=MANAGER)
        
        else:
            self.elements["clan"] = pygame_gui.elements.UITextBox("-kit",
                                                              scale(pygame.Rect((820, 1005), (200, 50))),
                                                              object_id="#text_box_30_horizcenter",
                                                              manager=MANAGER)
        


    def open_name_clan(self):
        """Opens the name Clan screen"""
        self.clear_all_page()
        self.sub_screen = 'name clan'

        # Create all the elements.
        self.elements["background"] = pygame_gui.elements.UIImage(scale(pygame.Rect((0, 0), (1600, 1400))),
                                                                  pygame.transform.scale(MakeClanScreen.name_clan_img,
                                                                                         (1600, 1400))
                                                                  , manager=MANAGER)
        self.elements['background'].disable()
        self.elements["random"] = UIImageButton(scale(pygame.Rect((448, 1190), (68, 68))), "",
                                                object_id="#random_dice_button"
                                                , manager=MANAGER)

        self.elements["error"] = pygame_gui.elements.UITextBox("", scale(pygame.Rect((506, 1310), (596, -1))),
                                                               manager=MANAGER,
                                                               object_id="#default_dark", visible=False)

        self.elements['previous_step'] = UIImageButton(scale(pygame.Rect((506, 1270), (294, 60))), "",
                                                       object_id="#previous_step_button", manager=MANAGER)
        self.elements['next_step'] = UIImageButton(scale(pygame.Rect((800, 1270), (294, 60))), "",
                                                   object_id="#next_step_button", manager=MANAGER)
        self.elements['next_step'].disable()
        self.elements["name_entry"] = pygame_gui.elements.UITextEntryLine(scale(pygame.Rect((530, 1195), (280, 58)))
                                                                          , manager=MANAGER)
        self.elements["name_entry"].set_allowed_characters(
            list("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_- "))
        self.elements["name_entry"].set_text_length_limit(11)
        self.elements["clan"] = pygame_gui.elements.UITextBox("-Clan",
                                                              scale(pygame.Rect((750, 1200), (200, 50))),
                                                              object_id="#text_box_30_horizcenter_light",
                                                              manager=MANAGER)
        self.elements["reset_name"] = UIImageButton(scale(pygame.Rect((910, 1190), (268, 60))), "",
                                                    object_id="#reset_name_button", manager=MANAGER)
        
        if game.settings['dark mode']:
            self.elements["clan_size"] = pygame_gui.elements.UITextBox("Clan Size: ",
                                                              scale(pygame.Rect((400, 110), (200, 50))),
                                                              object_id="#text_box_30_horizcenter_light",
                                                              manager=MANAGER)
        else:
            self.elements["clan_size"] = pygame_gui.elements.UITextBox("Clan Size: ",
                                                              scale(pygame.Rect((400, 110), (200, 50))),
                                                              object_id="#text_box_30_horizcenter",
                                                              manager=MANAGER)  
        
        self.elements["small"] = pygame_gui.elements.UIButton(scale(pygame.Rect((600,100), (200, 70))), "Small", object_id="#small_button", manager=MANAGER)
        self.elements["medium"] = pygame_gui.elements.UIButton(scale(pygame.Rect((850,100), (200, 70))), "Medium", object_id="#small_button", manager=MANAGER)
        self.elements["large"] = pygame_gui.elements.UIButton(scale(pygame.Rect((1100,100), (200, 70))), "Large", object_id="#small_button", manager=MANAGER)
        self.elements["medium"].disable()

    def clan_name_header(self):
        self.elements["name_backdrop"] = pygame_gui.elements.UIImage(scale(pygame.Rect((584, 200), (432, 100))),
                                                                     MakeClanScreen.clan_frame_img, manager=MANAGER)
        self.elements["clan_name"] = pygame_gui.elements.UITextBox(self.clan_name + "Clan",
                                                                   scale(pygame.Rect((585, 212), (432, 100))),
                                                                   object_id="#text_box_30_horizcenter_light",
                                                                   manager=MANAGER)

    def open_choose_leader(self):
        """Set up the screen for the choose leader phase. """
        self.clear_all_page()
        self.sub_screen = 'choose leader'

        if game.settings['dark mode']:
            self.elements['background'] = pygame_gui.elements.UIImage(scale(pygame.Rect((500, 1000), (600, 70))),
                                                                  MakeClanScreen.leader_img_dark, manager=MANAGER)
        else:
            self.elements['background'] = pygame_gui.elements.UIImage(scale(pygame.Rect((500, 1000), (600, 70))),
                                                                  MakeClanScreen.leader_img, manager=MANAGER)

        self.elements['background'].disable()
        self.clan_name_header()

        # Roll_buttons
        x_pos = 310
        y_pos = 470
        self.elements['roll1'] = UIImageButton(scale(pygame.Rect((x_pos, y_pos), (68, 68))), "",
                                               object_id="#random_dice_button", manager=MANAGER)
        y_pos += 80
        self.elements['roll2'] = UIImageButton(scale(pygame.Rect((x_pos, y_pos), (68, 68))), "",
                                               object_id="#random_dice_button", manager=MANAGER)
        y_pos += 80
        self.elements['roll3'] = UIImageButton(scale(pygame.Rect((x_pos, y_pos), (68, 68))), "",
                                               object_id="#random_dice_button", manager=MANAGER)

        _tmp = 160
        if self.rolls_left == -1:
            _tmp += 5
        self.elements['dice'] = UIImageButton(scale(pygame.Rect((_tmp, 870), (68, 68))), "",
                                              object_id="#random_dice_button", manager=MANAGER)
        del _tmp
        self.elements['reroll_count'] = pygame_gui.elements.UILabel(scale(pygame.Rect((200, 880), (100, 50))),
                                                                    str(self.rolls_left),
                                                                    object_id=get_text_box_theme(""),
                                                                    manager=MANAGER)

        if game.config["clan_creation"]["rerolls"] == 3:
            if self.rolls_left <= 2:
                self.elements['roll1'].disable()
            if self.rolls_left <= 1:
                self.elements['roll2'].disable()
            if self.rolls_left == 0:
                self.elements['roll3'].disable()
            self.elements['dice'].hide()
            self.elements['reroll_count'].hide()
        else:
            if self.rolls_left == 0:
                self.elements['dice'].disable()
            elif self.rolls_left == -1:
                self.elements['reroll_count'].hide()
            self.elements['roll1'].hide()
            self.elements['roll2'].hide()
            self.elements['roll3'].hide()

        # info for chosen cats:
        if game.settings['dark mode']:
            self.elements['cat_info'] = pygame_gui.elements.UITextBox("", scale(pygame.Rect((880, 450), (230, 250))),
                                                                    visible=False, object_id="#text_box_22_horizleft_spacing_95_dark",
                                                                    manager=MANAGER)
        else:
            self.elements['cat_info'] = pygame_gui.elements.UITextBox("", scale(pygame.Rect((880, 450), (230, 250))),
                                                                    visible=False, object_id=get_text_box_theme("#text_box_22_horizleft_spacing_95"),
                                                                    manager=MANAGER)
        self.elements['cat_name'] = pygame_gui.elements.UITextBox("", scale(pygame.Rect((300, 350), (1000, 110))),
                                                                  visible=False,
                                                                  object_id=get_text_box_theme(
                                                                      "#text_box_30_horizcenter"),
                                                                  manager=MANAGER)

        self.elements['select_cat'] = UIImageButton(scale(pygame.Rect((706, 720), (190, 60))),
                                                    "",
                                                    object_id="#recruit_button",
                                                    visible=False,
                                                    manager=MANAGER)
        

        # Next and previous buttons
        self.elements['previous_step'] = UIImageButton(scale(pygame.Rect((506, 800), (294, 60))), "",
                                                       object_id="#previous_step_button", manager=MANAGER)
        self.elements['next_step'] = UIImageButton(scale(pygame.Rect((800, 800), (294, 60))), "",
                                                   object_id="#next_step_button", manager=MANAGER)
        self.elements['next_step'].disable()
        
        self.elements['customize'] = pygame_gui.elements.UIButton(scale(pygame.Rect((400,100),(100,50))), "customize", object_id="#small_button", manager=MANAGER)

        # draw cats to choose from
        self.refresh_cat_images_and_info()

    def open_customize_cat(self):
        self.clear_all_page()
        self.sub_screen = "customize cat"
        pelt2 = Pelt(
            name=self.pname,
            length=self.length,
            colour=self.colour,
            white_patches=self.white_patches,
            eye_color=self.eye_color,
            eye_colour2=self.eye_colour2,
            tortiebase=self.tortiebase,
            tortiecolour=self.tortiecolour,
            pattern=self.pattern,
            tortiepattern=self.tortiepattern,
            vitiligo=self.vitiligo,
            points=self.points,
            accessory=self.accessory,
            paralyzed=self.paralyzed,
            opacity=self.opacity,
            scars=self.scars,
            tint=self.tint,
            skin=self.skin,
            white_patches_tint=self.white_patches_tint,
            kitten_sprite=self.kitten_sprite,
            adol_sprite=self.adol_sprite,
            adult_sprite=self.adult_sprite,
            senior_sprite=self.senior_sprite,
            para_adult_sprite=self.para_adult_sprite,
            reverse=self.reverse,
            accessories=self.accessories
        )
        self.custom_cat = Cat(moons = 1, pelt=pelt2, loading_cat=True)
        self.custom_cat.sprite = generate_sprite(self.custom_cat)
        self.elements["sprite"] = UISpriteButton(scale(pygame.Rect
                                         ((700,100), (200, 200))),
                                   self.custom_cat.sprite,
                                   self.custom_cat.ID,
                                   starting_height=0, manager=MANAGER)
        
        column1_x = 200  # x-coordinate for column 1
        column2_x = 700  # x-coordinate for column 2
        column3_x = 1200  # x-coordinate for column 3
        y_pos = [400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300]
        
        pelts = list(Pelt.sprites_names.keys())
        pelts.remove("Tortie")
        pelts.remove("Calico")
        
        pelts_tortie = pelts.copy()
        pelts_tortie.remove("SingleColour")
        pelts_tortie.remove("TwoColour")
        pelts_tortie.append("Single")
        
        permanent_conditions = ['born without a leg', 'weak leg', 'twisted leg', 'born without a tail', 'paralyzed', 'raspy lungs', 'wasting disease', 'blind', 'one bad eye', 'failing eyesight', 'partial hearing loss', 'deaf', 'constant joint pain', 'seizure prone', 'allergies', 'persistent headaches']
        self.elements['pelt text'] = pygame_gui.elements.UITextBox(
            'Pelt type',
            scale(pygame.Rect((column1_x, y_pos[0] - 40),(1200,-1))),
            object_id=get_text_box_theme("#text_box_22_horizleft"), manager=MANAGER
        )
        self.elements['pelt color text'] = pygame_gui.elements.UITextBox(
            'Pelt color',
            scale(pygame.Rect((column1_x, y_pos[1] - 40),(1200,-1))),
            object_id=get_text_box_theme("#text_box_22_horizleft"), manager=MANAGER
        )
        self.elements['eye color text'] = pygame_gui.elements.UITextBox(
            'Eye color',
            scale(pygame.Rect((column1_x, y_pos[2] - 40),(1200,-1))),
            object_id=get_text_box_theme("#text_box_22_horizleft"), manager=MANAGER
        )
        self.elements['eye color2 text'] = pygame_gui.elements.UITextBox(
            'Second eye color (optional)',
            scale(pygame.Rect((column1_x, y_pos[3] - 40),(1200,-1))),
            object_id=get_text_box_theme("#text_box_22_horizleft"), manager=MANAGER
        )
        self.elements['white patch text'] = pygame_gui.elements.UITextBox(
            'White patches',
            scale(pygame.Rect((column1_x, y_pos[4] - 40),(1200,-1))),
            object_id=get_text_box_theme("#text_box_22_horizleft"), manager=MANAGER
        )
        self.elements['pelt length text'] = pygame_gui.elements.UITextBox(
            'Pelt length',
            scale(pygame.Rect((column1_x, y_pos[5] - 40),(1200,-1))),
            object_id=get_text_box_theme("#text_box_22_horizleft"), manager=MANAGER
        )
        self.elements['pelt dropdown'] = pygame_gui.elements.UIDropDownMenu(pelts, "SingleColour", scale(pygame.Rect((column1_x, y_pos[0]),(250,70))), manager=MANAGER)
        self.elements['pelt color'] = pygame_gui.elements.UIDropDownMenu(Pelt.pelt_colours, "WHITE", scale(pygame.Rect((column1_x, y_pos[1]),(250,70))), manager=MANAGER)
        self.elements['eye color'] = pygame_gui.elements.UIDropDownMenu(Pelt.eye_colours, "BLUE", scale(pygame.Rect((column1_x, y_pos[2]),(250,70))), manager=MANAGER)
        self.elements['eye color2'] = pygame_gui.elements.UIDropDownMenu(["None"] + Pelt.eye_colours, "None", scale(pygame.Rect((column1_x, y_pos[3]),(250,70))), manager=MANAGER)
        self.elements['white patches'] = pygame_gui.elements.UIDropDownMenu(["None", "FULLWHITE"] + Pelt.little_white + Pelt.mid_white + Pelt.high_white + Pelt.mostly_white, "None", scale(pygame.Rect((column1_x, y_pos[4]),(250,70))), manager=MANAGER)
        self.elements['pelt length'] = pygame_gui.elements.UIDropDownMenu(Pelt.pelt_length, "short", scale(pygame.Rect((column1_x, y_pos[5]), (250, 70))), manager=MANAGER)
        
        self.elements['para text'] = pygame_gui.elements.UITextBox(
            'Paralyzed',
            scale(pygame.Rect((column2_x, y_pos[0] - 40),(1200,-1))),
            object_id=get_text_box_theme("#text_box_22_horizleft"), manager=MANAGER
        )
        self.elements['reverse text'] = pygame_gui.elements.UITextBox(
            'Reverse',
            scale(pygame.Rect((column2_x, y_pos[1] - 40),(1200,-1))),
            object_id=get_text_box_theme("#text_box_22_horizleft"), manager=MANAGER
        )
        self.elements['scar text'] = pygame_gui.elements.UITextBox(
            'Scar',
            scale(pygame.Rect((column2_x, y_pos[2] - 40),(1200,-1))),
            object_id=get_text_box_theme("#text_box_22_horizleft"), manager=MANAGER
        )
        self.elements['vit text'] = pygame_gui.elements.UITextBox(
            'Vitiligo',
            scale(pygame.Rect((column2_x, y_pos[3] - 40),(1200,-1))),
            object_id=get_text_box_theme("#text_box_22_horizleft"), manager=MANAGER
        )
        self.elements['point text'] = pygame_gui.elements.UITextBox(
            'Points',
            scale(pygame.Rect((column2_x, y_pos[4] - 40),(1200,-1))),
            object_id=get_text_box_theme("#text_box_22_horizleft"), manager=MANAGER
        )
        self.elements['tint text'] = pygame_gui.elements.UITextBox(
            'Tint',
            scale(pygame.Rect((column2_x, y_pos[5] - 40),(1200,-1))),
            object_id=get_text_box_theme("#text_box_22_horizleft"), manager=MANAGER
        )
        self.elements['paralyzed'] = pygame_gui.elements.UIDropDownMenu(["Yes", "No"], "No", scale(pygame.Rect((column2_x, y_pos[0]), (250, 70))), manager=MANAGER)
        self.elements['reverse'] = pygame_gui.elements.UIDropDownMenu(["Yes", "No"], "No", scale(pygame.Rect((column2_x, y_pos[1]), (250, 70))), manager=MANAGER)
        self.elements['scars'] = pygame_gui.elements.UIDropDownMenu(["None"] + Pelt.scars1 + Pelt.scars2 + Pelt.scars3, "None", scale(pygame.Rect((column2_x, y_pos[2]), (250, 70))), manager=MANAGER)
        self.elements['vitiligo'] = pygame_gui.elements.UIDropDownMenu(["None"] + Pelt.vit, "None", scale(pygame.Rect((column2_x, y_pos[3]), (250, 70))), manager=MANAGER)
        self.elements['points'] = pygame_gui.elements.UIDropDownMenu(["None"] + Pelt.point_markings, "None", scale(pygame.Rect((column2_x, y_pos[4]), (250, 70))), manager=MANAGER)
        self.elements['tint'] = pygame_gui.elements.UIDropDownMenu(["pink", "gray", "red", "orange", "None"], "None", scale(pygame.Rect((column2_x, y_pos[5]), (250, 70))), manager=MANAGER)
        
        self.elements['skin text'] = pygame_gui.elements.UITextBox(
            'Skin',
            scale(pygame.Rect((column3_x, y_pos[0] - 40),(1200,-1))),
            object_id=get_text_box_theme("#text_box_22_horizleft"), manager=MANAGER
        )
        self.elements['white patch tint text'] = pygame_gui.elements.UITextBox(
            'White patches tint',
            scale(pygame.Rect((column3_x, y_pos[1] - 40),(1200,-1))),
            object_id=get_text_box_theme("#text_box_22_horizleft"), manager=MANAGER
        )
        self.elements['tortie text'] = pygame_gui.elements.UITextBox(
            'Tortie',
            scale(pygame.Rect((column3_x, y_pos[2] - 40),(1200,-1))),
            object_id=get_text_box_theme("#text_box_22_horizleft"), manager=MANAGER
        )
        self.elements['pattern text'] = pygame_gui.elements.UITextBox(
            'Pattern',
            scale(pygame.Rect((column3_x, y_pos[3] - 40),(1200,-1))),
            object_id=get_text_box_theme("#text_box_22_horizleft"), manager=MANAGER
        )
        self.elements['base text'] = pygame_gui.elements.UITextBox(
            'Base',
            scale(pygame.Rect((column3_x, y_pos[4] - 40),(1200,-1))),
            object_id=get_text_box_theme("#text_box_22_horizleft"), manager=MANAGER
        )
        self.elements['tortie color text'] = pygame_gui.elements.UITextBox(
            'Color',
            scale(pygame.Rect((column3_x, y_pos[5] - 40),(1200,-1))),
            object_id=get_text_box_theme("#text_box_22_horizleft"), manager=MANAGER
        )
        self.elements['tint text'] = pygame_gui.elements.UITextBox(
            'Patch pattern',
            scale(pygame.Rect((column3_x, y_pos[6] - 40),(1200,-1))),
            object_id=get_text_box_theme("#text_box_22_horizleft"), manager=MANAGER
        )
        self.elements['skin'] = pygame_gui.elements.UIDropDownMenu(Pelt.skin_sprites, "BLACK", scale(pygame.Rect((column3_x, y_pos[0]), (250, 70))), manager=MANAGER)
        self.elements['white_patches_tint'] = pygame_gui.elements.UIDropDownMenu(["None"] + ["offwhite"], "None", scale(pygame.Rect((column3_x, y_pos[1]), (250, 70))), manager=MANAGER)
        
        self.elements['tortie'] = pygame_gui.elements.UIDropDownMenu(["Yes", "No"], "No", scale(pygame.Rect((column3_x, y_pos[2]), (250, 70))), manager=MANAGER)
        self.elements['pattern'] = pygame_gui.elements.UIDropDownMenu(Pelt.tortiepatterns, "ONE", scale(pygame.Rect((column3_x, y_pos[3]), (250, 70))), manager=MANAGER)
        self.elements['tortiebase'] = pygame_gui.elements.UIDropDownMenu(Pelt.tortiebases, "single", scale(pygame.Rect((column3_x, y_pos[4]), (250, 70))), manager=MANAGER)
        self.elements['tortiecolor'] = pygame_gui.elements.UIDropDownMenu(Pelt.pelt_colours, "GINGER", scale(pygame.Rect((column3_x, y_pos[5]), (250, 70))), manager=MANAGER)
        self.elements['tortiepattern'] = pygame_gui.elements.UIDropDownMenu(pelts_tortie, "Bengal", scale(pygame.Rect((column3_x, y_pos[6]), (250, 70))), manager=MANAGER)

        # self.elements['permanent conditions'] = pygame_gui.elements.UIDropDownMenu(["None"] + permanent_conditions, "None", scale(pygame.Rect((column3_x, y_pos[7]), (250, 70))), manager=MANAGER)
        
        self.elements['pattern'].disable()
        self.elements['tortiebase'].disable()
        self.elements['tortiecolor'].disable()
        self.elements['tortiepattern'].disable()
        
        self.elements['previous_step'] = UIImageButton(scale(pygame.Rect((506, 1200), (294, 60))), "",
                                                       object_id="#previous_step_button", manager=MANAGER)
        self.elements['next_step'] = UIImageButton(scale(pygame.Rect((800, 1200), (294, 60))), "",
                                                   object_id="#next_step_button", manager=MANAGER)
        
        # sex, perm condition, sprite kitten, personality, trait, more scars
        # color tints based on color groups
                
    def handle_customize_cat_event(self, event):
        if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if event.ui_element == self.elements['pelt dropdown']:
                self.pname = event.text
                self.update_sprite()
            elif event.ui_element == self.elements['pelt color']:
                self.colour = event.text
                self.update_sprite()
            elif event.ui_element == self.elements['eye color']:
                self.eye_color = event.text
                self.update_sprite()
            elif event.ui_element == self.elements['eye color2']:
                if event.text == "None":
                    self.eye_colour2 = None
                else:
                    self.eye_colour2 = event.text
                self.update_sprite()
            elif event.ui_element == self.elements['white patches']:
                if event.text == "None":
                    self.white_patches = None
                else:
                    self.white_patches = event.text
                self.update_sprite()
            elif event.ui_element == self.elements['pelt length']:
                self.length = event.text
                self.update_sprite()
            elif event.ui_element == self.elements['scars']:
                if event.text == "None":
                    self.scars = None
                else:
                    self.scars = [event.text]
                self.update_sprite()
            elif event.ui_element == self.elements['tortie']:
                if event.text == "Yes":
                    self.pname = "Tortie"
                    self.elements['pelt dropdown'].disable()
                    self.elements['pattern'].enable()
                    self.elements['tortiebase'].enable()
                    self.elements['tortiecolor'].enable()
                    self.elements['tortiepattern'].enable()
                    
                    self.pattern = "ONE"
                    self.tortiepattern = "bengal"
                    self.tortiebase = "single"
                    self.tortiecolour = "GINGER"
                else:
                    self.pname = "SingleColour"
                    self.elements['pelt dropdown'].enable()
                    self.elements['pattern'].disable()
                    self.elements['tortiebase'].disable()
                    self.elements['tortiecolor'].disable()
                    self.elements['tortiepattern'].disable()
                    self.pattern = None
                    self.tortiebase = None
                    self.tortiepattern = None
                    self.tortiecolour = None
                self.update_sprite()
                
            elif event.ui_element == self.elements['tortiecolor']:
                self.tortiecolour = event.text
                self.update_sprite()
            elif event.ui_element == self.elements['pattern']:
                self.pattern = event.text
                self.update_sprite()
            elif event.ui_element == self.elements['tortiepattern']:
                self.tortiepattern = event.text.lower()
                self.update_sprite()
            elif event.ui_element == self.elements['tortiebase']:
                self.tortiebase = event.text
                self.update_sprite()
            elif event.ui_element == self.elements['vitiligo']:
                if event.text == "None":
                    self.vitiligo = None
                else:
                    self.vitiligo = event.text
                self.update_sprite()
            elif event.ui_element == self.elements['points']:
                if event.text == "None":
                    self.points = None
                else:
                    self.points = event.text
                self.update_sprite()
            elif event.ui_element == self.elements['paralyzed']:
                self.paralyzed = (event.text == "Yes")
                self.update_sprite()
            elif event.ui_element == self.elements['tint']:
                if event.text == "None":
                    self.tint = None
                else:
                    self.tint = event.text
                self.update_sprite()
            elif event.ui_element == self.elements['skin']:
                self.skin = event.text
                self.update_sprite()
            elif event.ui_element == self.elements['white_patches_tint']:
                if event.text == "None":
                    self.white_patches_tint = None
                else:
                    self.white_patches_tint = event.text
                self.update_sprite()
            elif event.ui_element == self.elements['reverse']:
                self.reverse = (event.text == "Yes")
                self.update_sprite()
            # elif event.ui_element == self.elements['permanent conditions']:
            #     chosen_condition = event.text
            #     self.custom_cat.get_permanent_condition(chosen_condition, True)
            #     # assign scars
            #     if chosen_condition in ['lost a leg', 'born without a leg']:
            #         self.custom_cat.pelt.scars.append('NOPAW')
            #     elif chosen_condition in ['lost their tail', 'born without a tail']:
            #         self.custom_cat.pelt.scars.append("NOTAIL")
            #     self.update_sprite()
        elif event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.elements['next_step']:
                new_cat = Cat(moons = 1)
                new_cat.pelt = self.custom_cat.pelt
                self.your_cat = new_cat
                self.selected_cat = None
                self.open_name_cat()
            elif event.ui_element == self.elements['previous_step']:
                self.open_choose_leader()

    def update_sprite(self):
        pelt2 = Pelt(
            name=self.pname,
            length=self.length,
            colour=self.colour,
            white_patches=self.white_patches,
            eye_color=self.eye_color,
            eye_colour2=self.eye_colour2,
            tortiebase=self.tortiebase,
            tortiecolour=self.tortiecolour,
            pattern=self.pattern,
            tortiepattern=self.tortiepattern,
            vitiligo=self.vitiligo,
            points=self.points,
            accessory=self.accessory,
            paralyzed=self.paralyzed,
            opacity=self.opacity,
            scars=self.scars,
            tint=self.tint,
            skin=self.skin,
            white_patches_tint=self.white_patches_tint,
            kitten_sprite=self.kitten_sprite,
            adol_sprite=self.adol_sprite,
            adult_sprite=self.adult_sprite,
            senior_sprite=self.senior_sprite,
            para_adult_sprite=self.para_adult_sprite,
            reverse=self.reverse,
            accessories=self.accessories
        )
        self.custom_cat = Cat(moons = 1, pelt=pelt2, loading_cat=True)
        self.custom_cat.sprite = generate_sprite(self.custom_cat)
        self.elements['sprite'].kill()
        self.elements["sprite"] = UISpriteButton(scale(pygame.Rect
                                         ((700,100), (200, 200))),
                                   self.custom_cat.sprite,
                                   self.custom_cat.ID,
                                   starting_height=0, manager=MANAGER)
    
    def open_choose_background(self):
        # clear screen
        self.clear_all_page()
        self.sub_screen = 'choose camp'

        self.elements['previous_step'] = UIImageButton(scale(pygame.Rect((506, 1290), (294, 60))), "",
                                                       object_id="#previous_step_button", manager=MANAGER)
        self.elements["done_button"] = UIImageButton(scale(pygame.Rect((800, 1290), (294, 60))), "",
                                                     object_id="#done_arrow_button", manager=MANAGER)
        self.elements['done_button'].disable()

        # Biome buttons
        self.elements['forest_biome'] = UIImageButton(scale(pygame.Rect((392, 200), (200, 92))), "",
                                                      object_id="#forest_biome_button", manager=MANAGER)
        self.elements['mountain_biome'] = UIImageButton(scale(pygame.Rect((608, 200), (212, 92))), "",
                                                        object_id="#mountain_biome_button", manager=MANAGER)
        self.elements['plains_biome'] = UIImageButton(scale(pygame.Rect((848, 200), (176, 92))), "",
                                                      object_id="#plains_biome_button", manager=MANAGER)
        self.elements['beach_biome'] = UIImageButton(scale(pygame.Rect((1040, 200), (164, 92))), "",
                                                     object_id="#beach_biome_button", manager=MANAGER)

        # Camp Art Choosing Tabs, Dummy buttons, will be overridden.
        self.tabs["tab1"] = UIImageButton(scale(pygame.Rect((0, 0), (0, 0))), "",
                                          visible=False, manager=MANAGER)
        self.tabs["tab2"] = UIImageButton(scale(pygame.Rect((0, 0), (0, 0))), "",
                                          visible=False, manager=MANAGER)
        self.tabs["tab3"] = UIImageButton(scale(pygame.Rect((0, 0), (0, 0))), "",
                                          visible=False, manager=MANAGER)

        y_pos = 550
        self.tabs["newleaf_tab"] = UIImageButton(scale(pygame.Rect((1250, y_pos), (78, 68))), "",
                                                 object_id="#newleaf_toggle_button",
                                                 manager=MANAGER,
                                                 tool_tip_text='Switch starting season to Newleaf.'
                                                 )
        y_pos += 100
        self.tabs["greenleaf_tab"] = UIImageButton(scale(pygame.Rect((1250, y_pos), (78, 68))), "",
                                                   object_id="#greenleaf_toggle_button",
                                                   manager=MANAGER,
                                                   tool_tip_text='Switch starting season to Greenleaf.'
                                                   )
        y_pos += 100
        self.tabs["leaffall_tab"] = UIImageButton(scale(pygame.Rect((1250, y_pos), (78, 68))), "",
                                                  object_id="#leaffall_toggle_button",
                                                  manager=MANAGER,
                                                  tool_tip_text='Switch starting season to Leaf-fall.'
                                                  )
        y_pos += 100
        self.tabs["leafbare_tab"] = UIImageButton(scale(pygame.Rect((1250, y_pos), (78, 68))), "",
                                                  object_id="#leafbare_toggle_button",
                                                  manager=MANAGER,
                                                  tool_tip_text='Switch starting season to Leaf-bare.'
                                                  )
        # Random background
        self.elements["random_background"] = UIImageButton(scale(pygame.Rect((510, 1190), (580, 60))), "",
                                                           object_id="#random_background_button", manager=MANAGER)

        # art frame
        self.elements['art_frame'] = pygame_gui.elements.UIImage(scale(pygame.Rect(((334, 324), (932, 832)))),
                                                                 pygame.transform.scale(
                                                                     pygame.image.load(
                                                                         "resources/images/bg_preview_border.png").convert_alpha(),
                                                                     (932, 832)), manager=MANAGER)

        # camp art self.elements["camp_art"] = pygame_gui.elements.UIImage(scale(pygame.Rect((175,170),(450, 400))),
        # pygame.image.load(self.get_camp_art_path(1)).convert_alpha(), visible=False)

    def open_clan_saved_screen(self):
        self.clear_all_page()

        self.sub_screen = 'saved screen'

        self.elements["leader_image"] = pygame_gui.elements.UIImage(scale(pygame.Rect((700, 240), (200, 200))),
                                                                    pygame.transform.scale(
                                                                        self.your_cat.sprite,
                                                                        (200, 200)), manager=MANAGER)
        self.elements["continue"] = UIImageButton(scale(pygame.Rect((692, 500), (204, 60))), "",
                                                  object_id="#continue_button_small")
        self.elements["save_confirm"] = pygame_gui.elements.UITextBox('Welcome to the world, ' + self.your_cat.name.prefix + 'kit!',
                                                                      scale(pygame.Rect((200, 270), (1200, 60))),
                                                                      object_id=get_text_box_theme(
                                                                          "#text_box_30_horizcenter"),
                                                                      manager=MANAGER)

    def save_clan(self):
        self.handle_create_other_cats()
        game.mediated.clear()
        game.patrolled.clear()
        game.cat_to_fade.clear()
        Cat.outside_cats.clear()
        Patrol.used_patrols.clear()
        convert_camp = {1: 'camp1', 2: 'camp2', 3: 'camp3'}
        self.your_cat.create_inheritance_new_cat()
        game.clan = Clan(self.clan_name,
                         self.leader,
                         self.deputy,
                         self.med_cat,
                         self.biome_selected,
                         convert_camp[self.selected_camp_tab],
                         self.game_mode, self.members,
                         starting_season=self.selected_season,
                         your_cat=self.your_cat)
        game.clan.your_cat.moons = -1
        game.clan.create_clan()
        #game.clan.starclan_cats.clear()
        game.cur_events_list.clear()
        game.herb_events_list.clear()
        Cat.grief_strings.clear()
        Cat.sort_cats()

    def get_camp_art_path(self, campnum):
        leaf = self.selected_season.replace("-", "")

        camp_bg_base_dir = "resources/images/camp_bg/"
        start_leave = leaf.casefold()
        light_dark = "light"
        if game.settings["dark mode"]:
            light_dark = "dark"

        biome = self.biome_selected.lower()

        if campnum:
            return f'{camp_bg_base_dir}/{biome}/{start_leave}_camp{campnum}_{light_dark}.png'
        else:
            return None
