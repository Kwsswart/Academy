from app import create_app, db
from app.models import User, PermissionGroups, Academy, Lessons, Student, TrainedIn


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
        'Student': Student}


if __name__ == '__main__':
    app.run()