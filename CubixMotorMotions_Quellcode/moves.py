import cube
import movement_checker

class MovePool(): #TODO: Maybe subclass from list or collections.MutableSequence ?!
    def __init__(self):
        self.moves = list()

    def add_move(self, move):
        if(issubclass(type(move), AbstractMove)):
            self.moves.append(move) #TODO: Maybe show the move which "move_number" he has ?!
            return True
        return False

    def remove_move(self, move):
        if(move in self.moves):
            self.moves.remove(move)
            return True
        return False

    def get_pool(self):
        return self.moves

    @classmethod
    def from_string(cls, string):
        pool = cls()
        for string_move in string.split(","):
            pool.add_move(AbstractMove.from_string(string_move.strip()))
        return pool

class AbstractMove():
    def __init__(self, inverse=False):
        self.inverse = inverse

    @classmethod
    def from_string(cls, string_move):
        face = cube.FaceID(string_move[0])
        for move_class in [UpMove, DownMove, BackMove, FrontMove, LeftMove, RightMove]:
            if(move_class.face == face):
                return move_class(inverse=bool("'" in string_move))
        raise ValueError("Cannot Parse {0} to any CubeMove!".format(str(string_move)))

class UpMove(AbstractMove):
    face = cube.FaceID.UP

class DownMove(AbstractMove):
    face = cube.FaceID.DOWN

class BackMove(AbstractMove):
    face = cube.FaceID.BACK

class FrontMove(AbstractMove):
    face = cube.FaceID.FRONT

class LeftMove(AbstractMove):
    face = cube.FaceID.LEFT

class RightMove(AbstractMove):
    face = cube.FaceID.RIGHT
