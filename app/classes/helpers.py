from app.models import Academy, Lessons

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
            name2 = name + str(lessons + 1)
            
            lesson = Lessons.query.filter_by(name=name2).first()
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
            name2 = name + str(lessons + 1)
            
            lesson = Lessons.query.filter_by(name=name2).first()
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
            name2 = name + str(lessons + 1)
            
            lesson = Lessons.query.filter_by(name=name2).first()
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
            name2 = name + str(lessons + 1)
            
            lesson = Lessons.query.filter_by(name=name2).first()
            if lesson:
                name2 = name
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
            name2 = name + str(lessons + 1)
            
            lesson = Lessons.query.filter_by(name=name2).first()
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
            name2 = name + str(lessons + 1)
            
            lesson = Lessons.query.filter_by(name=name2).first()
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
            name2 = name + str(lessons + 1)
            
            lesson = Lessons.query.filter_by(name=name2).first()
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
            name2 = name + str(lessons + 1)
            
            lesson = Lessons.query.filter_by(name=name2).first()
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
            name2 = name + str(lessons + 1)
            
            lesson = Lessons.query.filter_by(name=name2).first()
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
            name2 = name + str(lessons + 1)
            
            lesson = Lessons.query.filter_by(name=name2).first()
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
            name2 = name + str(lessons + 1)
            
            lesson = Lessons.query.filter_by(name=name2).first()
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
            name2 = name + str(lessons + 1)
            
            lesson = Lessons.query.filter_by(name=name2).first()
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
        name2 = name + str(lessons + 1)
            
        lesson = Lessons.query.filter_by(name=name2).first()
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
        name2 = name + str(lessons + 1)
            
        lesson = Lessons.query.filter_by(name=name2).first()
        if lesson:
            name2 = name
        return name2
