Contributing

Thanks for contributing to Galactic Conflict! Here’s the quick guide:



Setup



Code to run

python GalacticConflict\\galacticconflict.py



Code for tests

python GalacticConflict\\galacticconflict.py --run-tests test/suites/suite1.json



Rules

Follow PEP‑8.



Every new mechanic must be reversible via Board.undo\_move().



Rules of the game can be found in doc folder.

Every new piece must implement:

update\_valid\_moves()

before\_move()

undo\_before\_move()



Tests

Add a JSON position + expected move for:



PROMOTION



DEMOTION



MERGE



DECOUPLE\_BM



DECOUPLE\_IN



COUPLE



BOARDING



Pull Requests

Keep changes focused.



Include tests.



Update documentation.

