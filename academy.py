from app import create_app, db
from app.models import User, PermissionGroups, Academy, Lessons, Student, TrainedIn, LengthOfClass, TypeOfClass, DaysDone, Step, StepMarks, Classes121, Class121, StepExpectedTracker, StepExpectedProgress, StepActualProgress, StepActualTracker, Studentonclass, Studentonclass2, CustomInsert


app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db, 
        'User': User, 
        'PermissionGroups': PermissionGroups, 
        'Academy': Academy, 
        'Lessons': Lessons, 
        'TrainedIn': TrainedIn,
        'Student': Student,
        'LengthOfClass': LengthOfClass, 
        'TypeOfClass': TypeOfClass, 
        'DaysDone': DaysDone, 
        'Step': Step, 
        'StepMarks': StepMarks, 
        'Classes121': Classes121, 
        'Class121': Class121,
        'StepExpectedTracker': StepExpectedTracker, 
        'StepExpectedProgress': StepExpectedProgress, 
        'StepActualProgress': StepActualProgress, 
        'StepActualTracker': StepActualTracker,
        'Studentonclass': Studentonclass, 
        'Studentonclass2': Studentonclass2, 
        'CustomInsert': CustomInsert}


if __name__ == '__main__':
    app.run()