test-cov: ## run tests with coverage
	@pytest tests --junitxml=`pwd`/~build/pytest.xml -vv \
        --cov-report=xml:`pwd`/~build/coverage.xml --cov-report=html --cov-report=term \
        --cov-config=tests/.coveragerc \
        --cov=ktcalendars || true
	@if [ "${BROWSERCMD}" != "" ]; then \
    	${BROWSERCMD} `pwd`/~build/coverage/index.html ; \
    fi