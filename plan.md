1. Manual trigger or repo changes?

2. Build python container to install requirements - stash container

3. unstash container from 2 - ````make test```` for local test

4. integration-test: ````docker-compose```` um integration-test python-container erweitern

    a) health Check abfragen\
    b) requests auf einzelne ports
    c) ausführen einzelner Services: nutzer hinzufügen..?

5. if passed: print "publish to docker-hub"



1. repo change triggers pipeline

2. run health check as unit test

3. deploy to ecs

4. run integration test that calls endpoints and verifies output

5.  if succesful:
        write out commit-hash into envvar
    else:
        checkout commit in envvar and rerun deployment


