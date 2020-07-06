import moves
import motor
import cube
import rotations
import networkx as nx
import itertools
import copy
import os
import sys

class NoPathException(Exception):
    pass

left_arm = motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL)
right_arm = motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL)
down_arm = motor.MotorArmState(motor.MotorArmAngle.VERTICAL)

start_motor_map = motor.MoveMotorMap()
start_motor_map[cube.FaceID.LEFT] = left_arm
start_motor_map[cube.FaceID.RIGHT] = right_arm
start_motor_map[cube.FaceID.DOWN] = down_arm


class Path(list):
    def print_path(self):
        print("\nPath:")
        for idx, n in enumerate(self):
            print("{0}.: {1}".format(str(idx), str(n)))
        print("\n")

class EdgePathSearcher():
    def __init__(self, g, edge_attribute="rotation"):
        self.g = g
        self.edge_attribute = edge_attribute
        self.visited_nodes = list()
        self.path = list()

    def search_path_to_edge(self, start, target_edge, max_depth):
        for i in range(1, max_depth+1):
            self.path.clear()
            self._depth_limited_search(start, target_edge, i)
            if(len(self.path)>0): #TODO: Search best path, not first we encounter!
                return self.path
        raise NoPathException("No Valid Path from {0} to reach edge {1}".format(str(start), str(target_edge)))

    def _depth_limited_search(self, start, target_edge, max_depth):
        print("Searching for depth: {0}".format(str(max_depth)))
        #print("visited nodes: {0}".format(str(self.visited_nodes)))
        if(max_depth==0 or start in self.visited_nodes):
            return False
        #print("adding visited_nodes: {0}".format(str(start)))
        self.visited_nodes.append(start)
        for neighbor in self.g.neighbors(start):
           # print("proccessing neighbor: {0}".format(str(neighbor)))
            if(self.g.get_edge_data(start, neighbor).get(self.edge_attribute, None)==target_edge):
                self.path.insert(0, neighbor)
                print("Found edge {0} between {1} and {2} !!".format(str(target_edge), str(start), str(neighbor)))
                return True
            elif(not isinstance(self.g.get_edge_data(start, neighbor).get(self.edge_attribute, None), rotations.NoRotationTurn)):
                print("another rotation between {0} and {1}".format(str(start), str(neighbor)))
                continue
            if(self._depth_limited_search(neighbor, target_edge, max_depth-1)):
                print("Found path somewhere in the chain! adding neighbor: {0}".format(str(neighbor)))
                self.path.insert(0, neighbor)
                return True
            #print("continuing with next neigbor...")
        #print("removing visited_nodes: {0}".format(str(start)))
        self.visited_nodes.remove(start)


class MoveCubeMap(dict):
    def apply_cube_turn(self, specific_cube_rotation_turn):
        for k, v in specific_cube_rotation_turn.items():
            self[self[k]] = v

    def get_who_has_mapped(self, face_id):
        for mapped_face, face in self.items():
            if(face_id==face):
                return mapped_face

    @classmethod
    def start_position_map(cls):
        move_cube_map = cls()
        move_cube_map[cube.FaceID.RIGHT] = cube.FaceID.RIGHT
        move_cube_map[cube.FaceID.UP] = cube.FaceID.UP
        move_cube_map[cube.FaceID.DOWN] = cube.FaceID.DOWN
        move_cube_map[cube.FaceID.LEFT] = cube.FaceID.LEFT
        move_cube_map[cube.FaceID.BACK] = cube.FaceID.BACK
        move_cube_map[cube.FaceID.FRONT] = cube.FaceID.FRONT
        return move_cube_map


class MotorMovesSolver():
    def __init__(self, moves_pool, start_motor_state, move_cube_map=None, max_depth=8):
        self.moves_pool = moves_pool
        self.current_motor_state = start_motor_state
        self.move_cube_map = (move_cube_map if(move_cube_map is not None) else MoveCubeMap.start_position_map())
        self.max_depth = max_depth
        self.g = nx.read_gpickle(os.path.join(os.path.abspath(os.path.curdir), "graph.bin"))
        self.path = Path([start_motor_state])

    def solve(self):
        for move in self.moves_pool.get_pool():
            if(move.face not in self.current_motor_state):
                print("No mapping to {0}. Searching for mapping....".format(str(move.face)))
                cube_turn_comb = self._search_cube_rotation_combination_for_needed_face_id_to_be_mapped(move.face)
                print("Found cube_turn_combination: {0}. Searching for path...".format(str(cube_turn_comb)))
                self._search_path_for_cube_rotation_turn_combination(cube_turn_comb)
                print("Found path!!")
                self.path.print_path()
            transformed_face = self.move_cube_map.get_who_has_mapped(move.face)
            print("Searching for path to {0}... -> Transformed to {1}".format(str(move.face), str(transformed_face)))
            self._search_path_for_move_face(transformed_face)
            print("Found path!!")
            self.path.print_path()
        return self.path

    def _search_cube_rotation_combination_for_needed_face_id_to_be_mapped(self, face_id):
        for cube_turn_comb in itertools.product(itertools.chain(rotations.CubeRotationTurn.y_axis_cube_turn().cube_rotation_turn_mapping, rotations.CubeRotationTurn.x_axis_cube_turn().cube_rotation_turn_mapping), repeat=2):
            move_cube_map = copy.deepcopy(self.move_cube_map)
            print("Trying {0}..".format(str(cube_turn_comb)))
            for idx, cube_turn in enumerate(cube_turn_comb):
                move_cube_map.apply_cube_turn(cube_turn)
                print(str([move_cube_map[motor_face_id] for motor_face_id in self.current_motor_state]))
                if(face_id in [move_cube_map[motor_face_id] for motor_face_id in self.current_motor_state]):
                    return cube_turn_comb[:idx+1]
        raise NoPathException("There is no Path to rotate the cube in such a way that {0} is mapped on a motor_arm".format(str(face_id)))

    def _search_path_for_cube_rotation_turn_combination(self, cube_rotation_turn_combination):
        for cube_turn in cube_rotation_turn_combination:
            cube_rotation_turn = (rotations.CubeRotationTurn.x_axis_cube_turn() if(rotations.CubeRotationTurn.x_axis_cube_turn().is_specific_cube_turn_in_mapping(cube_turn)) else rotations.CubeRotationTurn.y_axis_cube_turn())
            #print("Searching for {0}..".format(str(cube_rotation_turn)))
            path = EdgePathSearcher(self.g).search_path_to_edge(self.current_motor_state, cube_rotation_turn, self.max_depth)
            self.move_cube_map.apply_cube_turn(cube_turn)
            self._add_path(path)

    def _search_path_for_move_face(self, face_id):
        path = EdgePathSearcher(self.g).search_path_to_edge(self.current_motor_state, rotations.FaceRotationTurn([face_id]), self.max_depth)
        self._add_path(path)

    def _add_path(self, path):
        self.path.extend(path)
        self.current_motor_state = self.path[-1]





if(__name__=="__main__"):
    if(len(sys.argv)<=2):
        print("Usage: {0} [moves seperated by comma] [max_depth]\n For Example: {0} R,L,U',B',R,R,L,D' 10\n".format(str(sys.argv[0])))
        os._exit(0)

    moves_string = sys.argv[1]
    max_depth = int(sys.argv[2])

    moves_pool = moves.MovePool.from_string(moves_string)
    
    solver = MotorMovesSolver(moves_pool, start_motor_map, max_depth=max_depth)
    solver.solve()
