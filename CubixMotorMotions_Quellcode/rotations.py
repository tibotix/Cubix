import motor
import cube




class CubeRotationTurnGroup():
    def __init__(self, face_id_group_members, cube_rotation_turn):
        self.face_id_group_members = face_id_group_members
        self.cube_rotation_turn = cube_rotation_turn

    def contains_face_ids(self, face_ids):
        for face_id in self.face_id_group_members:
            if(face_id not in face_ids):
                return False
        return True

    def __str__(self):
        return "[FaceIDs] {0} ; [CubeRotationTurn] {1}".format(str(self.face_id_group_members), str(self.cube_rotation_turn))


class RotationTurn():
    pass

class NoRotationTurn(RotationTurn):
    pass

class CubeRotationTurn(RotationTurn):
    def __init__(self, cube_rotation_turn_mapping):
        self.cube_rotation_turn_mapping = cube_rotation_turn_mapping

    def __hash__(self):
        return hash(frozenset([frozenset(i.items()) for i in self.cube_rotation_turn_mapping]))

    def __eq__(self, value):
        return hash(value)==hash(self)

    def __str__(self):
        return "[CubeRotation] {0}".format(str(self.cube_rotation_turn_mapping))

    def is_specific_cube_turn_in_mapping(self, specific_cube_turn):
        return specific_cube_turn in self.cube_rotation_turn_mapping

    @classmethod
    def y_axis_cube_turn(cls):
        return cls(({
            cube.FaceID.FRONT: cube.FaceID.UP,
            cube.FaceID.UP: cube.FaceID.BACK,
            cube.FaceID.BACK: cube.FaceID.DOWN,
            cube.FaceID.DOWN: cube.FaceID.FRONT}, {
            cube.FaceID.FRONT: cube.FaceID.DOWN,
            cube.FaceID.DOWN: cube.FaceID.BACK,
            cube.FaceID.BACK: cube.FaceID.UP,
            cube.FaceID.UP: cube.FaceID.FRONT}))

    @classmethod
    def x_axis_cube_turn(cls):
        return cls(({
            cube.FaceID.FRONT: cube.FaceID.RIGHT,
            cube.FaceID.RIGHT: cube.FaceID.BACK,
            cube.FaceID.BACK: cube.FaceID.LEFT,
            cube.FaceID.LEFT: cube.FaceID.FRONT}, {
            cube.FaceID.FRONT: cube.FaceID.LEFT,
            cube.FaceID.LEFT: cube.FaceID.BACK,
            cube.FaceID.BACK: cube.FaceID.RIGHT,
            cube.FaceID.RIGHT: cube.FaceID.FRONT}))



class FaceRotationTurn(RotationTurn):
    def __init__(self, face_turns):
        self.face_turns = face_turns

    def __hash__(self):
        return hash(frozenset(self.face_turns))

    def __eq__(self, value):
        return hash(value)==hash(self)

    def __str__(self):
        return "[FaceRotation] {0}".format(str(self.face_turns))


class MotorArmMovementAnalyzeResult():
    def __init__(self, always_released, always_hold, face_turns):
        self.always_released = always_released
        self.always_hold = always_hold
        self.face_turns = face_turns

        
class MotorArmStateMovementAnalyzer():
    def __init__(self, start_motor_map, end_motor_map):
        self.start_motor_map = start_motor_map
        self.end_motor_map = end_motor_map

    def analyze(self):
        self.always_released = list()
        self.always_hold = list()
        self.face_turns = list()
        self._analyze_angles()
        self._analyze_face_turns()
        return MotorArmMovementAnalyzeResult(self.always_released, self.always_hold, self.face_turns)
        
    def _analyze_angles(self):
        for face_id, motor_state in self.start_motor_map.items():
            if(face_id in self.end_motor_map and (motor_state.position==motor.MotorArmPosition.HOLD and self.end_motor_map[face_id].position==motor.MotorArmPosition.HOLD)):
                self.always_hold.append(face_id)
            if(face_id in self.end_motor_map and (motor_state.position==motor.MotorArmPosition.RELEASED and self.end_motor_map[face_id].position==motor.MotorArmPosition.RELEASED)):
                self.always_released.append(face_id)

    def _analyze_face_turns(self):
        for face_id in self.always_hold:
            if(self.start_motor_map[face_id].angle!=self.end_motor_map[face_id].angle):
                self.face_turns.append(face_id)



class RotationTurnFactory():
    def __init__(self, cube_rotation_turn_groups):
        self.cube_rotation_turn_groups = cube_rotation_turn_groups

    def get_rotatation_turn(self, start_motor_map, end_motor_map):
        analyze_result = MotorArmStateMovementAnalyzer(start_motor_map, end_motor_map).analyze()
        for cube_rotation_turn_group in self.cube_rotation_turn_groups:
            if(cube_rotation_turn_group.contains_face_ids(analyze_result.face_turns) and self._all_other_cube_rotation_turn_groups_released(cube_rotation_turn_group, analyze_result)):
                return cube_rotation_turn_group.cube_rotation_turn
        return (FaceRotationTurn(analyze_result.face_turns) if(analyze_result.face_turns) else NoRotationTurn())

    def _all_other_cube_rotation_turn_groups_released(self, cube_rotation_turn_group_to_check, analyze_result):
        for cube_rotation_turn_group in self.cube_rotation_turn_groups:
            if(cube_rotation_turn_group!=cube_rotation_turn_group_to_check):
                if(not cube_rotation_turn_group.contains_face_ids(analyze_result.always_released)):
                    return False
        return True


if(__name__=="__main__"):

    side_arm_cube_rotation_turn_group = CubeRotationTurnGroup((cube.FaceID.LEFT, cube.FaceID.RIGHT), CubeRotationTurn.y_axis_cube_turn())
    down_arm_cube_rotation_turn_group = CubeRotationTurnGroup((cube.FaceID.DOWN,), CubeRotationTurn.x_axis_cube_turn())
    rotation_turn_factory = RotationTurnFactory([side_arm_cube_rotation_turn_group, down_arm_cube_rotation_turn_group])

    start_motor_map = motor.MoveMotorMap({cube.FaceID.LEFT: motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL), cube.FaceID.DOWN: motor.MotorArmState(motor.MotorArmAngle.VERTICAL), cube.FaceID.RIGHT: motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL)})
    end_motor_map = motor.MoveMotorMap({cube.FaceID.LEFT: motor.MotorArmState(motor.MotorArmAngle.VERTICAL), cube.FaceID.DOWN: motor.MotorArmState(motor.MotorArmAngle.VERTICAL), cube.FaceID.RIGHT: motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL)})
    assert MotorArmStateMovementAnalyzer(start_motor_map, end_motor_map).analyze().face_turns == [cube.FaceID.LEFT]
    print(str(rotation_turn_factory.get_rotatation_turn(start_motor_map, end_motor_map)))

    start_motor_map = motor.MoveMotorMap({cube.FaceID.LEFT: motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL), cube.FaceID.DOWN: motor.MotorArmState(motor.MotorArmAngle.VERTICAL), cube.FaceID.RIGHT: motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL)})
    end_motor_map = motor.MoveMotorMap({cube.FaceID.LEFT: motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL), cube.FaceID.DOWN: motor.MotorArmState(motor.MotorArmAngle.VERTICAL, motor.MotorArmPosition.RELEASED), cube.FaceID.RIGHT: motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL)})
    assert MotorArmStateMovementAnalyzer(start_motor_map, end_motor_map).analyze().face_turns == []
    print(str(rotation_turn_factory.get_rotatation_turn(start_motor_map, end_motor_map)))

    start_motor_map = motor.MoveMotorMap({cube.FaceID.LEFT: motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL), cube.FaceID.DOWN: motor.MotorArmState(motor.MotorArmAngle.VERTICAL), cube.FaceID.RIGHT: motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL)})
    end_motor_map = motor.MoveMotorMap({cube.FaceID.LEFT: motor.MotorArmState(motor.MotorArmAngle.VERTICAL), cube.FaceID.DOWN: motor.MotorArmState(motor.MotorArmAngle.VERTICAL), cube.FaceID.RIGHT: motor.MotorArmState(motor.MotorArmAngle.VERTICAL)})
    assert MotorArmStateMovementAnalyzer(start_motor_map, end_motor_map).analyze().face_turns == [cube.FaceID.LEFT, cube.FaceID.RIGHT]
    print(str(rotation_turn_factory.get_rotatation_turn(start_motor_map, end_motor_map)))

    start_motor_map = motor.MoveMotorMap({cube.FaceID.LEFT: motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL), cube.FaceID.DOWN: motor.MotorArmState(motor.MotorArmAngle.VERTICAL), cube.FaceID.RIGHT: motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL)})
    end_motor_map = motor.MoveMotorMap({cube.FaceID.LEFT: motor.MotorArmState(motor.MotorArmAngle.VERTICAL), cube.FaceID.DOWN: motor.MotorArmState(motor.MotorArmAngle.VERTICAL), cube.FaceID.RIGHT: motor.MotorArmState(motor.MotorArmAngle.VERTICAL, motor.MotorArmPosition.RELEASED)})
    assert MotorArmStateMovementAnalyzer(start_motor_map, end_motor_map).analyze().face_turns == [cube.FaceID.LEFT]
    print(str(rotation_turn_factory.get_rotatation_turn(start_motor_map, end_motor_map)))

    start_motor_map = motor.MoveMotorMap({cube.FaceID.LEFT: motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL), cube.FaceID.DOWN: motor.MotorArmState(motor.MotorArmAngle.VERTICAL, motor.MotorArmPosition.RELEASED), cube.FaceID.RIGHT: motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL)})
    end_motor_map = motor.MoveMotorMap({cube.FaceID.LEFT: motor.MotorArmState(motor.MotorArmAngle.VERTICAL), cube.FaceID.DOWN: motor.MotorArmState(motor.MotorArmAngle.VERTICAL, motor.MotorArmPosition.RELEASED), cube.FaceID.RIGHT: motor.MotorArmState(motor.MotorArmAngle.VERTICAL)})
    assert MotorArmStateMovementAnalyzer(start_motor_map, end_motor_map).analyze().face_turns == [cube.FaceID.LEFT, cube.FaceID.RIGHT] #cube turn
    print(str(rotation_turn_factory.get_rotatation_turn(start_motor_map, end_motor_map)))

    start_motor_map = motor.MoveMotorMap({cube.FaceID.LEFT: motor.MotorArmState(motor.MotorArmAngle.VERTICAL, motor.MotorArmPosition.RELEASED), cube.FaceID.DOWN: motor.MotorArmState(motor.MotorArmAngle.VERTICAL), cube.FaceID.RIGHT: motor.MotorArmState(motor.MotorArmAngle.VERTICAL, motor.MotorArmPosition.RELEASED)})
    end_motor_map = motor.MoveMotorMap({cube.FaceID.LEFT: motor.MotorArmState(motor.MotorArmAngle.VERTICAL, motor.MotorArmPosition.RELEASED), cube.FaceID.DOWN: motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL), cube.FaceID.RIGHT: motor.MotorArmState(motor.MotorArmAngle.HORIZONTAL, motor.MotorArmPosition.RELEASED)})
    result = MotorArmStateMovementAnalyzer(start_motor_map, end_motor_map).analyze()
    print(str(rotation_turn_factory.get_rotatation_turn(start_motor_map, end_motor_map)))