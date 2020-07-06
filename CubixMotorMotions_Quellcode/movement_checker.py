
import cube

class InvalidMoveException(Exception):
    pass


class MovementChecker():
    def __init__(self):
        self.movement_deny_rules = list()
        self.denied_motor_maps = list()

    def deny_move(self, deny_rule):
        self.movement_deny_rules.append(deny_rule)

    def deny_motor_map(self, rule_motor_map):
        self.denied_motor_maps.append(rule_motor_map)

    def is_allowed(self, motor_map, new_motor_map):
        return bool(self._check_motor_maps(new_motor_map) and self._check_movement_rules(motor_map, new_motor_map))

    def _check_motor_maps(self, new_motor_map):
        for denied_rule_motor_map in self.denied_motor_maps:
            if(denied_rule_motor_map.contains_move_motor_map(new_motor_map)):
                return False
        return True

    def _check_movement_rules(self, motor_map, new_motor_map):
        for rule in self.movement_deny_rules:
            if(rule.is_forbidden_move(motor_map, new_motor_map)):
                return False
        return True