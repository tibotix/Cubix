import enum


class FaceRelation(enum.Enum):
    UP = 'U'
    DOWN = 'D'
    BACK = 'B'
    FRONT = 'F'
    LEFT = 'L'
    RIGHT = 'R'


class FaceID(enum.Enum):
    UP = 'U'
    DOWN = 'D'
    BACK = 'B'
    FRONT = 'F'
    LEFT = 'L'
    RIGHT = 'R'

    @classmethod
    def y_line(cls):
        return [cls.UP, cls.FRONT, cls.DOWN, cls.BACK]

    @classmethod
    def x_line(cls):
        return [cls.LEFT, cls.FRONT, cls.RIGHT, cls.BACK]

    @classmethod
    def cube(cls):
        return [cls.UP, cls.LEFT, cls.FRONT, cls.RIGHT, cls.BACK, cls.DOWN]

    def get_middle_line_neighboors(self):
        ml = FaceID.x_line()
        if(self in ml):
            return [ml[ml.index(self)-1]] + [self] + [ml[::-1][ml[::-1].index(self)-1]]
        return ml

    def get_relation_to(self, relation_point): #TODO: Make Own class
        cube = FaceID.cube()
        normal_cube = FaceID.cube()
        xl = FaceID.x_line()
        yl = FaceID.y_line()
        if(self in xl):
            rotated_x_line = xl[xl.index(self)-xl.index(FaceID.FRONT):] + xl[:xl.index(self)-xl.index(FaceID.FRONT)]
            cube[cube.index(FaceID.LEFT):cube.index(FaceID.BACK)+1] = rotated_x_line
        else:
            rotated_y_line = yl[yl.index(self)-yl.index(FaceID.FRONT):] + yl[:yl.index(self)-yl.index(FaceID.FRONT)]
            for face, new_face in zip(yl, rotated_y_line):
                cube[normal_cube.index(face)] = new_face

        rel_idx = cube.index(relation_point)
        return FaceRelation(normal_cube[rel_idx].value)

    def get_from_relation(self, face_relation): # REFACTOR: VERY VERY BAD RUNTIME EFFICIENCY
        for face_id in FaceID.cube():
            if(self.get_relation_to(face_id)==face_relation):
                return face_id



#test:
if(__name__=='__main__'):
    assert FaceID.FRONT.get_relation_to(FaceID.BACK) == FaceRelation.BACK
    assert FaceID.LEFT.get_relation_to(FaceID.RIGHT) == FaceRelation.BACK
    assert FaceID.UP.get_relation_to(FaceID.DOWN) == FaceRelation.BACK
    assert FaceID.LEFT.get_relation_to(FaceID.UP) == FaceRelation.UP
    assert FaceID.LEFT.get_relation_to(FaceID.DOWN) == FaceRelation.DOWN
    assert FaceID.LEFT.get_relation_to(FaceID.FRONT) == FaceRelation.RIGHT
    assert FaceID.LEFT.get_relation_to(FaceID.BACK) == FaceRelation.LEFT
    assert FaceID.DOWN.get_relation_to(FaceID.RIGHT) == FaceRelation.RIGHT
    assert FaceID.DOWN.get_relation_to(FaceID.BACK) == FaceRelation.DOWN
    assert FaceID.DOWN.get_relation_to(FaceID.FRONT) == FaceRelation.UP
    assert FaceID.BACK.get_relation_to(FaceID.LEFT) == FaceRelation.RIGHT
    assert FaceID.BACK.get_relation_to(FaceID.RIGHT) == FaceRelation.LEFT
    assert FaceID.UP.get_relation_to(FaceID.UP) == FaceRelation.FRONT

