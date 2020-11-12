from app.models import Academy, Lessons
from wtforms.validators import Optional

def get_name(name, days, time, types, academy):
    ''' Helper function to create class names '''

    step_options = ['Group General English', 'Group Business English']
    options_IC = [
            'In-Company General English',
            'In-Company Business English',
        ]

    if types in step_options:
        
        if 'Monday' in days and 'Wednesday' in days:

            name = 'SM'

            if 8 <= time.hour < 12: 
                name = name + "M - "
            elif 12 <= time.hour < 17:
                name = name + "A - "
            elif 17 <= time.hour < 22:
                name = name + "E - "
            academy = Academy.query.filter_by(name=academy).first()
            lessons = Lessons.query.filter_by(academy_id=academy.id).filter(Lessons.name.like(name + '%')).count()
            if lessons != 0:
                name2 = name + str(1)
            else:
                name2 = name + '1'
            
            lesson = Lessons.query.filter_by(academy_id=academy.id).filter_by(name=name2).first()
            if lesson:
                name2 = name
            return name2
        elif 'Tuesday' in days and 'Thursday' in days:

            name = 'ST'

            if 8 <= time.hour < 12: 
                name = name + "M - "
            elif 12 <= time.hour < 17:
                name = name + "A - "
            elif 17 <= time.hour < 22:
                name = name + "E - "
            academy = Academy.query.filter_by(name=academy).first()
            lessons = Lessons.query.filter_by(academy_id=academy.id).filter(Lessons.name.like(name + '%')).count()
            if lessons != 0:
                name2 = name + str(1)
            else:
                name2 = name + '1'
            
            lesson = Lessons.query.filter_by(academy_id=academy.id).filter_by(name=name2).first()
            if lesson:
                name2 = name
            return name2
        elif 'Friday' in days:

            name = 'SF'

            if 8 <= time.hour < 12: 
                name = name + "M - "
            elif 12 <= time.hour < 17:
                name = name + "A - "
            elif 17 <= time.hour < 22:
                name = name + "E - "
            academy = Academy.query.filter_by(name=academy).first()
            lessons = Lessons.query.filter_by(academy_id=academy.id).filter(Lessons.name.like(name + '%')).count()
            if lessons != 0:
                name2 = name + str(1)
            else:
                name2 = name + '1'
            
            lesson = Lessons.query.filter_by(academy_id=academy.id).filter_by(name=name2).first()
            if lesson:
                name2 = name
            return name2
        elif 'Saturday' in days:

            name = 'SS'

            if 8 <= time.hour < 12: 
                name = name + "M - "
            elif 12 <= time.hour < 17:
                name = name + "A - "
            elif 17 <= time.hour < 22:
                name = name + "E - "
            academy = Academy.query.filter_by(name=academy).first()
            lessons = Lessons.query.filter_by(academy_id=academy.id).filter(Lessons.name.like(name + '%')).count()
            
            if lessons != 0:
                name2 = name + str(1)
            else:
                name2 = name + '1'
            
            lesson = Lessons.query.filter_by(academy_id=academy.id).filter_by(name=name2).first()
            print(lesson) # problem is here 
            if lesson:
                name2 = name
                print(name2)
            return name2
        else:
            return None

    elif types == 'Group Exam Class':
        if 'Monday' in days and 'Wednesday' in days:

            name = 'EM'

            if 8 <= time.hour < 12: 
                name = name + "M - "
            elif 12 <= time.hour < 17:
                name = name + "A - "
            elif 17 <= time.hour < 22:
                name = name + "E - "
            academy = Academy.query.filter_by(name=academy).first()
            lessons = Lessons.query.filter_by(academy_id=academy.id).filter(Lessons.name.like(name + '%')).count()
            if lessons != 0:
                name2 = name + str(1)
            else:
                name2 = name + '1'
            
            lesson = Lessons.query.filter_by(academy_id=academy.id).filter_by(name=name2).first()
            if lesson:
                name2 = name
            return name2
        elif 'Tuesday' in days and 'Thursday' in days:

            name = 'ET'

            if 8 <= time.hour < 12: 
                name = name + "M - "
            elif 12 <= time.hour < 17:
                name = name + "A - "
            elif 17 <= time.hour < 22:
                name = name + "E - "
            academy = Academy.query.filter_by(name=academy).first()
            lessons = Lessons.query.filter_by(academy_id=academy.id).filter(Lessons.name.like(name + '%')).count()
            if lessons != 0:
                name2 = name + str(1)
            else:
                name2 = name + '1'
            
            lesson = Lessons.query.filter_by(academy_id=academy.id).filter_by(name=name2).first()
            if lesson:
                name2 = name
            return name2
        elif 'Friday' in days:

            name = 'EF'

            if 8 <= time.hour < 12: 
                name = name + "M - "
            elif 12 <= time.hour < 17:
                name = name + "A - "
            elif 17 <= time.hour < 22:
                name = name + "E - "
            academy = Academy.query.filter_by(name=academy).first()
            lessons = Lessons.query.filter_by(academy_id=academy.id).filter(Lessons.name.like(name + '%')).count()
            if lessons != 0:
                name2 = name + str(1)
            else:
                name2 = name + '1'
            
            lesson = Lessons.query.filter_by(academy_id=academy.id).filter_by(name=name2).first()
            if lesson:
                name2 = name
            return name2
        elif 'Saturday' in days:

            name = 'ES'

            if 8 <= time.hour < 12: 
                name = name + "M - "
            elif 12 <= time.hour < 17:
                name = name + "A - "
            elif 17 <= time.hour < 22:
                name = name + "E - "
            academy = Academy.query.filter_by(name=academy).first()
            lessons = Lessons.query.filter_by(academy_id=academy.id).filter(Lessons.name.like(name + '%')).count()
            if lessons != 0:
                name2 = name + str(1)
            else:
                name2 = name + '1'
            
            lesson = Lessons.query.filter_by(academy_id=academy.id).filter_by(name=name2).first()
            if lesson:
                name2 = name
            return name2
        else:
            return None

    elif types == 'Group Children':
        if 'Monday' in days and 'Wednesday' in days:

            name = 'KM'

            if 8 <= time.hour < 12: 
                name = name + "M - "
            elif 12 <= time.hour < 17:
                name = name + "A - "
            elif 17 <= time.hour < 22:
                name = name + "E - "
            academy = Academy.query.filter_by(name=academy).first()
            lessons = Lessons.query.filter_by(academy_id=academy.id).filter(Lessons.name.like(name + '%')).count()
            if lessons != 0:
                name2 = name + str(1)
            else:
                name2 = name + '1'
            
            lesson = Lessons.query.filter_by(academy_id=academy.id).filter_by(name=name2).first()
            if lesson:
                name2 = name
            return name2
        elif 'Tuesday' in days and 'Thursday' in days:

            name = 'KT'

            if 8 <= time.hour < 12: 
                name = name + "M - "
            elif 12 <= time.hour < 17:
                name = name + "A - "
            elif 17 <= time.hour < 22:
                name = name + "E - "
            academy = Academy.query.filter_by(name=academy).first()
            lessons = Lessons.query.filter_by(academy_id=academy.id).filter(Lessons.name.like(name + '%')).count()
            if lessons != 0:
                name2 = name + str(1)
            else:
                name2 = name + '1'
            
            lesson = Lessons.query.filter_by(academy_id=academy.id).filter_by(name=name2).first()
            if lesson:
                name2 = name
            return name2
        elif 'Friday' in days:

            name = 'KF'

            if 8 <= time.hour < 12: 
                name = name + "M - "
            elif 12 <= time.hour < 17:
                name = name + "A - "
            elif 17 <= time.hour < 22:
                name = name + "E - "
            academy = Academy.query.filter_by(name=academy).first()
            lessons = Lessons.query.filter_by(academy_id=academy.id).filter(Lessons.name.like(name + '%')).count()
            if lessons != 0:
                name2 = name + str(1)
            else:
                name2 = name + '1'
            
            lesson = Lessons.query.filter_by(academy_id=academy.id).filter_by(name=name2).first()
            if lesson:
                name2 = name
            return name2
        elif 'Saturday' in days:

            name = 'KS'

            if 8 <= time.hour < 12: 
                name = name + "M - "
            elif 12 <= time.hour < 17:
                name = name + "A - "
            elif 17 <= time.hour < 22:
                name = name + "E - "
            academy = Academy.query.filter_by(name=academy).first()
            lessons = Lessons.query.filter_by(academy_id=academy.id).filter(Lessons.name.like(name + '%')).count()
            if lessons != 0:
                name2 = name + str(1)
            else:
                name2 = name + '1'
            
            lesson = Lessons.query.filter_by(academy_id=academy.id).filter_by(name=name2).first()
            if lesson:
                name2 = name
            return name2
        else:
            return None
    
    elif types == 'Group Intensive':

        name = 'INT - '
        if 8 <= time.hour < 12: 
            name = name + "M - "
        elif 12 <= time.hour < 17:
            name = name + "A - "
        elif 17 <= time.hour < 22:
            name = name + "E - "
        academy = Academy.query.filter_by(name=academy).first()
        lessons = Lessons.query.filter_by(academy_id=academy.id).filter(Lessons.name.like(name + '%')).count()
        if lessons != 0:
            name2 = name + str(1)
        else:
            name2 = name + '1'
            
        lesson = Lessons.query.filter_by(academy_id=academy.id).filter_by(name=name2).first()
        if lesson:
            name2 = name
        return name2
    
    elif types is options_IC:

        new_name = 'IC - ' + name 
        if 8 <= time.hour < 12: 
            new_name = new_name + "M - "
        elif 12 <= time.hour < 17:
            new_name = new_name + "A - "
        elif 17 <= time.hour < 22:
            new_name = new_name + "E - "
        academy = Academy.query.filter_by(name=academy).first()
        lessons = Lessons.query.filter_by(academy_id=academy.id).filter(Lessons.name.like(name + '%')).count()
        if lessons != 0:
            name2 = name + str(1)
        else:
            name2 = name + '1'
         
        lesson = Lessons.query.filter_by(academy_id=academy.id).filter_by(name=name2).first()
        if lesson:
            name2 = name
        return name2


class OptionalIf(Optional):
    # a validator which makes a field optional if
    # another field has a desired value

    def __init__(self, other_field_name, *args, **kwargs):
        self.other_field_name = other_field_name
        super(OptionalIf, self).__init__(*args, **kwargs)

    def __call__(self, form, field):
        other_field = form._fields.get(self.other_field_name)
        if other_field is None:
            raise Exception('no field named "%s" in form' % self.other_field_name)
        if other_field.data == 'No':
            super(OptionalIf, self).__call__(form, field)
