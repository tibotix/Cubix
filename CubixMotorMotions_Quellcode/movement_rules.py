import motor
import cube

class ForbiddenMovementException(Exception):
    pass




class MovementDenyRule():
    def __init__(self, start_rule_motor_map, end_rule_motor_map):
        self.start_rule_motor_map = start_rule_motor_map
        self.end_rule_motor_map = end_rule_motor_map

    def is_forbidden_move(self, start_move_motor_map, end_move_motor_map):
        # check start_move <-> end_move
        return bool((self.start_rule_motor_map.contains_move_motor_map(start_move_motor_map) and self.end_rule_motor_map.contains_move_motor_map(end_move_motor_map)) or (self.end_rule_motor_map.contains_move_motor_map(start_move_motor_map) and self.start_rule_motor_map.contains_move_motor_map(end_move_motor_map)))
