import sys
import os
import csv
from app.models import LengthOfClass, Step, StepExpectedTracker, StepExpectedProgress
from app import db


def importer(filename, time, step):
     

    with open(filename, "r") as toImport:
        #reader and writer
        reader = csv.DictReader(toImport)
        writer = csv.writer(toImport)
        
        length = time
        steps = step
        length = LengthOfClass.query.filter_by(name=length).first()
        step = Step.query.filter_by(name=steps).first()
        step_expected_tracker = StepExpectedTracker(length_of_class=length.id, step_id=step.id)
        db.session.add(step_expected_tracker)
        db.session.commit()
        
        for row in reader:
            # sort names into list
            # insert into db
           
            new = StepExpectedProgress(
                class_number=row['HOUR'], 
                lesson_number=row['LESSON NUMBER'], 
                last_page=row['NEW WORK TO'],
                last_word=row['LAST WORD'],
                exercises=row['EXERCISE'],
                step_expected_id=step_expected_tracker.id)

            db.session.add(new)
            db.session.commit()
            


def looper(path, time):

    filenames = os.listdir(path)

    for f in filenames:
        s = os.path.splitext(f)[0]
        importer('app/csv_files/1_hour/' + f, time, s)

        print('imported {} for step {} time {}'.format(f, s, time))