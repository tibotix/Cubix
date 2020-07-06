import enum
import cube
import copy
import itertools

class MotorMovementAction(enum.Enum):
    ROTATE = 0
    RELEASE = 1
    HOLD = 2


class MotorArmPosition(enum.Enum):
    HOLD = 0
    RELEASED = 1

    def is_hold(self):
        return self==MotorArmPosition.HOLD

    def is_released(self):
        return self==MotorArmPosition.RELEASED

class MotorArmAngle(enum.Enum):
    HORIZONTAL = 0
    VERTICAL = 1
    
    def rotate(self):
        if(self.is_horizontal()):
            self = MotorArmAngle.VERTICAL
        else:
            self = MotorArmAngle.HORIZONTAL

    def is_horizontal(self):
        return self==MotorArmAngle.HORIZONTAL

    def is_vertical(self):
        return self==MotorArmAngle.VERTICAL

class MotorArmState(): # Datenstruktur
    def __init__(self, motor_arm_angle, motor_arm_position=MotorArmPosition.HOLD):
        self.angle = motor_arm_angle
        self.position = motor_arm_position

    @property
    def all_angle_combinations(self):
        for angle in MotorArmAngle:
            if(angle!=self.angle):
                yield MotorArmState(angle, self.position)

    @property
    def all_position_combinations(self):
        for position in MotorArmPosition:
            if(position!=self.position):
                yield MotorArmState(self.angle, position)

    @property
    def all_states(self): #TODO: Refactor
        return list(self.all_angle_combinations)+list(self.all_position_combinations)

    def __hash__(self):
        return hash((self.angle, self.position))

    def __eq__(self, value):
        return hash(value)==hash(self)

    def __str__(self):
        return "[MotorArmState] Angle: {0}, Position: {1}".format(str(self.angle.name), str(self.position.name))



class AbstractMotorMap(dict):
    def __setitem__(self, key, value):
        if(not isinstance(key, cube.FaceID)):
            raise ValueError('Key must be from type {0}, but got type {1}.'.format(str(type(cube.FaceID)), str(type(key))))
        if(not isinstance(value, self.motor_arm_state_class)):
            raise ValueError('Value must be from type {0}, but got type {1}.'.format(str(type(self.motor_arm_state_class)), str(type(value))))
        return super().__setitem__(key, value)

    def __getitem__(self, key):
        if(key not in self):
            return None
        return super().__getitem__(key)

    @property
    def all_maps(self):
        for i in range(len(self)):
            for motor_arm_comb in itertools.combinations(self.items(), r=i):
                #                   = ((face_id, motor_arm_state), ..., i)
                for new_motor_state_combination in itertools.chain(itertools.product(*[[(face_id, nms) for nms in motor_arm_state.all_angle_combinations] for face_id, motor_arm_state in motor_arm_comb]), itertools.product(*[[(face_id, nms) for nms in motor_arm_state.all_position_combinations] for face_id, motor_arm_state in motor_arm_comb])):
                    #                               = ((face_id, new_motor_state_1) , ..., i
                    m = copy.deepcopy(self)
                    m.update({face_id: new_motor_state for face_id, new_motor_state in new_motor_state_combination})
                    yield m

    def __iter__(self):
        return super().__iter__()

    def __contains__(self, key):
        return super().__contains__(key)

    def __hash__(self):
        return hash(frozenset(self.items()))

    def __str__(self):
        return '|'.join(["[FaceID] {0} {1}".format(str(f.name), str(i)) for f, i in self.items()])

    def __eq__(self, value):
        return hash(value)==hash(self)

class MoveMotorMap(AbstractMotorMap):
    motor_arm_state_class = MotorArmState


class RuleMotorMap(AbstractMotorMap):
    motor_arm_state_class = tuple

    def contains_move_motor_map(self, move_motor_map):
        for face_id in self:
            if(face_id not in move_motor_map or move_motor_map[face_id] not in self[face_id]):
                return False
        return True