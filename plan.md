1. Manual trigger or repo changes?

2. Build python container to install requirements - stash container

3. unstash container from 2 - ````make test```` for local test

4. integration-test: ````docker-compose```` um integration-test python-container erweitern

    a) health Check abfragen\
    b) requests auf einzelne ports
    c) ausführen einzelner Services: nutzer hinzufügen..?

5. if passed: print "publish to docker-hub"
