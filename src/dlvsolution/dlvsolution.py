import os

from base.option_descriptor import OptionDescriptor
from languages.asp.asp_input_program import ASPInputProgram
from languages.asp.asp_mapper import ASPMapper

from src.constants import RESOURCES_PATH
from src.dlvsolution.helpers import choose_dlv_system, Color, Ball, Tube, Move, On, GameOver


class DLVSolution:

    def __init__(self):
        try:
            self.__handler = choose_dlv_system()
            self.__static_facts = None
            self.__dinamic_facts = None
            self.__fixedInputProgram = ASPInputProgram()

            self.__init_fixed()
        except Exception as e:
            print(str(e))

    def __init_fixed(self):
        self.__fixedInputProgram.add_files_path(os.path.join(RESOURCES_PATH, "ballSort.txt"))
        self.__handler.add_program(self.__fixedInputProgram)

    def __init_static_facts(self, colors: [], balls: [], tubes: []):
        self.__static_facts = ASPInputProgram()
        for color in colors:
            self.__static_facts.add_object_input(color)

        for ball in balls:
            self.__static_facts.add_object_input(ball)

        tube_size = 0
        full_tube = 0
        for tube in tubes:
            self.__static_facts.add_object_input(tube)
            if len(tube.get_balls()) > 0:
                tube_size = len(tube.get_balls())
                full_tube += 1

        self.__static_facts.add_program("tubeSize(" + str(tube_size) + ").")
        self.__static_facts.add_program("fullTube(" + str(full_tube) + ").")

        print(self.__static_facts.get_programs())

    def call_asp(self, colors: [], balls: [], tubes: [], on: []):

        ASPMapper.get_instance().register_class(Color)
        ASPMapper.get_instance().register_class(Ball)
        ASPMapper.get_instance().register_class(Tube)
        ASPMapper.get_instance().register_class(Move)
        ASPMapper.get_instance().register_class(On)
        ASPMapper.get_instance().register_class(GameOver)

        self.__init_static_facts(colors, balls, tubes)

        self.__dinamic_facts = ASPInputProgram()
        for o in on:
            self.__dinamic_facts.add_object_input(o)

        self.__handler.add_program(self.__static_facts)
        self.__handler.add_program(self.__dinamic_facts)

        option = OptionDescriptor("--filter=on/4, move/3, gameOver/1")
        self.__handler.add_option(option)

        moves = []
        ons = []
        game_over = False

        step = 1
        while not game_over:
            #print(step)
            self.__dinamic_facts.add_program("step(" + str(step) + ").")

            print(self.__dinamic_facts.get_programs())

            answer_sets = self.__handler.start_sync()

            self.__dinamic_facts.clear_all()

            for answer_set in answer_sets.get_optimal_answer_sets():
                print(answer_set)
                for obj in answer_set.get_atoms():
                    if isinstance(obj, Move):
                        if obj.get_step() == step:
                            self.__dinamic_facts.add_object_input(obj)
                            moves.append(obj)

                    if isinstance(obj, On):
                        if obj.get_step() == 1:
                            ons.append(obj)
                        if obj.get_step() == step + 1:
                            self.__dinamic_facts.add_object_input(obj)
                            ons.append(obj)

                    if isinstance(obj, GameOver):
                        game_over = True

            step += 1

        return moves, ons
