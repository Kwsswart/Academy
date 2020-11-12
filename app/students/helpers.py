from app.models import Academy, Lessons

def get_name(name, academy, types, companyname):
    ''' Helper function to create 121 names '''

    steps = ['121-Business English', '121-General English']

    if types in steps:

        new_name = 'S121 - '
        if types == '121-Business English':
            new_name = new_name + 'B - '

        academy = Academy.query.filter_by(name=academy).first()
        lessons = Lessons.query.filter_by(academy_id=academy.id).filter(Lessons.name.like(new_name + '%')).count()

        name2 = new_name + str(lessons + 1)
        
        name2 = name2 + ' - ' + name
        lesson = Lessons.query.filter_by(name=name2).first()
        if lesson:
            name2 = name
        return name2

    elif types == '121-Exam Class':

        new_name = 'E121 - '
        
        academy = Academy.query.filter_by(name=academy).first()
        lessons = Lessons.query.filter_by(academy_id=academy.id).filter(Lessons.name.like(new_name + '%')).count()

        name2 = new_name + str(lessons + 1)
        
        name2 = name2 + ' - ' + name
        lesson = Lessons.query.filter_by(name=name2).first()
        if lesson:
            name2 = name
        return name2  

    elif types == '121-Children':

        new_name = 'K121 - '
        
        academy = Academy.query.filter_by(name=academy).first()
        lessons = Lessons.query.filter_by(academy_id=academy.id).filter(Lessons.name.like(new_name + '%')).count()

        name2 = new_name + str(lessons + 1)
        
        name2 = name2 + ' - ' + name
        lesson = Lessons.query.filter_by(name=name2).first()
        if lesson:
            name2 = name
        return name2  

    elif types == 'In-Company-121':

        new_name = 'IC121 - ' + companyname + ' - '
        
        academy = Academy.query.filter_by(name=academy).first()
        lessons = Lessons.query.filter_by(academy_id=academy.id).filter(Lessons.name.like(new_name + '%')).count()

        name2 = new_name + str(lessons + 1)
        
        name2 = name2 + ' - ' + name
        lesson = Lessons.query.filter_by(name=name2).first()
        if lesson:
            name2 = name
        return name2  

