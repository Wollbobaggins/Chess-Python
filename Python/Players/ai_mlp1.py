##############################################################################
############################### Module Imports ###############################
##############################################################################
import keras
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Conv1D, MaxPooling1D
from keras.callbacks import EarlyStopping
from keras.models import Input, Model
from keras.models import load_model

import numpy as np

import pandas as pd

import random
from random import randint

import sklearn
import sklearn.datasets
from sklearn import metrics as mt

import player as PLAYER
##############################################################################

class AI_Mlp1(PLAYER.Player):

    def __init__(self, color, model_file_path):
        """
        Initialization for Random AI Object
        """
        super().__init__(color)
        self.found_model = True

        try:
            self.model = load_model(model_file_path)
            print("Succeeded to load model.\n")
            self.found_model = True

        except IOError:
            print("Failed to load model. AI will now play moves randomly.")
            self.found_model = False



    def request_move(self, board):
        """
        Asks the AI what move to make, AI submits possible move to Chess game
        :return: a starting location and ending location for chess move
        """
        if self.found_model:

            best_start_coordinate, best_end_coordinate = self.get_best_move(board)
            cf1, cr1 = board._convert_to_chess_coordinates(best_start_coordinate[0], best_start_coordinate[1])
            cf2, cr2 = board._convert_to_chess_coordinates(best_end_coordinate[0], best_end_coordinate[1])

        else:

            cf1 = self._alphabet[random.randint(0, 7)]
            cr1 = randint(1, 8)
            cf2 = self._alphabet[randint(0, 7)]
            cr2 = randint(1, 8)

        return cf1, cr1, cf2, cr2



    def get_best_move(self, board):
        """

        :param board:
        :return:
        """
        move_and_evaluations = []
        for r in range(board.height):
            for c in range(board.width):
                piece = board.grid[r][c].piece
                if self.color == piece.color:
                    valid_available_coordinates = board.get_valid_available_coordinates(piece)
                    for end_coordinate in valid_available_coordinates:
                        copy_board = board.copy_board_object()
                        copy_board.execute_valid_move(start_coordinate=[r, c], end_coordinate=end_coordinate)
                        copy_board_data = self.convert_board_ohe(self.color, copy_board)
                        for i in copy_board_data:
                            print(i,end=', ')
                        print()
                        copy_board_data = np.expand_dims(copy_board_data, axis=0)
                        copy_board_data = np.expand_dims(copy_board_data, axis=2)

                        move_and_evaluations.append([[r, c], end_coordinate, self.model.predict(copy_board_data)[0][0]])

        best_start_coordinate = None
        best_end_coordinate = None

        if self.color == 'white':
            best_evaluation = -1000000
        else:
            best_evaluation = 1000000

        for me in move_and_evaluations:
            start_coordinate = me[0]
            end_coordinate = me[1]
            evaluation = me[2]
            if self.color == 'white':
                if evaluation > best_evaluation:
                    best_start_coordinate = start_coordinate
                    best_end_coordinate = end_coordinate
                    best_evaluation = evaluation
            else:
                if evaluation < best_evaluation:
                    best_start_coordinate = start_coordinate
                    best_end_coordinate = end_coordinate
                    best_evaluation = evaluation

        print(best_evaluation)
        return best_start_coordinate, best_end_coordinate



    @staticmethod
    def convert_board_ohe(color, board):
        """
        Convert's board.grid into a normalized numpy array of the piece values
        :param color: Team color
        :param board: Board object
        :return: normalized numpy array of the piece values; length 509
                    (0:505 - one hot encoded board of piece values
                     505   - which color's turn is it
                     506:509 - castling options for each color)
        """
        board_data = []

        # Converts the board into piece's values
        for r in range(board.height):
            for c in range(board.width):
                if board.grid[r][c].piece.symbol == 'bp':
                    board_data.extend([1, 0, 1, 0, 0, 0, 0, 0])
                elif board.grid[r][c].piece.symbol == 'bn':
                    board_data.extend([1, 0, 0, 1, 0, 0, 0, 0])
                elif board.grid[r][c].piece.symbol == 'bb':
                    board_data.extend([1, 0, 0, 0, 1, 0, 0, 0])
                elif board.grid[r][c].piece.symbol == 'br':
                    board_data.extend([1, 0, 0, 0, 0, 1, 0, 0])
                elif board.grid[r][c].piece.symbol == 'bq':
                    board_data.extend([1, 0, 0, 0, 0, 0, 1, 0])
                elif board.grid[r][c].piece.symbol == 'bk':
                    board_data.extend([1, 0, 0, 0, 0, 0, 0, 1])
                elif board.grid[r][c].piece.symbol == 'wp':
                    board_data.extend([1, 1, 1, 0, 0, 0, 0, 0])
                elif board.grid[r][c].piece.symbol == 'wn':
                    board_data.extend([1, 1, 0, 1, 0, 0, 0, 0])
                elif board.grid[r][c].piece.symbol == 'wb':
                    board_data.extend([1, 1, 0, 0, 1, 0, 0, 0])
                elif board.grid[r][c].piece.symbol == 'wr':
                    board_data.extend([1, 1, 0, 0, 0, 1, 0, 0])
                elif board.grid[r][c].piece.symbol == 'wq':
                    board_data.extend([1, 1, 0, 0, 0, 0, 1, 0])
                elif board.grid[r][c].piece.symbol == 'wk':
                    board_data.extend([1, 1, 0, 0, 0, 0, 0, 1])
                else:
                    board_data.extend([0, 0, 0, 0, 0, 0, 0, 0])  # Else no piece was found

        # Converts player turn into either 1 or -1 given color
        if color == 'white':
            board_data.append(1)
        else:
            board_data.append(0)

        # Converts board's castling potential into either 1 or 0
        if board.grid[7][4].piece._turn_last_moved == 0:
            board_data.append(board.grid[7][7].piece._turn_last_moved == 0)
            board_data.append(board.grid[7][0].piece._turn_last_moved == 0)
        else:
            board_data.append(0)
            board_data.append(0)

        if board.grid[0][4].piece._turn_last_moved == 0:
            board_data.append(board.grid[0][7].piece._turn_last_moved == 0)
            board_data.append(board.grid[0][0].piece._turn_last_moved == 0)
        else:
            board_data.append(0)
            board_data.append(0)

        # returns normalized board_data containing values between -1 and 1
        return np.array(board_data)
