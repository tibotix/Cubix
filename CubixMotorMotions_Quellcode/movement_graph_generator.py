import motor
import cube
import movement_checker
import movement_rules
import rotations

import networkx as nx
import matplotlib.pyplot as plt
import os


left_arm = motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL)
right_arm = motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL)
down_arm = motor.MotorArmState(motor.MotorArmAngle.VERTICAL)

start_motor_map = motor.MoveMotorMap()
start_motor_map[cube.FaceID.LEFT] = left_arm
start_motor_map[cube.FaceID.RIGHT] = right_arm
start_motor_map[cube.FaceID.DOWN] = down_arm



class GraphGenerator():
    def __init__(self, start_motor_map, movement_checker, rotation_turn_factory):
        self.start_motor_map = start_motor_map
        self.movement_checker = movement_checker
        self.rotation_turn_factory = rotation_turn_factory

    def generate_graph(self):
        self.g = nx.Graph()
        self.g.add_node(start_motor_map)
        self._process_motor_map(self.start_motor_map)
        print("Successfully generated Graph!!")
        return self.g

    def _process_motor_map(self, motor_map):
        #print("Starting   {0}!".format(str(motor_map)))
        for new_motor_map in motor_map.all_maps:
            if(not self.movement_checker.is_allowed(motor_map, new_motor_map)):
                #print("Not allowed: {0}".format(str(new_motor_map)))
                continue
            print("processing {0}...".format(str(new_motor_map)))
            print("neighbors: {0}".format(str(len(list(self.g.neighbors(motor_map))))))
            print("anzahl nodes: {0}".format(str(self.g.number_of_nodes())))

            rotation_turn = self.rotation_turn_factory.get_rotatation_turn(motor_map, new_motor_map)

            if(new_motor_map in self.g.neighbors(motor_map)):
                self.g.add_edge(motor_map, new_motor_map, rotation=rotation_turn)
                continue
            self.g.add_edge(motor_map, new_motor_map, rotation=rotation_turn)
            self._process_motor_map(new_motor_map)



if(__name__=='__main__'):

    side_arm_cube_rotation_turn_group = rotations.CubeRotationTurnGroup((cube.FaceID.LEFT, cube.FaceID.RIGHT), rotations.CubeRotationTurn.y_axis_cube_turn())
    down_arm_cube_rotation_turn_group = rotations.CubeRotationTurnGroup((cube.FaceID.DOWN,), rotations.CubeRotationTurn.x_axis_cube_turn())
    rotation_turn_factory = rotations.RotationTurnFactory([side_arm_cube_rotation_turn_group, down_arm_cube_rotation_turn_group])

    move_checker = movement_checker.MovementChecker()

    #-----------------------------
    # Only one Side MotorArm turns without down hold -> undefined behaviour

    move_checker.deny_move(movement_rules.MovementDenyRule(motor.RuleMotorMap({
        cube.FaceID.LEFT: (motor.MotorArmState(motor.MotorArmAngle.VERTICAL),),
        cube.FaceID.DOWN: (motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL, motor.MotorArmPosition.RELEASED), motor.MotorArmState(motor.MotorArmAngle.VERTICAL, motor.MotorArmPosition.RELEASED)),
        cube.FaceID.RIGHT: (motor.MotorArmState(motor.MotorArmAngle.VERTICAL),)}),
                                                           motor.RuleMotorMap({
        cube.FaceID.LEFT: (motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL),),
        cube.FaceID.DOWN: (motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL, motor.MotorArmPosition.RELEASED), motor.MotorArmState(motor.MotorArmAngle.VERTICAL, motor.MotorArmPosition.RELEASED)),
        cube.FaceID.RIGHT: (motor.MotorArmState(motor.MotorArmAngle.VERTICAL),)})))

    move_checker.deny_move(movement_rules.MovementDenyRule(motor.RuleMotorMap({
        cube.FaceID.LEFT: (motor.MotorArmState(motor.MotorArmAngle.VERTICAL),),
        cube.FaceID.DOWN: (motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL, motor.MotorArmPosition.RELEASED), motor.MotorArmState(motor.MotorArmAngle.VERTICAL, motor.MotorArmPosition.RELEASED)),
        cube.FaceID.RIGHT: (motor.MotorArmState(motor.MotorArmAngle.VERTICAL),)}),
                                                           motor.RuleMotorMap({
        cube.FaceID.LEFT: (motor.MotorArmState(motor.MotorArmAngle.VERTICAL),),
        cube.FaceID.DOWN: (motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL, motor.MotorArmPosition.RELEASED), motor.MotorArmState(motor.MotorArmAngle.VERTICAL, motor.MotorArmPosition.RELEASED)),
        cube.FaceID.RIGHT: (motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL),)})))

    move_checker.deny_move(movement_rules.MovementDenyRule(motor.RuleMotorMap({
        cube.FaceID.LEFT: (motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL),),
        cube.FaceID.DOWN: (motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL, motor.MotorArmPosition.RELEASED), motor.MotorArmState(motor.MotorArmAngle.VERTICAL, motor.MotorArmPosition.RELEASED)),
        cube.FaceID.RIGHT: (motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL),)}),
                                                           motor.RuleMotorMap({
        cube.FaceID.LEFT: (motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL),),
        cube.FaceID.DOWN: (motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL, motor.MotorArmPosition.RELEASED), motor.MotorArmState(motor.MotorArmAngle.VERTICAL, motor.MotorArmPosition.RELEASED)),
        cube.FaceID.RIGHT: (motor.MotorArmState(motor.MotorArmAngle.VERTICAL),)})))

    move_checker.deny_move(movement_rules.MovementDenyRule(motor.RuleMotorMap({
        cube.FaceID.LEFT: (motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL),),
        cube.FaceID.DOWN: (motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL, motor.MotorArmPosition.RELEASED), motor.MotorArmState(motor.MotorArmAngle.VERTICAL, motor.MotorArmPosition.RELEASED)),
        cube.FaceID.RIGHT: (motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL),)}),
                                                           motor.RuleMotorMap({
        cube.FaceID.LEFT: (motor.MotorArmState(motor.MotorArmAngle.VERTICAL),),
        cube.FaceID.DOWN: (motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL, motor.MotorArmPosition.RELEASED), motor.MotorArmState(motor.MotorArmAngle.VERTICAL, motor.MotorArmPosition.RELEASED)),
        cube.FaceID.RIGHT: (motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL),)})))

    #-----------------------------
    # One Side Arm holds Cube -> undefined behaviour

    move_checker.deny_motor_map(motor.RuleMotorMap({
        cube.FaceID.LEFT: (motor.MotorArmState(motor.MotorArmAngle.VERTICAL), motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL)),
        cube.FaceID.DOWN: (motor.MotorArmState(motor.MotorArmAngle.VERTICAL, motor.MotorArmPosition.RELEASED), motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL, motor.MotorArmPosition.RELEASED)),
        cube.FaceID.RIGHT: (motor.MotorArmState(motor.MotorArmAngle.VERTICAL, motor.MotorArmPosition.RELEASED), motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL, motor.MotorArmPosition.RELEASED))}))


    move_checker.deny_motor_map(motor.RuleMotorMap({
        cube.FaceID.LEFT: (motor.MotorArmState(motor.MotorArmAngle.VERTICAL, motor.MotorArmPosition.RELEASED), motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL,  motor.MotorArmPosition.RELEASED)),
        cube.FaceID.DOWN: (motor.MotorArmState(motor.MotorArmAngle.VERTICAL, motor.MotorArmPosition.RELEASED), motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL, motor.MotorArmPosition.RELEASED)),
        cube.FaceID.RIGHT: (motor.MotorArmState(motor.MotorArmAngle.VERTICAL), motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL))}))

    #------------------------------
    # No MotorArm holds Cube

    move_checker.deny_motor_map(motor.RuleMotorMap({
        cube.FaceID.LEFT: (motor.MotorArmState(motor.MotorArmAngle.VERTICAL, motor.MotorArmPosition.RELEASED), motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL,  motor.MotorArmPosition.RELEASED)),
        cube.FaceID.DOWN: (motor.MotorArmState(motor.MotorArmAngle.VERTICAL, motor.MotorArmPosition.RELEASED), motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL, motor.MotorArmPosition.RELEASED)),
        cube.FaceID.RIGHT: (motor.MotorArmState(motor.MotorArmAngle.VERTICAL, motor.MotorArmPosition.RELEASED), motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL,  motor.MotorArmPosition.RELEASED))}))

    #------------------------------
    # Side MotorArms with Down MotorArm overlapping

    move_checker.deny_motor_map(motor.RuleMotorMap({
        cube.FaceID.LEFT: (motor.MotorArmState(motor.MotorArmAngle.VERTICAL, motor.MotorArmPosition.RELEASED), motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL,  motor.MotorArmPosition.RELEASED), motor.MotorArmState(motor.MotorArmAngle.VERTICAL), motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL)),
        cube.FaceID.DOWN: (motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL),),
        cube.FaceID.RIGHT: (motor.MotorArmState(motor.MotorArmAngle.VERTICAL),)}))

    move_checker.deny_motor_map(motor.RuleMotorMap({
        cube.FaceID.LEFT: (motor.MotorArmState(motor.MotorArmAngle.VERTICAL),),
        cube.FaceID.DOWN: (motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL),),
        cube.FaceID.RIGHT: (motor.MotorArmState(motor.MotorArmAngle.VERTICAL, motor.MotorArmPosition.RELEASED), motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL,  motor.MotorArmPosition.RELEASED), motor.MotorArmState(motor.MotorArmAngle.VERTICAL), motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL))}))


    #-------------------------------
    # Only Allow Side MotorArm Release/Hold Combinations

    move_checker.deny_move(movement_rules.MovementDenyRule(motor.RuleMotorMap({
        cube.FaceID.LEFT: (motor.MotorArmState(motor.MotorArmAngle.VERTICAL, motor.MotorArmPosition.RELEASED), motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL,  motor.MotorArmPosition.RELEASED), motor.MotorArmState(motor.MotorArmAngle.VERTICAL), motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL)),
        cube.FaceID.DOWN: (motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL), motor.MotorArmState(motor.MotorArmAngle.VERTICAL)),
        cube.FaceID.RIGHT: (motor.MotorArmState(motor.MotorArmAngle.VERTICAL, motor.MotorArmPosition.RELEASED), motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL, motor.MotorArmPosition.RELEASED))}),
                                                           motor.RuleMotorMap({
        cube.FaceID.LEFT: (motor.MotorArmState(motor.MotorArmAngle.VERTICAL, motor.MotorArmPosition.RELEASED), motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL,  motor.MotorArmPosition.RELEASED), motor.MotorArmState(motor.MotorArmAngle.VERTICAL), motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL)),
        cube.FaceID.DOWN: (motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL, motor.MotorArmPosition.RELEASED), motor.MotorArmState(motor.MotorArmAngle.VERTICAL, motor.MotorArmPosition.RELEASED)),
        cube.FaceID.RIGHT: (motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL), motor.MotorArmState(motor.MotorArmAngle.VERTICAL))})))

    move_checker.deny_move(movement_rules.MovementDenyRule(motor.RuleMotorMap({
        cube.FaceID.LEFT: (motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL, motor.MotorArmPosition.RELEASED), motor.MotorArmState(motor.MotorArmAngle.VERTICAL, motor.MotorArmPosition.RELEASED)),
        cube.FaceID.DOWN: (motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL), motor.MotorArmState(motor.MotorArmAngle.VERTICAL)),
        cube.FaceID.RIGHT: (motor.MotorArmState(motor.MotorArmAngle.VERTICAL, motor.MotorArmPosition.RELEASED), motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL,  motor.MotorArmPosition.RELEASED), motor.MotorArmState(motor.MotorArmAngle.VERTICAL), motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL))}),
                                                           motor.RuleMotorMap({
        cube.FaceID.LEFT: (motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL), motor.MotorArmState(motor.MotorArmAngle.VERTICAL)),
        cube.FaceID.DOWN: (motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL, motor.MotorArmPosition.RELEASED), motor.MotorArmState(motor.MotorArmAngle.VERTICAL, motor.MotorArmPosition.RELEASED)),
        cube.FaceID.RIGHT: (motor.MotorArmState(motor.MotorArmAngle.VERTICAL, motor.MotorArmPosition.RELEASED), motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL,  motor.MotorArmPosition.RELEASED), motor.MotorArmState(motor.MotorArmAngle.VERTICAL), motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL))})))



    generator = GraphGenerator(start_motor_map, move_checker, rotation_turn_factory)
    g = generator.generate_graph()

    nx.write_gpickle(g, os.path.join(os.path.abspath(os.path.curdir), "graph.bin"))
    print("Successfully Saved Graph!!")
    nx.draw(g, with_labels=True, font_size=5)
    plt.show()